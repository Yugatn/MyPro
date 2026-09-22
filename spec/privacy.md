# Privacy and Ethical Constraints v0.3

Privacy is represented as machine-checkable project metadata and policy constraints.

## Privacy levels

Projects and assets may declare levels such as:

- public;
- internal;
- confidential;
- restricted;
- personal_data.

Derived observations inherit the minimum required privacy scope of their inputs unless an explicit transformation policy permits a change.

## Sensitive processing

Analyzers declare whether they perform sensitive processing, including identity or other restricted classification.

A project policy can deny such analyzers before execution or deny publication of their outputs.

## Redaction

Redaction and anonymization are explicit transformations with provenance. They do not silently overwrite originals.

## Invariant

**I_no_hidden_person_classification** — when project policy prohibits a declared sensitive classification, Core refuses execution and records the policy decision.

Ethical restrictions are implemented as constraints on execution and data flow, not merely documentation.
