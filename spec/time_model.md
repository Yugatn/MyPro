# Time Model v0.3

MyPro uses exact rational time internally.

## TimeBase

A timebase declares:

- unit;
- epoch;
- resolution;
- source.

Supported conceptual epochs include project-relative, camera-relative and absolute clock references.

## SyncGroup

A SyncGroup relates assets using a declared synchronization method:

- timecode;
- audio waveform;
- sensor correlation;
- manual alignment;
- external clock.

Offsets are represented as exact rational values.

## External clocks

Future integrations may record GPS, NTP or PTP clock identity and declared accuracy.

## Drift

Audio/video drift and variable frame rate are represented explicitly rather than hidden by float rounding.

## Invariant

**I_timebase_conserved** — conversion between declared timebases does not lose precision beyond the declared resolution.
