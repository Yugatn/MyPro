from core.media import MediaFile, MediaManifest


def test_manifest_rejects_duplicate_ids():
    manifest = MediaManifest()
    manifest.add(MediaFile(id="shot-001", path="video.mov"))

    try:
        manifest.add(MediaFile(id="shot-001", path="other.mov"))
    except ValueError as exc:
        assert "Duplicate media id" in str(exc)
    else:
        raise AssertionError("Expected duplicate media id to fail")
