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


def test_ranges_get_harder_and_overlap():
    ranges = [t.grade_range for t in TagColor]
    for (low_a, high_a), (low_b, high_b) in zip(ranges, ranges[1:], strict=False):
        assert low_a <= low_b and high_a <= high_b
        assert low_b <= high_a  # neighbouring tags share at least one grade
