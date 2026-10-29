from core.models import Climb, Section


def section_rows(sections: list[Section], climbs: list[Climb]) -> list[tuple[str, str]]:
    """(title, subtitle) per section, ordered by section number."""
    counts: dict[str, int] = {}
    for climb in climbs:
        counts[climb.section_id] = counts.get(climb.section_id, 0) + 1
    rows = []
    for section in sorted(sections, key=lambda s: s.number):
        n = counts.get(section.id, 0)
        rows.append((section.name, f"{n} climb{'s' if n != 1 else ''}"))
    return rows
