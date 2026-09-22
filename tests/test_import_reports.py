from core.import_layer.reports import LossEntry, LossReport


def test_loss_report_is_explicit():
    report = LossReport((LossEntry("effects:c1", "major", "not mapped"),))
    assert not report.has_critical()
    assert report.as_dict()["entries"][0]["severity"] == "major"
