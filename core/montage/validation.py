"""Validation rules for the first Montage Model revision."""

from dataclasses import dataclass

from .model import MontageProject


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    clip_id: str | None = None


def validate_project(project: MontageProject) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    seen = set()
    for clip in project.clips:
        if clip.id in seen:
            issues.append(
                ValidationIssue("duplicate_clip_id", "Clip id is duplicated.", clip.id)
            )
        seen.add(clip.id)

        if clip.start_seconds < 0:
            issues.append(
                ValidationIssue("negative_start", "Clip start cannot be negative.", clip.id)
            )

        if clip.end_seconds <= clip.start_seconds:
            issues.append(
                ValidationIssue("invalid_range", "Clip range is not positive.", clip.id)
            )

    return issues
