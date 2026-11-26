# Blast Radius vs. Agent Autonomy {#blast-radius-matrix}

The right model is a **2×2 quadrant matrix**: it shows which operations can run autonomously, which need human review, and which are prohibited.

- Horizontal axis: blast radius, from low impact to high impact.
- Vertical axis: agent autonomy, from supervised to autonomous.
- The high-impact, high-autonomy quadrant is the danger zone.

@answer scope="Qualitative governance zones from the supplied specification; positions are illustrative, not scored thresholds."
@meta locale=en

## Governance matrix {#governance-matrix}

```mermaid title="Blast radius vs. agent autonomy"
quadrantChart
    x-axis Low blast radius --> High blast radius
    y-axis Low autonomy --> High autonomy
    quadrant-1 DANGER
    quadrant-2 AUTONOMOUS
    quadrant-3 ASSISTED
    quadrant-4 STRICT HITL
    RAG / read: [0.18, 0.82]
    Unsupervised write: [0.82, 0.82]
    Drafts: [0.18, 0.20]
    Finance / ERP: [0.82, 0.20]
```

## What belongs in each quadrant? {#quadrant-controls}

| Zone | Examples | Required control |
| --- | --- | --- |
| Autonomous | RAG / FAQ, DW reads, intent classification | Allow autonomous read-only work. |
| Danger | Direct ERP mutation, data deletion without HITL | Prohibit autonomous high-impact mutation. |
| Assisted | Internal drafts, vector research, business analysis | Keep the user in control before use. |
| Strict HITL | Financial transfers, stock movement, bulk email, sensitive record changes | Dry-run, durable approval, and an audited human decision. |

@callout id=threshold-note level=note title="How to read the positions"
The points communicate relative policy zones from the supplied matrix. They are not calibrated risk scores; define numeric thresholds separately if the policy needs them.
