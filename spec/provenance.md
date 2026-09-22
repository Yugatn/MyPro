# Provenance Model

MyPro provenance records the derivation of observations, findings, proposals, actions and exported artifacts.

A provenance record identifies inputs and hashes, operation or analyzer identity, software version, code hash, configuration hash, environment when material, outputs, timestamp and parent provenance records.

Persisted provenance nodes are content-addressed. A provenance.link event binds the node hash and parent relationships to the append-only project history.

The resulting graph can be represented as a Merkle-style DAG and mapped to C2PA or W3C PROV for interoperability.

A provenance record describes how a result was produced. It does not prove that the result is correct.
