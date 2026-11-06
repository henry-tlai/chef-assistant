import tools


def test_get_favorite_no_match(temp_db):
    result = tools.get_favorite("pizza")
    assert "No favorite found" in result


def test_get_favorite_multiple_matches(temp_db):
    tools.save_favorite("Chicken Soup", "1. Boil")
    tools.save_favorite("Chicken Curry", "1. Simmer")
    result = tools.get_favorite("chicken")
    assert "Several favorites match:" in result             


def test_get_favorite_single_match(temp_db):
    tools.save_favorite("Garlic Herb Steak", "1. Sear it")
    result = tools.get_favorite("steak")
    assert "Several favorites match" in result               