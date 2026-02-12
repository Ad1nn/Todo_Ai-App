---
id: 001
title: Update Constitution for Phase 3
stage: constitution
date: 2026-01-21
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 002-fullstack-web-app
user: user
command: /sp.constitution
labels: ["phase3", "ai-chatbot", "mcp", "openai-agents"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - CLAUDE.md
tests:
  - null
---

## Prompt

update constitution for phase 3

## Response snapshot

Updated constitution from v1.1.0 to v1.2.0 (MINOR version bump) to add Phase 3 AI-Powered Chatbot requirements:

**New Principle Added:**
- Principle IX: AI Agent Design Principles - Covers MCP server design, agent behavior, and conversation management

**Modified Principles:**
- Principle VII (API Design): Extended to include chat endpoint patterns (`POST /api/{user_id}/chat`)
- Principle VIII (Security): Added AI/LLM-specific security guidance for API keys and user isolation

**New Technology Stack:**
- OpenAI Agents SDK for agent orchestration
- Official MCP SDK for tool exposure
- OpenAI ChatKit for chat UI
- New database models: Conversation, Message

**New Quality Gates:**
- MCP tools tested with mock agent responses
- Conversation persistence verified across requests
- User isolation enforced in all MCP tools

## Outcome

- ✅ Impact: Constitution updated to v1.2.0 with Phase 3 technologies and principles
- 🧪 Tests: N/A (documentation change)
- 📁 Files: constitution.md (updated), CLAUDE.md (updated)
- 🔁 Next prompts: /sp.specify for Phase 3 chatbot feature
- 🧠 Reflection: Constitution now provides clear guidance for AI agent implementation following SDD principles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): standard constitution update
- Next experiment (smallest change to try): Proceed to /sp.specify for Phase 3
