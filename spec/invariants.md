# MyPro Invariants

Invariants are executable architectural properties. Each invariant should eventually have at least one automated test.

- `I_project_atomicity`: interrupted writes never install a partial canonical project.
- `I_backup_recoverability`: a declared recovery point can be verified and restored.
- `I_external_reference_transparency`: missing or changed external media is explicit.
- `I_analysis_provenance`: derived analysis has traceable inputs and analyzer identity.
- `I_uncertainty_visible`: uncertainty is not silently discarded during aggregation.
- `I_observation_not_conclusion`: observations cannot be serialized as findings without an explicit transformation.
- `I_plugin_capability_bound`: plugins operate only within granted capabilities and scopes.
- `I_no_hidden_control`: plugin or AI changes require an explicit policy-controlled application path.
- `I_reversible_action`: destructive or material actions have a recoverable prior revision.
- `I_domain_formula_explicit`: domain formulas declare inputs, assumptions, version and output semantics.
- `I_proxy_integrity`: a proxy cannot silently replace an original for a final operation requiring originals.
- `I_timeline_consistency`: timeline operations preserve valid time intervals and references.
- `I_event_log_append_only`: existing event records are never mutated in place.
- `I_timebase_rational`: canonical time is represented exactly.
- `I_no_silent_substitution`: a missing or changed artifact cannot be replaced without an explicit decision.
