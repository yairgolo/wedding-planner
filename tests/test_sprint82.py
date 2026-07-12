from pathlib import Path


def test_mobile_navigation_uses_fab_without_bottom_nav():
    html = Path("app/templates/base.html").read_text(encoding="utf-8")
    assert 'class="mobile-fab"' in html
    assert 'class="bottom-nav"' not in html
    assert "data-quick-add-open" in html


def test_sidebar_has_mobile_scroll_support():
    css = Path("app/static/css/app.css").read_text(encoding="utf-8")
    assert "height:100dvh" in css
    assert "overflow-y:auto" in css
    assert "-webkit-overflow-scrolling:touch" in css
    assert "overscroll-behavior:contain" in css
