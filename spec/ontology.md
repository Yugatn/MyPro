# MyPro Ontology v0.2

MyPro uses a small, explicit ontology so that data, interpretation, proposals and applied changes cannot be silently conflated.

| Entity | Meaning | Not this |
|---|---|---|
| Asset | An identifiable source, proxy, render or derived media artifact | A timeline clip |
| Observation | A measured or detected fact produced by an analyzer | A conclusion |
| Interpretation | A model-based interpretation of observations | Ground truth |
| Finding | An aggregated, reviewable conclusion | A verdict |
| Hypothesis | A proposition that can be tested | An action |
| Proposal | A suggested change produced by AI or a plugin | A project mutation |
| Decision | An explicit human or policy choice | The mutation itself |
| Action | An applied project change | A proposal |
| Revision | A recoverable version of project state | A file on disk |
| Invariant | A property that can be mechanically checked | A design wish |
| Policy | A rule governing whether an operation may be applied | A capability |

## Decision boundary

The canonical control boundary is:

**AI or analyzer proposes. Core validates. Human or policy decides. Action applies. Project records.**

An implementation may automate a decision only when an explicit policy permits it and the decision remains auditable and reversible.

## Non-conflation rules

1. Missing analysis is not evidence of absence.
2. Confidence is not truth.
3. A finding is not a verdict.
4. A proposal is not an action.
5. A capability is not permission.
6. A proxy is not an original asset.
7. A revision is not merely the latest serialized file.
