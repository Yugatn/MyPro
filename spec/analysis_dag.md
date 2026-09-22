# Analysis DAG

Analysis is modeled as a directed acyclic computation graph.

A node declares:

- analyzer id;
- analyzer version;
- code hash;
- configuration hash;
- input artifact ids/hashes;
- output observation ids;
- cache key;
- resource/capability requirements;
- provenance record.

## Invalidation

A cached result is reusable only when all declared inputs and execution identity remain compatible.

Changes to any of the following invalidate dependent results:

- input asset hash;
- upstream observation identity;
- analyzer version;
- analyzer code hash;
- configuration hash;
- declared model identity;
- relevant execution environment, when the analyzer declares environment dependence.

## Generation

Generative operations can be represented as graph nodes as well.

Generation nodes must record, when available:

- provider;
- model id and version;
- prompt or structured request;
- source assets;
- seed;
- generation parameters;
- resulting asset hashes.

Generation is therefore part of evidence rather than an opaque side channel.
