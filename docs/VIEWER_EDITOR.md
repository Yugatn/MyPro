# MyPro Viewer-Editor

MyPro includes an architectural concept for a browser-like content viewer that can edit while content is being watched.

The viewer is not a separate player bolted onto the editor. It is a presentation surface over the same canonical content, fragment, montage, provenance and project models.

## Core interaction

While watching content, the user can:

- mark the current moment as a fragment boundary;
- select the current range as a reusable fragment;
- split by scene, speech, action or other detected boundaries;
- trim a selected range;
- add a selected fragment to a montage;
- create a new clip or sequence from selected fragments;
- attach a note or discussion to a time range;
- save the selection into a personal or project fragment collection.

The viewer should keep playback continuous while editorial operations are prepared as proposals.

## Architecture

The viewer consumes:

- MediaAsset
- FragmentIndex
- ContentFragment
- Timeline
- Observation and provenance data

Editorial operations produce:

- FragmentProposal
- Montage proposal
- time-anchored discussion/comment
- eventual Revision after an explicit decision

The viewer never directly mutates canonical project state merely because a detection or gesture occurred.

## Dual-purpose selection

A selection made during playback has two possible editorial interpretations:

1. **Fragment selection**: preserve the source range as a reusable reference.
2. **Timeline placement**: place a reference to that fragment into a montage.

These are distinct operations. A source fragment can therefore be reused in multiple projects without duplicating the media.

## Browser/social integration

For published content, the same viewer can expose social actions:

- watch;
- select a moment;
- create a clip;
- quote a range;
- comment on a range;
- reply with a video;
- remix when permitted;
- open the source project when authorized.

A viewer selection must preserve publication version and source time range so discussion and remix provenance remain stable.

## Implementation boundary

The initial implementation should be a platform-neutral Viewer Controller and event contract. Desktop, web and mobile interfaces can implement the same operations later.

The rendering backend remains separate. Viewer selection creates editorial data; FFmpeg or another renderer produces the resulting media artifact.

## Invariants

- playback state is not project state;
- selection is not publication;
- proposal is not action;
- source provenance survives selection;
- exact rational time is used;
- published-version references remain stable;
- no hidden media replacement occurs;
- editing operations remain auditable and reversible where possible.
