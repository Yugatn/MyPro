# Analyzer Trust Levels v0.3

Trust is distinct from capability. Capability limits what a component can do; trust determines which policies may permit it to execute.

## Levels

- core
- verified
- community
- untrusted
- sandboxed

Each analyzer records id/version, code hash, signature when applicable, trust declaration, Model Card reference and requested capabilities.

Policy determines acceptable trust levels.

**I_analyzer_trust_enforced** — an analyzer below the required trust level cannot execute a protected operation.
