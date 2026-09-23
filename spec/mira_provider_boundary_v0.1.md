# Mira Provider Boundary v0.1

Mira is an orchestration role, not an authority source and not a hard-coded model.

A provider adapter MUST convert model output into MyPro typed envelopes before it enters the core.

The provider MUST NOT:
- mutate canonical project state;
- bypass policy checks;
- turn CLAIMED into OBSERVED;
- authorize its own proposal;
- suppress conflicts;
- infer object absence from access failure.

Runtime sequence:
1. Load canonical context.
2. Read existing Grok results.
3. Validate provenance.
4. Identify missing work.
5. Create a stable child task.
6. Dispatch through the agent runtime.
7. Independently verify.
8. Build Proposal.
9. Submit Proposal to Policy/Decision.
10. Execute only an authorized Action.
11. Append evidence and Revision.

The reference adapter is `ai/mira_adapter.py`.
