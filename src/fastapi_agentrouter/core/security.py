"""Security and middleware dependencies for FastAPI AgentRouter."""

import hashlib
import hmac
import logging
import time
from collections import defaultdict
from typing import Annotated, Any, Callable, Optional

from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .settings import Settings, settings

logger = logging.getLogger(__name__)

# Security schemes
security = HTTPBearer(auto_error=False)


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, requests_per_minute: int = 60):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute per key
        """
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[float]] = defaultdict(list)

    def check_rate_limit(self, key: str) -> bool:
        """Check if request is within rate limit.

        Args:
            key: Unique identifier for rate limiting (e.g., user_id, IP)

        Returns:
            True if within limit, False otherwise
        """
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key] if req_time > minute_ago
        ]

        # Check limit
        if len(self.requests[key]) >= self.requests_per_minute:
            return False

        # Add current request
        self.requests[key].append(now)
        return True

    def reset(self, key: Optional[str] = None) -> None:
        """Reset rate limit tracking.

        Args:
            key: Optional key to reset. If None, resets all.
        """
        if key:
            self.requests.pop(key, None)
        else:
            self.requests.clear()


# Global rate limiter instance
rate_limiter = RateLimiter()


def check_rate_limit(
    request: Request,
    settings_dep: Annotated[Settings, Depends(lambda: settings)],
) -> None:
    """Dependency to check rate limits.

    Raises:
        HTTPException: If rate limit exceeded
    """
    if not getattr(settings_dep, "enable_rate_limiting", True):
        return

    # Use client IP as rate limit key
    client_ip = request.client.host if request.client else "unknown"

    # Check if custom rate limit key is provided in headers
    rate_limit_key = request.headers.get("X-Rate-Limit-Key", client_ip)

    if not rate_limiter.check_rate_limit(rate_limit_key):
        logger.warning(f"Rate limit exceeded for {rate_limit_key}")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"},
        )


def verify_signature(
    secret_key: str,
    signature_header: str,
    body: bytes,
    timestamp_tolerance: int = 300,
) -> bool:
    """Verify request signature (similar to Slack/GitHub webhooks).

    Args:
        secret_key: Secret key for HMAC
        signature_header: Signature from request header
        body: Request body bytes
        timestamp_tolerance: Maximum age of request in seconds

    Returns:
        True if signature is valid
    """
    try:
        # Parse signature header (format: "v0=timestamp,signature")
        parts = signature_header.split(",")
        if len(parts) != 2:
            return False

        timestamp_part, signature_part = parts
        if not timestamp_part.startswith("v0="):
            return False

        timestamp = int(timestamp_part[3:])

        # Check timestamp is within tolerance
        current_time = int(time.time())
        if abs(current_time - timestamp) > timestamp_tolerance:
            logger.warning("Request timestamp outside tolerance window")
            return False

        # Compute expected signature
        base_string = f"v0:{timestamp}:{body.decode('utf-8')}"
        expected_signature = hmac.new(
            secret_key.encode(), base_string.encode(), hashlib.sha256
        ).hexdigest()

        # Compare signatures
        return hmac.compare_digest(signature_part, f"v0={expected_signature}")

    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        return False


def create_platform_signature_verifier(platform: str) -> Callable:
    """Factory for platform-specific signature verification.

    Args:
        platform: Platform name (e.g., "slack", "github")

    Returns:
        Dependency function for signature verification
    """

    async def verify_platform_signature(
        request: Request,
        x_signature: Annotated[Optional[str], Header()] = None,
        settings_dep: Optional[Settings] = None,
    ) -> None:
        """Verify platform-specific signature."""
        # Check if signature verification is enabled
        if settings_dep is None:
            settings_dep = settings

        if not getattr(settings_dep, f"verify_{platform}_signature", True):
            return

        if not x_signature:
            raise HTTPException(
                status_code=401, detail=f"{platform} signature header missing"
            )

        # Get platform secret from settings
        secret = getattr(settings_dep, f"{platform}_signing_secret", None)
        if not secret:
            logger.warning(f"{platform} signing secret not configured")
            raise HTTPException(
                status_code=500, detail=f"{platform} signing secret not configured"
            )

        # Get request body
        body = await request.body()

        # Verify signature
        if not verify_signature(secret, x_signature, body):
            raise HTTPException(status_code=401, detail="Invalid signature")

    return verify_platform_signature


def check_api_key(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    settings_dep: Annotated[Settings, Depends(lambda: settings)],
) -> Optional[str]:
    """Verify API key from Authorization header.

    Returns:
        API key if valid, None if not required

    Raises:
        HTTPException: If API key is invalid
    """
    # Check if API key auth is enabled
    if not getattr(settings_dep, "require_api_key", False):
        return None

    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = credentials.credentials

    # Validate API key (in production, check against database or secure store)
    valid_api_keys = getattr(settings_dep, "valid_api_keys", [])
    if api_key not in valid_api_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return str(api_key)


def log_request(
    request: Request,
    settings_dep: Annotated[Settings, Depends(lambda: settings)],
) -> None:
    """Log incoming requests for audit purposes."""
    if not getattr(settings_dep, "enable_request_logging", True):
        return

    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )


def create_security_dependencies(platform: Optional[str] = None) -> list[Depends]:
    """Create a list of security dependencies for a router.

    Args:
        platform: Optional platform name for platform-specific checks

    Returns:
        List of dependencies to apply to router

    Example:
        router = APIRouter(
            dependencies=create_security_dependencies("slack")
        )
    """
    deps = [
        Depends(check_rate_limit),
        Depends(log_request),
    ]

    if platform:
        # Add platform-specific signature verification
        deps.append(Depends(create_platform_signature_verifier(platform)))

    return deps


class SecurityContext:
    """Context object containing security-related information."""

    def __init__(
        self,
        user_id: Optional[str] = None,
        api_key: Optional[str] = None,
        platform: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        """Initialize security context."""
        self.user_id = user_id
        self.api_key = api_key
        self.platform = platform
        self.request_id = request_id or self._generate_request_id()
        self.timestamp = time.time()

    @staticmethod
    def _generate_request_id() -> str:
        """Generate unique request ID."""
        import uuid

        return str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "user_id": self.user_id,
            "platform": self.platform,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
        }


def get_security_context(
    request: Request,
    api_key: Annotated[Optional[str], Depends(check_api_key)] = None,
) -> SecurityContext:
    """Get security context for the current request.

    Example:
        @app.post("/query")
        def query(
            context: Annotated[SecurityContext, Depends(get_security_context)],
            message: str,
        ):
            logger.info(f"Query from {context.user_id}: {message}")
    """
    # Extract user information from headers or auth
    user_id = request.headers.get("X-User-Id")

    # Determine platform from path
    platform = None
    if "/slack" in str(request.url):
        platform = "slack"
    elif "/discord" in str(request.url):
        platform = "discord"

    return SecurityContext(
        user_id=user_id,
        api_key=api_key,
        platform=platform,
    )
