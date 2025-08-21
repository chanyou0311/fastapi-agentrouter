# Changelog

## [0.6.2](https://github.com/chanyou0311/fastapi-agentrouter/compare/v0.6.1...v0.6.2) (2025-08-21)


### Bug Fixes

* **deps:** update docker/build-push-action action to v6 ([#93](https://github.com/chanyou0311/fastapi-agentrouter/issues/93)) ([d0598a0](https://github.com/chanyou0311/fastapi-agentrouter/commit/d0598a0567d20d87d5d44ad97b64c2deee9fef4e))
* **deps:** update ghcr.io/astral-sh/uv docker tag to v0.8.12 ([#91](https://github.com/chanyou0311/fastapi-agentrouter/issues/91)) ([8f10c47](https://github.com/chanyou0311/fastapi-agentrouter/commit/8f10c47cc4364e811b60af025c5a74b779c93b16))
* **deps:** update googleapis/release-please-action digest to c2a5a2b ([#94](https://github.com/chanyou0311/fastapi-agentrouter/issues/94)) ([940fd96](https://github.com/chanyou0311/fastapi-agentrouter/commit/940fd96d9a53fbdfacce526983b2dfd69989ff1a))
* **deps:** update python docker tag to v3.13.7 ([#92](https://github.com/chanyou0311/fastapi-agentrouter/issues/92)) ([cc1c528](https://github.com/chanyou0311/fastapi-agentrouter/commit/cc1c52883c7975e493736740e43cf49cfaff8a0a))

## [0.6.1](https://github.com/chanyou0311/fastapi-agentrouter/compare/v0.6.0...v0.6.1) (2025-08-19)


### Bug Fixes

* add semantic versioning tags to Docker image publishing ([#83](https://github.com/chanyou0311/fastapi-agentrouter/issues/83)) ([c9b6924](https://github.com/chanyou0311/fastapi-agentrouter/commit/c9b692461ae7bb754d015af4cf3bbe2645877776))
* **deps:** update docker/build-push-action digest to ca052bb ([#81](https://github.com/chanyou0311/fastapi-agentrouter/issues/81)) ([900a918](https://github.com/chanyou0311/fastapi-agentrouter/commit/900a9182203523fe7172372cd3629f38b021b0ec))
* **deps:** update docker/login-action digest to 184bdaa ([#82](https://github.com/chanyou0311/fastapi-agentrouter/issues/82)) ([68acc6f](https://github.com/chanyou0311/fastapi-agentrouter/commit/68acc6f4601112283e27c4d7f901a5f9b7d3f509))
* **deps:** update docker/metadata-action digest to c1e5197 ([#85](https://github.com/chanyou0311/fastapi-agentrouter/issues/85)) ([4ae2661](https://github.com/chanyou0311/fastapi-agentrouter/commit/4ae26619d44404fcf9ed30f4a14d6f18b52cba1f))
* **deps:** update docker/setup-buildx-action digest to e468171 ([#86](https://github.com/chanyou0311/fastapi-agentrouter/issues/86)) ([78224a9](https://github.com/chanyou0311/fastapi-agentrouter/commit/78224a9e27c1319bedd918d33207bcfa852e8e48))


### Documentation

* Remove outdated documentation files for installation, quickstart, and Slack integration; delete Japanese translations for core API, integrations, contributing, examples, and configuration; eliminate improvement suggestions document. ([#84](https://github.com/chanyou0311/fastapi-agentrouter/issues/84)) ([517ed51](https://github.com/chanyou0311/fastapi-agentrouter/commit/517ed510129104c3a9f3dec2812146fced2fadf7))
* update README.md to match current implementation ([#87](https://github.com/chanyou0311/fastapi-agentrouter/issues/87)) ([edc4d90](https://github.com/chanyou0311/fastapi-agentrouter/commit/edc4d9011d5362312f041731d08f7bb862eb5d00))

## [0.6.0](https://github.com/chanyou0311/fastapi-agentrouter/compare/v0.5.0...v0.6.0) (2025-08-19)


### Features

* add Docker support for FastAPI application ([#79](https://github.com/chanyou0311/fastapi-agentrouter/issues/79)) ([e4d0c9b](https://github.com/chanyou0311/fastapi-agentrouter/commit/e4d0c9bee1cc32d43574d0f8309c8865feb636f0))
* add main entry point for FastAPI application ([#78](https://github.com/chanyou0311/fastapi-agentrouter/issues/78)) ([7de58ab](https://github.com/chanyou0311/fastapi-agentrouter/commit/7de58abbafb60dd4582899e878a5fff839b8b692))


### Bug Fixes

* **deps:** update amannn/action-semantic-pull-request digest to 24e6f01 ([#76](https://github.com/chanyou0311/fastapi-agentrouter/issues/76)) ([f927c33](https://github.com/chanyou0311/fastapi-agentrouter/commit/f927c33c93d24aa4762517747db0a2d2311bd85a))

## [0.5.0](https://github.com/chanyou0311/fastapi-agentrouter/compare/v0.4.2...v0.5.0) (2025-08-16)


### Features

* add Vertex AI engine warmup to prevent ClientDisconnect errors ([#71](https://github.com/chanyou0311/fastapi-agentrouter/issues/71)) ([a55bed7](https://github.com/chanyou0311/fastapi-agentrouter/commit/a55bed777e1b15ae8ae8e78bd3f7576923545ed5))
* enable Slack bot to reply in threads ([#73](https://github.com/chanyou0311/fastapi-agentrouter/issues/73)) ([b73dacd](https://github.com/chanyou0311/fastapi-agentrouter/commit/b73dacd3988036ba71e801d75dac81a5fc7aa2fa))
* explicitly create and use sessions in Slack app_mention handler ([#72](https://github.com/chanyou0311/fastapi-agentrouter/issues/72)) ([8559dfb](https://github.com/chanyou0311/fastapi-agentrouter/commit/8559dfba6abdf7ce6187132e56e05b3c538229e7))
* export get_vertex_ai_agent_engine for easy Vertex AI integration ([#60](https://github.com/chanyou0311/fastapi-agentrouter/issues/60)) ([a3e31b1](https://github.com/chanyou0311/fastapi-agentrouter/commit/a3e31b1e61e43f663096add62af6955c0a8d39e3))
* implement thread-based session management for Slack integration ([#74](https://github.com/chanyou0311/fastapi-agentrouter/issues/74)) ([e109f0e](https://github.com/chanyou0311/fastapi-agentrouter/commit/e109f0e2b332de220f4e21b1d3191097816a8ef8))
* improve type hints for AgentProtocol and add examples gitignore ([#58](https://github.com/chanyou0311/fastapi-agentrouter/issues/58)) ([2f85664](https://github.com/chanyou0311/fastapi-agentrouter/commit/2f85664c5274b38f70ae75b9dcf1db7adc4f757e))


### Bug Fixes

* remove debug say() call in Slack app_mention handler ([#61](https://github.com/chanyou0311/fastapi-agentrouter/issues/61)) ([eff390e](https://github.com/chanyou0311/fastapi-agentrouter/commit/eff390e20953dcd54a7ed202d2d60ed573949490))


### Documentation

* add PR feedback handling guidelines to CLAUDE.md ([#68](https://github.com/chanyou0311/fastapi-agentrouter/issues/68)) ([6459de6](https://github.com/chanyou0311/fastapi-agentrouter/commit/6459de68ebc98fa415992f7f06f0f10844155e9c))

## [0.4.2](https://github.com/chanyou0311/fastapi-agentrouter/compare/v0.4.1...v0.4.2) (2025-08-14)


### Bug Fixes

* **deps:** pin actions/create-github-app-token action to d72941d ([#53](https://github.com/chanyou0311/fastapi-agentrouter/issues/53)) ([8764110](https://github.com/chanyou0311/fastapi-agentrouter/commit/8764110343a6ef721576a0a15f8aed1143b18588))
* **deps:** update actions/checkout digest to 08eba0b ([#38](https://github.com/chanyou0311/fastapi-agentrouter/issues/38)) ([496232a](https://github.com/chanyou0311/fastapi-agentrouter/commit/496232a99cea9f4d50fc292b9f5bec3c0039e82c))
* **deps:** update actions/create-github-app-token action to v2 ([#54](https://github.com/chanyou0311/fastapi-agentrouter/issues/54)) ([5af7a48](https://github.com/chanyou0311/fastapi-agentrouter/commit/5af7a4812e6a98fe95b2d24ecc1f2a0c9400d8ed))

## [0.4.1](https://github.com/chanyou0311/fastapi-agentrouter/compare/v0.4.0...v0.4.1) (2025-08-14)


### ⚠ BREAKING CHANGES

* Minimum Python version is now 3.10

### Bug Fixes

* add extra='ignore' to Slack and Settings model configs ([#43](https://github.com/chanyou0311/fastapi-agentrouter/issues/43)) ([25d08cb](https://github.com/chanyou0311/fastapi-agentrouter/commit/25d08cbe67980425961e568870b3f9e0c7011711))
* add GitHub App token retrieval to release workflow ([#52](https://github.com/chanyou0311/fastapi-agentrouter/issues/52)) ([4f8d073](https://github.com/chanyou0311/fastapi-agentrouter/commit/4f8d07377c62ca4dfeb935ecf7f4975ddda9b10c))
* **deps:** update actions/checkout action to v5 ([#39](https://github.com/chanyou0311/fastapi-agentrouter/issues/39)) ([1b82f33](https://github.com/chanyou0311/fastapi-agentrouter/commit/1b82f33e1240c2e9102be0c746888d1441c5609a))
* **deps:** update amannn/action-semantic-pull-request action to v6 ([#50](https://github.com/chanyou0311/fastapi-agentrouter/issues/50)) ([7c5bbbf](https://github.com/chanyou0311/fastapi-agentrouter/commit/7c5bbbf2e8427057094a20220c5c9b7faf793c0f))
* **deps:** update amannn/action-semantic-pull-request digest to e32d7e6 ([#49](https://github.com/chanyou0311/fastapi-agentrouter/issues/49)) ([cd0cbcb](https://github.com/chanyou0311/fastapi-agentrouter/commit/cd0cbcb5455a0850a7c9c52879d45f79570c9d70))
* **deps:** update astral-sh/setup-uv digest to d9e0f98 ([#46](https://github.com/chanyou0311/fastapi-agentrouter/issues/46)) ([56d2a3d](https://github.com/chanyou0311/fastapi-agentrouter/commit/56d2a3d9be410829692bea99b395ebed573d24e3))


### Miscellaneous Chores

* drop Python 3.9 support ([#40](https://github.com/chanyou0311/fastapi-agentrouter/issues/40)) ([db04dcf](https://github.com/chanyou0311/fastapi-agentrouter/commit/db04dcfaa7c9f1091613e6f61d51a3d6dfdf7ab5))
* override release version to avoid breaking change bump ([#44](https://github.com/chanyou0311/fastapi-agentrouter/issues/44)) ([4726fa2](https://github.com/chanyou0311/fastapi-agentrouter/commit/4726fa26038f51cc240530d728ae982ab880bd17))

## [0.4.0](https://github.com/chanyou0311/fastapi-agentrouter/compare/v0.3.0...v0.4.0) (2025-08-11)


### ⚠ BREAKING CHANGES

* Changed disable_slack to enable_slack (inverted logic)

### Features

* add auto-approve and auto-merge workflow for chanyou0311 PRs ([#28](https://github.com/chanyou0311/fastapi-agentrouter/issues/28)) ([5d9a566](https://github.com/chanyou0311/fastapi-agentrouter/commit/5d9a5667d793fbdf5a70292537ed67120eb00b29))


### Bug Fixes

* Reimplement slack integration ([#37](https://github.com/chanyou0311/fastapi-agentrouter/issues/37)) ([5a82b6f](https://github.com/chanyou0311/fastapi-agentrouter/commit/5a82b6f2f96cb3b1190fbe6b4abe05c5696a25cd))


### Documentation

* comprehensive CLAUDE.md architecture update ([#33](https://github.com/chanyou0311/fastapi-agentrouter/issues/33)) ([c273f1d](https://github.com/chanyou0311/fastapi-agentrouter/commit/c273f1da10df1d8e886cdcf6744df66169b697dd))


### Miscellaneous Chores

* override release version to avoid breaking change bump ([#30](https://github.com/chanyou0311/fastapi-agentrouter/issues/30)) ([793531a](https://github.com/chanyou0311/fastapi-agentrouter/commit/793531a37f08baa02a0df9274851bf996e616a76))


### Code Refactoring

* improve settings configuration with dependency injection ([#25](https://github.com/chanyou0311/fastapi-agentrouter/issues/25)) ([ae18e7b](https://github.com/chanyou0311/fastapi-agentrouter/commit/ae18e7bf5e040e3a90247af70c841db91ab5a1f1))

## [0.3.0](https://github.com/chanyou0311/fastapi-agentrouter/compare/v0.2.0...v0.3.0) (2025-08-07)


### Features

* MkDocsドキュメントにi18n対応を追加 ([#24](https://github.com/chanyou0311/fastapi-agentrouter/issues/24)) ([75f412c](https://github.com/chanyou0311/fastapi-agentrouter/commit/75f412c31bd543e4e9c6a0eb827e30690a31f0ce))


### Bug Fixes

* Remove incorrect Discord and webhook references from CLAUDE.md ([#23](https://github.com/chanyou0311/fastapi-agentrouter/issues/23)) ([9b28e3b](https://github.com/chanyou0311/fastapi-agentrouter/commit/9b28e3b2f661fa0cd4306dd455f3bbc6df7d5c2a))


### Documentation

* add Python version compatibility testing workflow ([#16](https://github.com/chanyou0311/fastapi-agentrouter/issues/16)) ([e51f473](https://github.com/chanyou0311/fastapi-agentrouter/commit/e51f473bd7997e55c3b94f33340845a3bacc25c0))

## [0.2.0](https://github.com/chanyou0311/fastapi-agentrouter/compare/v0.1.2...v0.2.0) (2025-08-07)


### Features

* implement Slack integration with Slack Bolt for Python ([#13](https://github.com/chanyou0311/fastapi-agentrouter/issues/13)) ([620090f](https://github.com/chanyou0311/fastapi-agentrouter/commit/620090f0f575eb11fd529f0a815f0980e37728c3))
* migrate environment variables to pydantic-settings ([#14](https://github.com/chanyou0311/fastapi-agentrouter/issues/14)) ([011ea3b](https://github.com/chanyou0311/fastapi-agentrouter/commit/011ea3b298762b6c27a78586f0f94a966a86bff5))


### Bug Fixes

* add 'synchronize' event to PR linting workflow ([#11](https://github.com/chanyou0311/fastapi-agentrouter/issues/11)) ([858fcce](https://github.com/chanyou0311/fastapi-agentrouter/commit/858fcce5e29eb5d4c49aaa5f81a6caeb5dc4f240))
* change MkDocs theme color from blue to teal ([#15](https://github.com/chanyou0311/fastapi-agentrouter/issues/15)) ([08d9af4](https://github.com/chanyou0311/fastapi-agentrouter/commit/08d9af4d828a4d646f6ede4df6c286776bbd9dc4))

## [0.1.2](https://github.com/chanyou0311/fastapi-agentrouter/compare/v0.1.1...v0.1.2) (2025-08-06)


### Bug Fixes

* add PR title validation for Conventional Commits ([#5](https://github.com/chanyou0311/fastapi-agentrouter/issues/5)) ([a70b93a](https://github.com/chanyou0311/fastapi-agentrouter/commit/a70b93a01f46749010676b108d6599c125aa8295))
* add pre-commit file ending and auto-fix instructions ([#7](https://github.com/chanyou0311/fastapi-agentrouter/issues/7)) ([5319b54](https://github.com/chanyou0311/fastapi-agentrouter/commit/5319b54b87939047df23c4750c239a4b746ede2d))
* **deps:** pin dependencies ([#9](https://github.com/chanyou0311/fastapi-agentrouter/issues/9)) ([9c9a793](https://github.com/chanyou0311/fastapi-agentrouter/commit/9c9a7938cb0a786dd983586757a0edc677fc11a5))
* sync changelog between CHANGELOG.md and MkDocs ([#4](https://github.com/chanyou0311/fastapi-agentrouter/issues/4)) ([5082ffe](https://github.com/chanyou0311/fastapi-agentrouter/commit/5082ffeae202fab252d13e881299c6093c4e2c4e))

## [0.1.1](https://github.com/chanyou0311/fastapi-agentrouter/compare/v0.1.0...v0.1.1) (2025-08-06)


### Bug Fixes

* add pages permission to release workflow ([571ad7f](https://github.com/chanyou0311/fastapi-agentrouter/commit/571ad7f96d5e3d40b093b880f1b29ff17eef34e9))

## 0.1.0 (2025-08-06)


### Bug Fixes

* add permissions for issues in release workflow ([9b53ca6](https://github.com/chanyou0311/fastapi-agentrouter/commit/9b53ca6d477bd858578b09c98729cfd1051a15b0))
* add release configuration for fastapi-agentrouter ([60c8cec](https://github.com/chanyou0311/fastapi-agentrouter/commit/60c8cec02e7a83c65c6b1258c12353c2ef3af1de))
* add release manifest for version 0.1.0 ([3a788b1](https://github.com/chanyou0311/fastapi-agentrouter/commit/3a788b1151a50c652ff8390dd271abb1d0c93c51))
* update CI workflow to trigger on pull requests only ([93f7554](https://github.com/chanyou0311/fastapi-agentrouter/commit/93f7554846f081b120533dfb78df7d2e4764451f))
