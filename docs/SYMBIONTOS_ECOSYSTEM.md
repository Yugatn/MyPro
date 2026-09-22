# SymbiontOS Ecosystem

## 1. What this project is

SymbiontOS is a conceptual and engineering ecosystem for building a common digital environment in which content, observations, software agents, communication, identity, security, policies and human decisions can exist as connected but distinguishable layers.

SymbiontOS is not limited to one application. It is the environment in which several specialized projects can operate on the same underlying objects, evidence and provenance.

The central architectural idea is that a video, image, text, audio recording, live stream, observation, semantic fragment, analysis result, discussion or AI proposal should not become an isolated copy inside every application. The ecosystem should preserve a common identity for the underlying object and allow different subsystems to work with it according to their own responsibilities.

The current MyPro architecture is one concrete part of this ecosystem. Cinema Catharsis is a methodological and analytical part. Eugene Messenger is a communication part. Other components of SymbiontOS can provide identity, policy enforcement, cognitive safety, AI execution, security, audit, research export and future operating-system/runtime capabilities.

SymbiontOS therefore describes a shared environment rather than a collection of unrelated products.

## 2. Authorial origin

SymbiontOS is an authorial project and architectural direction being developed by Yugatn.

The project is developed incrementally. Some components already exist as prototypes or implemented modules, while other components remain architectural specifications, research directions or future implementation targets.

This distinction is important. The ecosystem documentation describes the intended architecture without presenting every planned subsystem as already implemented.

## 3. The main architectural principle

The ecosystem is organized around a common evidence and provenance substrate.

The basic principle is:

> The same underlying object should be represented once as accurately as possible, while different subsystems create different views, measurements, proposals and interactions around it.

For example, a video may be imported into MyPro. The media object receives a stable identity and source provenance. Analysis can produce observations about time ranges. Fragment detection can identify candidate semantic fragments. Cinema Catharsis can calculate descriptive content metrics from those observations. MyPro can use the fragments for montage. Eugene Messenger can attach a discussion to an exact fragment or time range. An AI subsystem can propose an edit. A policy layer can check whether the proposed operation is permitted. The final decision can then be recorded with its provenance.

These operations should remain distinguishable.

An observation is not automatically a conclusion.

A fragment candidate is not automatically an editorial decision.

An AI proposal is not automatically an action.

A discussion is not automatically evidence.

A metric is not automatically a causal explanation.

This separation is a foundational property of SymbiontOS.

## 4. Ecosystem structure

The current conceptual ecosystem contains several major layers.

### SymbiontOS

The common environment and architectural framework.

It provides the principles and shared interfaces through which specialized components can cooperate.

### MyPro

MyPro is the content and media environment.

Its responsibilities include:

- importing and representing media;
- preserving source provenance;
- representing exact time ranges;
- creating semantic fragments;
- viewing and selecting content;
- editing and montage construction;
- project state;
- analysis integration;
- evidence representation;
- publication-oriented workflows;
- backup and recovery;
- integration with external media technologies;
- future live-stream ingest and real-time editing.

MyPro is therefore more than a conventional video editor. It is intended to be an evidence-aware content environment.

### Cinema Catharsis

Cinema Catharsis is the formal methodology for descriptive analysis of media content.

It defines:

- content ontology;
- coding categories;
- event representation;
- temporal measurements;
- category duration;
- screen-time share;
- event density;
- category coverage;
- repeatability;
- normalized distribution;
- entropy;
- overlap-safe duration;
- coding uncertainty;
- category co-occurrence;
- reliability methodology.

Cinema Catharsis operates on observations and provenance supplied by the common environment. It does not need to create a separate copy of the media evidence.

Its methodological boundary is explicit: content coding does not by itself establish viewer exposure, viewer emotion, psychological effect, harm or causality.

### Eugene Messenger

Eugene Messenger is the communication environment.

It can provide:

- personal communication;
- group communication;
- discussions;
- channels;
- comments;
- presence;
- notifications;
- communication events;
- discussion around content;
- discussion around semantic fragments;
- discussion around exact time ranges;
- future integration with projects, observations and evidence.

The messenger can provide a social context around an object without silently changing the evidentiary status of that object.

### Shared evidence and provenance layer

This layer connects the ecosystem.

Its conceptual objects include:

- source content identity;
- content hashes;
- observations;
- semantic fragments;
- time ranges;
- analyzer identity;
- analyzer version;
- methodology version;
- source references;
- uncertainty;
- missing ranges;
- transformations;
- decisions;
- revisions;
- provenance records.

The purpose is reproducibility and traceability.

### AI and agent layer

AI systems can operate on the common substrate.

They may:

- analyze content;
- detect candidate fragments;
- summarize observations;
- propose edits;
- propose classifications;
- generate alternative interpretations;
- assist with project organization;
- assist with communication;
- generate research reports.

AI should normally produce explicit proposals or observations rather than silently mutating canonical project state.

### Policy and security layer

Security is not an optional add-on.

The ecosystem is intended to use:

- identity;
- capabilities;
- authorization;
- policy evaluation;
- provenance;
- audit records;
- controlled integrations;
- explicit source authorization;
- bounded operations;
- reversible actions where possible.

A capability does not automatically mean that an operation is permitted. Authorization and policy remain separate concerns.

### Cognitive-safety and ethical layer

The ecosystem is intended to connect with the broader EthicalAudit and PICCS architecture.

This layer can evaluate communications, proposed operations and other relevant events according to explicit rules and policies.

The purpose is not to replace human judgment with a hidden value classifier. The purpose is to make important constraints explicit, inspectable and auditable.

## 5. One environment, multiple interfaces

The same underlying evidence may appear differently depending on the subsystem.

For example:

A media source can be represented in MyPro as a media asset.

The same time range can be represented as a semantic fragment.

The same observation can become a Cinema Catharsis measurement.

The same fragment can become a discussion anchor in Eugene Messenger.

The same project can be inspected by an AI agent.

The same proposed operation can be evaluated by a policy engine.

The same final decision can be preserved in an audit trail.

These are different views of connected state, not necessarily independent copies.

## 6. The content lifecycle

A typical ecosystem workflow can be described in words.

A source enters the environment through an authorized import or live source connector.

MyPro records the source identity, media properties and provenance.

The system can inspect the media and generate observations.

Analysis modules can identify candidate semantic fragments.

The Viewer-Editor allows a human to inspect those fragments and select exact ranges.

Cinema Catharsis can measure coded content using the same observations and exact time ranges.

An editor can construct a montage from selected fragments.

An AI subsystem can propose an alternative montage, classification or transformation.

The proposal passes through validation and policy checks.

A human or authorized process decides whether the proposal becomes an action.

The resulting project state and its provenance are recorded.

Eugene Messenger can then provide communication around the resulting content or the evidence used to create it.

The important property is continuity of provenance throughout this process.

## 7. Live content

The same architecture extends to live media.

A live source can enter through an authorized connector such as a camera, RTMP source, SRT source, WebRTC source or another supported integration.

The system can create a bounded rolling media buffer.

Incoming media can be transcoded into an editing-friendly representation.

Analysis can operate while the source is still arriving.

Candidate fragments can be generated before the live source ends.

A human can select a time range from the rolling buffer and add it to an evolving montage.

Cinema Catharsis can calculate descriptive measurements over available ranges.

Dropped media, discontinuities and unavailable ranges must remain visible in provenance rather than being silently reconstructed as if the source were complete.

The future YouTube integration must respect the source platform's authorization and applicable access rules. The architecture is therefore based on authorized source connectors rather than arbitrary extraction of internal platform streams.

## 8. Fragments as a common language

A Fragment is one of the important objects connecting MyPro and the wider ecosystem.

A fragment is a bounded, provenance-preserving representation of a part of a source.

Fragments can represent:

- media intervals;
- scenes;
- speech;
- actions;
- reactions;
- objects;
- people;
- sounds;
- semantic events;
- composite structures.

A fragment can be a candidate rather than a final accepted object.

This distinction allows AI and analysis systems to propose fragments while leaving the final editorial or research decision explicit.

The fragment can then be used simultaneously for viewing, editing, analysis, discussion and research export.

## 9. Evidence and interpretation

SymbiontOS distinguishes several levels of information.

### Source

What entered the system from an external or internal source.

### Observation

What a detector, analyst or human coder recorded about the source.

### Measurement

A formal calculation based on observations.

### Interpretation

A statement that gives meaning to observations or measurements.

### Proposal

A suggested operation, classification or transformation.

### Decision

An explicit choice to accept, reject or modify a proposal.

### Action

A state-changing operation executed under authorization.

### Result

The state produced by an action.

Keeping these levels separate prevents a measurement from being mistaken for a conclusion and prevents an AI proposal from being mistaken for an executed action.

## 10. Provenance

Every important derived object should be traceable to its source.

For an analytical result, provenance can include:

- source content identifier;
- source content hash;
- analyzed time range;
- source version;
- observation identifiers;
- analyzer identifier;
- analyzer version;
- methodology version;
- ontology version;
- formula configuration;
- uncertainty representation;
- missing or dropped ranges;
- transformation history.

For an editorial result, provenance can additionally include:

- source fragments;
- montage revision;
- operation history;
- decision identity;
- actor identity;
- authorization context.

This allows a result to be examined rather than merely trusted.

## 11. Exact time

Time is a canonical part of the ecosystem.

MyPro uses exact rational time representations rather than floating-point values for canonical timeline semantics.

This matters because fragments, observations, edits, synchronization and measurements all depend on precise temporal boundaries.

A time range should have explicit start and end values and consistent half-open interval semantics.

The same temporal representation can therefore be reused by editing, analysis, evidence and communication layers.

## 12. Cinema Catharsis within SymbiontOS

Cinema Catharsis is not an isolated report generator.

It is a domain methodology operating on the shared evidence substrate.

A coded event can simultaneously be:

- an observation;
- part of a semantic fragment;
- a timeline marker;
- an input to a montage decision;
- an input to a Cinema Catharsis metric;
- a research-export record;
- a discussion reference.

The underlying observation should not be duplicated merely because different interfaces need different representations.

Cinema Catharsis therefore strengthens the ecosystem's analytical layer while MyPro provides the technical substrate on which the methodology can operate.

## 13. Eugene Messenger within SymbiontOS

Communication is treated as another connected layer.

A user should be able to discuss:

- a complete media item;
- an exact fragment;
- an exact time range;
- an observation;
- an analysis result;
- an editorial decision;
- a published version;
- a research result.

A discussion can preserve a reference to the object being discussed.

This makes communication contextual rather than detached from the underlying content.

At the same time, a message remains a message. It should not automatically become a verified observation merely because it is attached to evidence.

## 14. SymbiontOS and the broader architecture

SymbiontOS is intended to connect with the larger architecture of the user's projects.

Relevant conceptual components include:

- PICCS;
- EthicalAudit;
- SymbiontOS runtime;
- AI guard and policy mechanisms;
- identity and capability systems;
- audit and provenance;
- Eugene Messenger;
- MyPro;
- Cinema Catharsis;
- future research and simulation environments.

The ecosystem can therefore be viewed as a common environment in which content, cognition, communication and computation are connected through explicit interfaces and evidence.

## 15. Security model

The security architecture should assume that integrations, plugins, AI agents and external sources can be unreliable or compromised.

Important principles include:

- least privilege;
- explicit capabilities;
- explicit authorization;
- capability expiration;
- source authorization;
- provenance preservation;
- input validation;
- immutable or append-oriented audit records;
- atomic snapshots;
- recoverable incomplete writes;
- controlled plugin boundaries;
- no implicit trust based only on component identity;
- separation of proposal and execution.

The security layer should protect both the data and the meaning of the data.

A technically valid file that has lost its provenance is not equivalent to the original evidence.

## 16. Backup and recovery

Recovery is part of the architecture rather than an administrative afterthought.

MyPro already establishes a foundation around:

- content-addressed snapshots;
- verification;
- backup;
- restore;
- hash-based integrity;
- append-oriented event history;
- incomplete-tail recovery.

Future SymbiontOS components should use the same philosophy.

A recovered state should be distinguishable from an unverified state.

If evidence is missing, the system should represent the missing evidence rather than silently inventing continuity.

## 17. Open-source architecture

SymbiontOS is intended to remain modular.

External technologies can be integrated through explicit boundaries.

Examples include:

- FFmpeg and ffprobe for media processing and inspection;
- OpenTimelineIO for editorial interchange;
- MLT for media/rendering infrastructure;
- other open-source editors and media projects as reference implementations.

External code should remain separated according to its licenses and integration boundaries.

The goal is not to create an unmaintainable monolithic fork of existing projects.

The goal is to combine proven technologies through a coherent evidence-aware architecture.

## 18. Extensibility

Future subsystems can be added without changing the identity of the ecosystem.

Possible future domains include:

- live editing;
- research environments;
- simulation;
- browser-based creation;
- mobile clients;
- desktop clients;
- plugin systems;
- source connectors;
- AI agents;
- collaborative editing;
- distributed evidence exchange;
- anonymized research export;
- semantic search;
- multimodal analysis.

A new component should preferably consume and produce explicit canonical objects rather than inventing a parallel data model without provenance.

## 19. Architectural invariants

The following principles are intended as long-term invariants.

1. Provenance must survive transformations whenever technically possible.
2. Exact source identity must not be replaced by an informal filename alone.
3. Canonical time must remain exact.
4. Observations must remain distinguishable from interpretations.
5. Measurements must remain distinguishable from causal claims.
6. AI proposals must remain distinguishable from executed actions.
7. A proposal must not mutate canonical state merely by existing.
8. Authorization must remain distinct from capability possession.
9. Live gaps and source discontinuities must remain visible.
10. Imported information must preserve source mapping and loss information.
11. Content metrics must not silently become claims about viewer response or harm.
12. Security decisions must be auditable.
13. Important state changes must be recoverable.
14. External integrations must have explicit boundaries.
15. Human decisions must remain representable as explicit decisions rather than being hidden inside automation.

## 20. Current implementation status

The ecosystem should be understood as a layered project with different maturity levels.

Implemented or prototyped components include parts of MyPro's foundation:

- exact rational time;
- content hashing;
- event logging;
- snapshots;
- project creation;
- backup and restore;
- montage model;
- montage validation;
- OTIO integration;
- import provenance;
- semantic fragments;
- Viewer-Editor model;
- Cinema Catharsis measurements;
- tests and documentation.

Other components are architectural or planned:

- full live ingest;
- rolling-buffer editing;
- production transcoding;
- broader source connectors;
- advanced AI pipelines;
- complete policy runtime integration;
- full Eugene Messenger integration;
- broader SymbiontOS runtime integration;
- distributed ecosystem services.

This distinction should remain explicit as the project evolves.

## 21. Long-term direction

The long-term direction is to build a common environment in which a person can move from source content to understanding, creation, communication and publication without losing the relationship between the resulting object and its origin.

The environment should make it possible to:

- observe;
- measure;
- analyze;
- select;
- edit;
- discuss;
- propose;
- decide;
- publish;
- verify;
- reproduce;
- research.

The same evidence can support different activities while retaining its identity and provenance.

That is the role of SymbiontOS as the common ecosystem.

## 22. Relationship between the projects

The projects can be summarized by responsibility:

| Component | Primary responsibility |
|---|---|
| SymbiontOS | Common ecosystem, runtime direction and architectural environment |
| MyPro | Content, media, evidence, fragments, editing and project environment |
| Cinema Catharsis | Formal descriptive content analysis and measurements |
| Eugene Messenger | Communication and contextual discussion |
| PICCS | Meta-ethical and epistemic constraints for bounded intervention |
| EthicalAudit | Formal rule-based cognitive-safety and communication auditing |
| AI layer | Analysis, generation and explicit proposals |
| Policy layer | Authorization and constraint evaluation |
| Evidence layer | Provenance, observations, measurements and traceability |

These responsibilities overlap through shared data and interfaces, but they should not collapse into one indistinguishable subsystem.

## 23. The central idea

SymbiontOS can be understood as an attempt to create a digital environment where different forms of activity share one verifiable context.

Content is not separated from its history.

Analysis is not separated from its evidence.

Communication is not separated from the object being discussed.

AI is not granted automatic authority merely because it can generate an answer.

Security is not reduced to authentication alone.

A project is not reduced to the latest exported file.

The ecosystem instead preserves relationships between source, observation, interpretation, proposal, decision and result.

This is the architectural foundation on which MyPro, Cinema Catharsis, Eugene Messenger and future SymbiontOS components can develop as parts of one connected environment.
