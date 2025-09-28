---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
---

The user input can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.

2. Load and analyze the implementation context:
   - **REQUIRED**: Read tasks.md for the complete task list and execution plan
   - **REQUIRED**: Read plan.md for tech stack, architecture, and file structure
   - **IF EXISTS**: Read data-model.md for entities and relationships
   - **IF EXISTS**: Read contracts/ for API specifications and test requirements
   - **IF EXISTS**: Read research.md for technical decisions and constraints
   - **IF EXISTS**: Read quickstart.md for integration scenarios

3. Parse tasks.md structure and extract:
   - **Task phases**: Setup, Tests, Core, Integration, Polish
   - **Task dependencies**: Sequential vs parallel execution rules
   - **Task details**: ID, description, file paths, parallel markers [P]
   - **Execution flow**: Order and dependency requirements

4. Execute implementation following the task plan:
   - **Phase-by-phase execution**: Complete each phase before moving to the next
   - **Respect dependencies**: Run sequential tasks in order, parallel tasks [P] can run together
   - **Follow TDD approach**: Execute test tasks before their corresponding implementation tasks
   - **File-based coordination**: Tasks affecting the same files must run sequentially
   - **Validation checkpoints**: Verify each phase completion before proceeding
   - **Task-by-task commits**: Create individual commits for each completed task (detailed in steps 6 and 8)
   - **Incremental progress**: Each task should be fully completed and committed before moving to the next task

5. Implementation execution rules:
   - **Setup first**: Initialize project structure, dependencies, configuration
   - **Tests before code**: If you need to write tests for contracts, entities, and integration scenarios
   - **Core development**: Implement models, services, CLI commands, endpoints
   - **Integration work**: Database connections, middleware, logging, external services
   - **Polish and validation**: Unit tests, performance optimization, documentation

6. Progress tracking and error handling:
   - **Individual task completion cycle**:
     1. Implement the task completely
     2. Validate the implementation works correctly
     3. Mark task as [X] completed in tasks.md
     4. Create individual git commit for this task (using step 8 strategy)
     5. Report task completion and move to next task
   - **Error handling**: Halt execution if any non-parallel task fails
   - **Parallel tasks [P]**: Continue with successful tasks, report failed ones
   - **Clear error messages**: Provide context for debugging when tasks fail
   - **Recovery guidance**: Suggest next steps if implementation cannot proceed

7. Completion validation:
   - Verify all required tasks are completed
   - Check that implemented features match the original specification
   - Validate that tests pass and coverage meets requirements
   - Confirm the implementation follows the technical plan
   - Report final status with summary of completed work

8. **Task-by-task commit strategy**:
   - **Individual commits**: Create a separate git commit for each completed task
   - **Commit timing**: After each task is fully implemented and validated
   - **Commit message format**: Use task ID and description for clear tracking
     ```
     feat(task-ID): Brief description from tasks.md

     Implements task ID with details:
     - [Specific changes made]
     - [Files affected]

     🤖 Generated with [Claude Code](https://claude.ai/code)

     Co-Authored-By: Claude <noreply@anthropic.com>
     ```
   - **Commit scope**: Include all files changed for that specific task only
   - **Progress tracking**: Update tasks.md to mark task as [X] completed before each commit
   - **Validation before commit**: Ensure task implementation is complete and functional
   - **Parallel task handling**: For parallel tasks [P], commit each one individually when completed

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/tasks` first to regenerate the task list.
