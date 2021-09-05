from woshi.wiki import get_table_df


def test_get_page() -> None:
    """Test getting page."""
    df = get_table_df()
    print("CANADIAN ELECTION DATAFRAME:\n")
    print(df)
    print("\nFIN.")
