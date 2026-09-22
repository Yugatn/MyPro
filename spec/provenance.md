# Provenance Model

MyPro provenance records the derivation of observations, findings, proposals, actions and exported artifacts.

A provenance record SHOULD identify:

- input artifact ids and hashes;
- operation or analyzer id;
- software/model version;
- code hash;
- configuration hash;
- environment information when material;
- output ids;
- timestamp;
- parent provenance records;
- optional signature.

The resulting graph is content-addressed and can be represented as a Merkle-style DAG.

## Interoperability

The model is designed to support mappings to:

- C2PA / Content Credentials for content provenance;
- W3C PROV concepts for provenance interchange.

These are interoperability targets, not dependencies of the core.

## Evidence rule

A provenance record describes how a result was produced. It does not prove that the result is correct.
