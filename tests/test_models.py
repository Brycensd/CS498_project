from core.models import TAG_GRADE_RANGES, TagColor


def test_tags_in_gym_order():
    assert [t.value for t in TagColor] == [
        "Red",
        "Yellow",
        "Green",
        "White",
        "Blue",
        "Black",
        "Purple",
        "Orange",
        "Pink",
    ]


def test_every_tag_has_a_range():
    assert set(TAG_GRADE_RANGES) == set(TagColor)


def test_known_ranges_and_labels():
    assert TagColor.RED.grade_range == (0, 0)
    assert TagColor.RED.range_label == "V0"
    assert TagColor.YELLOW.grade_range == (0, 2)
    assert TagColor.GREEN.grade_range == (1, 3)
    assert TagColor.GREEN.range_label == "V1–V3"
    assert TagColor.PINK.grade_range == (8, None)
    assert TagColor.PINK.range_label == "V8+"


def test_covers():
    assert TagColor.RED.covers(0)
    assert not TagColor.RED.covers(1)
    assert TagColor.GREEN.covers(1) and TagColor.GREEN.covers(3)
    assert not TagColor.GREEN.covers(0) and not TagColor.GREEN.covers(4)
    assert TagColor.PINK.covers(8) and TagColor.PINK.covers(15)
    assert not TagColor.PINK.covers(7)


def test_ranges_get_harder_and_overlap():
    tags = list(TagColor)
    for easier, harder in zip(tags, tags[1:], strict=False):
        low_a, high_a = easier.grade_range
        low_b, _ = harder.grade_range
        assert high_a is not None, "only the hardest tag may be open-ended"
        assert low_a <= low_b
        assert low_b <= high_a  # neighbouring tags share at least one grade
