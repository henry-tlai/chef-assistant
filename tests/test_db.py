import db


def test_save_and_list_favorites(temp_db):
    db.save_favorite("Garlic Chicken", "1. Cook it")
    rows = db.list_favorites()
    assert len(rows) == 1        
    assert rows[0][1] == "Garlic Chicken"   


def test_find_favorite_ignores_case(temp_db):
    db.save_favorite("Garlic Herb Steak", "1. Sear it")
    assert len(db.find_favorite("STEAK")) == 1
    assert db.find_favorite("zzz") == []


def test_delete_favorite(temp_db):
    db.save_favorite("Test dish", "1. Do a thing")
    favorite_id = db.list_favorites()[0][0]
    assert db.delete_favorite(favorite_id) is True    
    assert db.delete_favorite(favorite_id) is False    


def test_messages_come_back_in_order(temp_db):
    db.save_messages("s1", ["first", "second", "third"])
    assert db.load_messages("s1") == ["first", "second", "third"]