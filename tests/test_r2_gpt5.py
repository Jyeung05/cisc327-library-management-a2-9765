import library_service as svc

def test_catalog_returns_list_of_dicts(seed_books):
    books = svc.get_all_books()
    assert isinstance(books, list)
    assert books and isinstance(books[0], dict)

def test_catalog_has_required_fields(seed_books):
    required = {"id", "title", "author", "isbn", "total_copies", "available_copies"}
    for b in svc.get_all_books():
        assert required.issubset(b.keys())

def test_catalog_is_sorted_by_title(seed_books):
    titles = [b["title"] for b in svc.get_all_books()]
    assert titles == sorted(titles)

def test_available_within_bounds(seed_books):
    for b in svc.get_all_books():
        assert 0 <= b["available_copies"] <= b["total_copies"]
