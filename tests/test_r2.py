import pytest
import library_service

def test_catalogue_has_books():
    books = library_service.get_all_books()
    assert len(books) >= 1

def test_test_catalogue_sorted_by_title():
    books = library_service.get_all_books()
    titles = [b["title"] for b in books]
    assert titles == sorted(titles)