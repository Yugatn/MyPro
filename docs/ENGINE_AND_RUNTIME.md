# Engine and Runtime Strategy

## Engine-first

MyPro Core is headless and independent of RosEdit.

RosEdit Desktop, RosEdit Mobile, CLI tools, workers and future agent runtimes consume the same project and evidence contracts.

## Renderer as a service

Rendering is an integration service rather than a responsibility of the project model.

The architecture permits:

- FFmpeg-based processing;
- MLT-based rendering;
- native platform renderers;
- future hardware-accelerated backends.

A renderer consumes an explicit render specification and returns a result with provenance. It must not silently rewrite canonical project state.

## Dual timeline representation

MyPro supports two complementary representations:

1. Track-oriented Montage Model for familiar NLE editing.
2. Graph-oriented processing/proposal model for compositing, analysis and agent workflows.

The canonical project can preserve both where their semantics differ. A graph transformation must not silently change the meaning of the editorial timeline.

## Mobile

RosEdit Mobile is not a thin UI wrapper around a desktop editor.

The mobile application should eventually use:

- native preview/render paths;
- platform hardware acceleration;
- Core contracts through FFI;
- the same project/evidence model;
- independent preview and export pipelines.

The first mobile implementation should not block the desktop/headless foundation.

## Backends

External systems remain replaceable integrations.

MyPro does not make FFmpeg, MLT, OpenTimelineIO or a mobile media framework the canonical source of truth.
