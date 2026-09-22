# Analyzer Model Card v0.3

Every production analyzer should publish a Model Card describing intended use and limitations.

## Required sections

- analyzer id and version;
- purpose;
- input assumptions;
- valid domain;
- training/evaluation provenance where applicable;
- metrics and evaluation corpus;
- known limitations;
- failure modes;
- determinism class;
- resource requirements;
- privacy characteristics.

## Domain mismatch

When input falls outside the declared valid domain, Core should not silently treat the result as equivalent to an in-domain result.

The Observation may be marked with a domain-mismatch status or reduced confidence according to the analyzer contract.

## Principle

A Model Card documents what an analyzer can reasonably claim and what it cannot establish. It is not a guarantee of correctness.
