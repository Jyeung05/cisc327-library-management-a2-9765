import library_service as svc
import database as db

def test_search_invalid_type_returns_empty(seed_books):
    assert svc.search_books_in_catalog("Brave", "genre") == []

def test_search_empty_term_returns_empty(seed_books):
    assert svc.search_books_in_catalog("", "title") == []

def test_search_partial_title_case_insensitive(seed_books):
    res = svc.search_books_in_catalog("brave", "title")
    assert len(res) == 1
    assert res[0]["title"] == "Brave New World"

def test_search_partial_author_case_insensitive(seed_books):
    res = svc.search_books_in_catalog("dickens", "author")
    assert len(res) == 1
    assert res[0]["author"] == "Charles Dickens"

def test_search_exact_isbn(seed_books):
    isbn = "3333333333333"  # Catch-22
    res = svc.search_books_in_catalog(isbn, "isbn")
    assert len(res) == 1
    assert res[0]["isbn"] == isbn
