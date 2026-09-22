# MCP Authorization Boundary v0.3

MCP is an adapter protocol, not an authority layer.

## Architecture

Agent → MCP Gateway → Core SDK/API

The Gateway is an untrusted protocol boundary. Authorization remains in Core.

Every invocation reaching Core carries agent identity, capability token, verb id/version, target resource ids and a request correlation id. Core validates identity, capability scope/revocation, verb availability, policy, resource identity, rate limits and invariant preconditions.

Denied requests are audited. The Gateway cannot mint or broaden capabilities.

## Invariants

**I_mcp_cannot_escalate** — MCP cannot execute a verb outside Core-granted authority.

**I_agent_identity_verifiable** — agent-originated operations are attributable to a verifiable identity or explicitly marked untrusted.
