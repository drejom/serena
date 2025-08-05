 R Language Server Protocol Implementation for Serena

  Task Overview

  Implement complete R Language Server Protocol support in Serena following the comprehensive specification in ADD_R_LSP.md.
  This involves Docker integration, core LSP implementation, testing infrastructure, and clean git commits.

  Required Reading

  Please read these files first to understand the requirements and architecture:
  - ADD_R_LSP.md - Complete R LSP implementation specification
  - CLAUDE.md - Serena project guidelines and development commands
  - src/solidlsp/ls_config.py - Existing language configuration patterns
  - src/solidlsp/ls.py - Language server factory patterns
  - src/solidlsp/language_servers/ - Existing language server implementations for reference
  - Dockerfile - Current Docker configuration to modify

  Available Specialized Agents

  You have access to 6 specialized agents located in .claude/agents/:

  1. r-lsp-orchestrator - Primary coordinator with deep architecture knowledge
  2. docker-integration-specialist - Handles R runtime containerization
  3. language-server-implementer - Core LSP implementation specialist
  4. test-infrastructure-builder - Creates comprehensive testing framework
  5. r-language-expert - R ecosystem domain specialist
  6. git-commit-manager - Ensures clean, logical commits

  Available Tools

  - File Operations: Read, Edit, MultiEdit, Write, Glob, Grep, LS
  - System Operations: Bash (for running tests, builds, git operations)
  - Coordination: TodoWrite (track progress), Task (launch specialized agents)
  - MCP Integration: MetaMCP server access for all agents

  Implementation Strategy

  1. Start with r-lsp-orchestrator to coordinate the overall implementation
  2. Follow the phase-based approach:
    - Phase 1: Docker foundation (docker-integration-specialist)
    - Phase 2: Core LSP implementation (language-server-implementer + r-language-expert)
    - Phase 3: Testing infrastructure (test-infrastructure-builder)
    - Phase 4: Integration & clean commits (git-commit-manager)

  Success Criteria

  - Docker container includes R runtime and languageserver package
  - RLanguageServer class implemented with full LSP support
  - Comprehensive test suite with realistic R package structure
  - All tests pass: uv run poe test -m "r"
  - Code formatted and type-checked: uv run poe format && uv run poe type-check
  - Clean git history with logical, atomic commits
  - Integration with existing Serena architecture maintained

  Getting Started

  Launch the r-lsp-orchestrator agent to begin coordinating this implementation. The orchestrator will manage the other agents
  and ensure proper sequencing and conflict resolution.

  ---
  Prompt: Using the specialized agents and following the ADD_R_LSP.md specification, implement complete R Language Server
  Protocol support in Serena with Docker integration, comprehensive testing, and clean git commits.
