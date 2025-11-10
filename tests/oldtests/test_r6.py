import pytest
import library_service

def test_check_for_proper_search_type():
    dictionary = library_service.search_books_in_catalog("abc", "wagagaoemjgo")
    assert len(dictionary) == 0
    

def test_search_term_is_not_empty():
    dictionary = library_service.search_books_in_catalog("", "author")
    assert len(dictionary) == 0
    
def test_support_partial_matching():
    dictionary = library_service.search_books_in_catalog("Kill", "title")
    assert len(dictionary) == 1

def test_search_exact_isbn():
    dictionary = library_service.search_books_in_catalog("9780743273565", "isbn")
    assert len(dictionary) == 1