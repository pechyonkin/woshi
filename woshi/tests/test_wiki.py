from woshi.wiki import get_page


def test_get_page() -> None:
    """Test getting page."""
    print("TEST! " * 21 + "\n\n")
    res = get_page()
    print("\n\nEND.")
