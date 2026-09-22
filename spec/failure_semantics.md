# Failure Semantics v0.3

Analyzer execution is transactional at the observation-batch boundary.

An analyzer may emit observations incrementally, but Core buffers them until the run completes successfully.

Successful run: all buffered observations are committed.

Analyzer exception: no ordinary observation from that run is committed. The failed run is recorded as analysis.failed with analyzer identity, input references and error class.

Partial diagnostic output may be stored only as an explicitly labeled diagnostic evidence artifact.

This prevents partial output from masquerading as a complete analysis.
