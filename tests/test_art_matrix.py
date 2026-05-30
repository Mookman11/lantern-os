from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_art_matrix_has_20_panels_and_12_by_3_grid() -> None:
    html = read("apps/lantern-garage/public/art.html")
    css = read("apps/lantern-garage/public/art.css")
    assert html.count('class="art-card') == 20
    assert "20 panels in a 12 x 3 signal matrix" in html
    assert "grid-template-columns: repeat(12" in css
    assert "grid-template-rows: repeat(3" in css


def test_art_matrix_has_left_right_navigation() -> None:
    html = read("apps/lantern-garage/public/art.html")
    js = read("apps/lantern-garage/public/art.js")
    required = [
        'id="prevPanel"',
        'id="nextPanel"',
        "setActivePanel(activeIndex - 1)",
        "setActivePanel(activeIndex + 1)",
        "ArrowLeft",
        "ArrowRight",
    ]
    missing = [phrase for phrase in required if phrase not in html + js]
    assert missing == []


def test_dashboard_links_art_matrix_section() -> None:
    html = read("apps/lantern-garage/public/index.html")
    assert "Art Matrix" in html
    assert "/art.html" in html
