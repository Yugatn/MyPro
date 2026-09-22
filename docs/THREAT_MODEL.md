# Threat Model

MyPro processes untrusted media and third-party extensions. The security model therefore starts at the parser and plugin boundaries.

## Assets

- source media;
- project state;
- analysis results;
- provenance;
- credentials and signing material;
- user data.

## Threats

- malicious or malformed media;
- parser memory corruption;
- decompression bombs;
- path traversal;
- malicious plugins;
- unauthorized network access;
- sandbox escape;
- dependency compromise;
- stale or substituted external media;
- tampered analysis artifacts.

## Controls

- bounded parsing and fuzzing;
- explicit path validation;
- deny-by-default capabilities;
- process/WASM isolation where available;
- signed plugins for trusted distribution;
- pinned dependencies and SBOM;
- audit logging;
- content hashes and provenance;
- explicit restore and migration checkpoints.

Security controls are not a promise that every integration is safe. Each integration declares its trust boundary and limitations.
