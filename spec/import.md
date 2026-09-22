# Universal Import Layer

Import is an adapter that produces evidence, not a mutation.

The contract consists of a source descriptor, canonical candidate, import manifest, mapping report, loss report, relinking report and provenance.

An import result becomes a project mutation only through an explicit Proposal, Policy Evaluation, Decision and Action.

Loss is recorded instead of silently discarded. Unsupported effects, markers, custom metadata and unresolved media receive explicit severity, fallback and confidence.

Media relinking uses exact hash, path match, filename match, manual or none. Unresolved references become placeholders and cannot be silently substituted.

Invariant: I_import_is_proposal.
