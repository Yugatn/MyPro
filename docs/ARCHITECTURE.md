# Architecture

## 1. Core idea

MyPro is built around a stable intermediate representation of a video project.

The central object is the Montage Model. It describes media references, tracks, clips, timing, transitions, audio decisions, titles and other editable operations without tying the project to one particular UI or renderer.

This separation allows the same project to be processed by a desktop editor, automated tools, AI services and interchange adapters.

## 2. Layers

### Media layer

Responsible for:
- source files;
- media identity;
- technical metadata;
- hashes;
- time ranges;
- proxy relationships.

### Analysis layer

Produces observations rather than silently changing the edit:
- scene boundaries;
- speech transcripts;
- subtitles;
- shot descriptions;
- duplicate and near-duplicate candidates;
- audio measurements;
- semantic tags.

### Montage Model

The canonical editable representation.

It should be deterministic, serializable and independently testable.

### Application layer

Provides human interaction:
- media browser;
- timeline;
- preview;
- inspector;
- AI suggestions;
- undo and redo;
- export controls.

### Integration layer

Connects MyPro to external technologies such as FFmpeg and OpenTimelineIO.

External systems must not become the hidden source of truth for the project.

## 3. AI boundary

AI may propose:
- clip selection;
- ordering;
- trimming;
- subtitles;
- music and sound suggestions;
- rough cuts;
- semantic metadata.

AI proposals must be represented as explicit project changes or suggestions. They must remain inspectable, reversible and rejectable by the user.

## 4. First implementation

The first implementation deliberately avoids a large editor.

Milestone 0 consists of:
1. Python package structure.
2. Media manifest model.
3. Montage Model draft.
4. JSON serialization.
5. Basic validation.
6. Tests.
7. FFprobe adapter as the first real media integration.

## 5. Future architecture

Later stages may introduce a high-performance media engine in Rust or C++, desktop UI, mobile UI, GPU acceleration, plugin isolation, camera integration, cloud collaboration and AI providers.

Those components are intentionally not required for the first milestone.
