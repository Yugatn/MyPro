from core.render.specification import RenderSpecification

def test_render_specification_is_deterministic():
    a = RenderSpecification("tl", "out.mp4")
    b = RenderSpecification("tl", "out.mp4")
    assert a.to_dict() == b.to_dict()
    assert a.spec_hash == b.spec_hash
