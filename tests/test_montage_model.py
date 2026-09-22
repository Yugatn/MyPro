from core.montage import Clip, MontageProject, validate_project


def test_project_serializes():
    project = MontageProject(name="First cut")
    project.add_clip(
        Clip(id="clip-001", media_id="shot-001", start_seconds=0, end_seconds=3.5)
    )

    data = project.to_dict()

    assert data["name"] == "First cut"
    assert data["clips"][0]["media_id"] == "shot-001"


def test_invalid_clip_is_reported():
    project = MontageProject()
    project.clips.append(
        Clip(id="bad", media_id="shot", start_seconds=4, end_seconds=2)
    )

    issues = validate_project(project)

    assert any(issue.code == "invalid_range" for issue in issues)
