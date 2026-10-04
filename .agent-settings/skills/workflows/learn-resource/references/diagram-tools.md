# Diagram and knowledge tooling decisions

Roles decided with the user (2026-10-04); revisit when better tools appear.

| Need | Tool |
|---|---|
| Per-note overview, flows, sequences, state machines, ER | Mermaid (incl. `mindmap`) - renders in the bundled html |
| 3-4 polished hero diagrams in the master | a diagram-design skill |
| Hand-drawn whiteboard diagrams to memorize | an Excalidraw skill (`excalidraw-diagram-generator`; read its README/source before installing) |
| Numeric charts (estimation, comparisons) | a data-chart skill such as lieflat-charts; NOT for architecture |
| Knowledge base storage and agent recall | OKF (okf-agent-memory): Markdown+YAML concepts in git, bidirectional links, `okf validate`, `okf search`, MCP server. Spiked and adopted: links carry a type as a `type: text` prefix in the link description, validated with `okf validate --strict --drift` (details in okf.md); graph viewer is `scripts/okf_graph.py` |
| Auto-built graph tools | graphify was judged unsuitable for this workflow |

## References
- What are the best diagram skills for Claude Code? (Skillselion): https://skillselion.com/guides/best-diagram-skills-for-claude-code
- drawio vs Excalidraw vs Mermaid vs Penpot (MCP.Directory): https://mcp.directory/blog/drawio-vs-excalidraw-vs-mermaid-vs-penpot-skills-2026
- AI diagrams in 2026: mermaid vs drawio vs excalidraw skills (aipptskill): https://aipptskill.com/blog/ai-diagram-skills-guide/
- Claude Code Skills: SVG vs Mermaid vs Excalidraw (classmethod): https://dev.classmethod.jp/en/articles/build-svg-diagram-skill-for-claude-code/
- lieflat-charts: https://github.com/larashero3-dotcom/lieflat-charts
- coleam00/excalidraw-diagram-skill: https://github.com/coleam00/excalidraw-diagram-skill
- okf-agent-memory: https://github.com/okf-memory/okf-agent-memory
