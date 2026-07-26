# Architecture

```
User Prompt
      │
      ▼
Research Agent
      │
      ▼
Code Generation Agent
      │
      ▼
Checker Agent
      │
      ▼
Self Correction Agent
      │
      ▼
Final Output
```

The project uses LangGraph to orchestrate multiple AI agents.

Each agent has a dedicated responsibility to improve the final code quality.
