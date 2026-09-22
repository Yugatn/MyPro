# Evidence Bundle v0.3

An Evidence Bundle is a portable, offline-verifiable representation of selected project state and its derivation history.

## Layout

A bundle may contain:

- manifest;
- project events and selected snapshots;
- media references;
- provenance graph;
- policy records;
- signatures;
- verification metadata;
- human-readable README.

Original media is optional. References may contain content hashes without copying the media.

## Root identity

The bundle manifest contains a root hash derived from canonicalized bundle metadata and included content.

Verification must not require network access.

## Selective disclosure

A bundle can intentionally omit unrelated media or project material. The manifest records omissions and referenced-but-not-included assets.

## Signatures

The format is designed to support Ed25519 signatures and interoperability with C2PA where semantic mapping is valid.

## Invariant

**I_bundle_self_verifying** — a verifier with the bundle and declared verification procedure can validate integrity offline.
