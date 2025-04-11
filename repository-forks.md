# Repository Forks and References

This document tracks the repositories we've forked to use in our implementation.

## Forked Repositories

### 1. langchain-ai/langchain
- **Original:** https://github.com/langchain-ai/langchain
- **Our Fork:** [To be added after forking]
- **Purpose:** Document processing and LLM integration
- **Status:** To be forked

### 2. vercel/ai
- **Original:** https://github.com/vercel/ai
- **Our Fork:** [To be added after forking]
- **Purpose:** Chat UI and streaming responses
- **Status:** To be forked

### 3. shadcn/ui
- **Original:** https://github.com/shadcn/ui
- **Our Fork:** [To be added after forking]
- **Purpose:** UI components for DevDocs interface
- **Status:** Components installed, no fork needed

## Other Referenced Repositories

### 1. microsoft/semantic-kernel
- **URL:** https://github.com/microsoft/semantic-kernel
- **Purpose:** Reference for AI plugin architecture
- **Key Files to Study:**
  - `dotnet/src/SemanticKernel.Abstractions/AI/AIPlugin.cs`
  - `python/semantic_kernel/kernel.py`

### 2. reworkd/AgentGPT
- **URL:** https://github.com/reworkd/AgentGPT
- **Purpose:** Reference for autonomous agent implementation
- **Key Files to Study:**
  - `next/src/services/agent/agent.ts`
  - `platform/reworkd_platform/web/api/agent/tools/tools.py`

## How to Fork Repositories

1. Visit the repository URL on GitHub
2. Click the "Fork" button in the upper right
3. Select our organization as the fork destination
4. Clone the forked repo to your machine:
   ```bash
   git clone [forked-repo-url]
   ```
5. Add the upstream repo as a remote to stay updated:
   ```bash
   git remote add upstream [original-repo-url]
   ```
