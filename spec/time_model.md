# Time Model v0.3

Canonical project time is rational.

Frame rates, sample rates and external clocks are represented explicitly. Multi-camera synchronization uses named SyncGroup objects containing members and SyncPoint pairs. External clock identity and epoch are recorded when synchronization depends on them.

No canonical project state stores floating-point time values. Float seconds are an interchange convenience only.
