# MyPro GitHub Fine-grained PAT Gateway v0.1

## Purpose

The GitHub integration is a technical capability boundary, not the source of authorization. A Fine-grained personal access token gives the gateway technical access to GitHub; MyPro decides whether an agent may perform a particular operation.

## Token scope

The recommended Fine-grained PAT is restricted to:

- repository access: Yugatn/MyPro only;
- Contents: Read and write;
- Pull requests: Read and write;
- Metadata: Read-only;
- no unrelated repositories.

The token is supplied to the runtime through MYPRO_GITHUB_TOKEN. It is never stored in source code, event payloads, evidence, proposals, issues, pull requests, or agent context.

## PR-first write model

1. MyPro creates a GitHubAuthorization for a concrete task and actor.
2. The authorization specifies the repository, permitted operations, optional path scope, and target branch.
3. MyPro emits ACTION_AUTHORIZED carrying the authorization identifier and repository.
4. AuthorizedGitHubExecutor checks that the task is ACTION_READY and that the authorization matches the authorization event.
5. FineGrainedPATGateway creates a non-main branch.
6. Authorized files are written only to that branch.
7. The gateway opens a pull request targeting the authorization target branch.
8. Checks, review, branch protection, and the repository owner remain responsible for merge policy.
9. The gateway intentionally has no merge method.

## Security invariants

- Direct writes to main are rejected by the gateway.
- Path scopes are checked before file writes.
- Cross-repository authorization is rejected.
- A proposal is not an authorization.
- An authorization without ACTION_READY runtime state cannot execute.
- An ACTION_AUTHORIZED event must carry the same authorization identifier and repository used by the executor.
- Credentials are not part of the event model.
- Conflicts and verification state remain explicit.

## Threat model

The boundary is designed to reduce:

- accidental direct changes to main;
- cross-repository use of a repository-scoped token;
- path-scope escalation;
- treating an AI proposal as permission to mutate GitHub;
- accidental credential disclosure through protocol data.

The gateway does not replace GitHub branch protection or rulesets. Those controls should remain enabled for main, including required checks and review requirements appropriate to the repository.

## Operational contract

The gateway can read repository content and, after authorization, create a branch, write scoped files, and open a PR. It does not merge. A successful execution produces GitHub evidence that is recorded as GITHUB_CHANGE and REVISION_RECORDED events.

This document describes the v0.1 boundary. It is not a claim of complete production-grade authorization cryptography; later versions may bind authorization records to signed policy decisions and persistent external state.
