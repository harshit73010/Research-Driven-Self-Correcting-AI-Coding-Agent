# Workflow

```
Start
 │
 ▼
ResearchAgent
 │
 ▼
CodeAgent
 │
 ▼
CheckerAgent
 │
 ├───────────────┐
 ▼               │
SelfCorrectAgent │
 │               │
 └───────────────┘
 │
 ▼
End
```

If the checker detects an issue, the workflow automatically routes to the SelfCorrectionAgent before returning the final output.
