"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books, get_db_connection
)
def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

# --------- Helper: Late-fee policy (pure) ----------
def _fee_for_days(days_overdue: int) -> float:
    """R5 policy: $0.50/day for first 7 days, $1.00/day after, cap $15."""
    if days_overdue <= 0:
        return 0.00
    first7 = min(days_overdue, 7)
    rest = max(days_overdue - 7, 0)
    fee = first7 * 0.50 + rest * 1.00
    return min(fee, 15.00)

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Implements R4: Accepts patron ID & book ID, verifies active borrow,
    records return date, updates availability, and reports late fee.
    """
    # Validate patron ID format
    if not (isinstance(patron_id, str) and patron_id.isdigit() and len(patron_id) == 6):
        return False, "Invalid patron ID. Must be exactly 6 digits."

    # Validate book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    # Verify patron currently has this book borrowed
    active = get_patron_borrowed_books(patron_id)
    match = next((r for r in active if r["book_id"] == book_id), None)
    if not match:
        return False, "No active borrow record for this patron and book."

    now = datetime.now()
    # Compute fee BEFORE closing the record (we have due_date here)
    due_date = match["due_date"]
    days_overdue = max(0, (now - due_date).days)
    fee_amount = _fee_for_days(days_overdue)

    # 1) Set return date
    if not update_borrow_record_return_date(patron_id, book_id, now):
        return False, "Database error occurred while updating return record."

    # 2) Increment availability (avoid exceeding total)
    if book["available_copies"] < book["total_copies"]:
        if not update_book_availability(book_id, +1):
            return False, "Database error occurred while updating book availability."

    # Success message with fee
    fee_str = f"${fee_amount:.2f}"
    if days_overdue > 0:
        return True, f'Returned "{book["title"]}". Overdue by {days_overdue} day(s). Late fee: {fee_str}.'
    else:
        return True, f'Returned "{book["title"]}". No late fee (0.00).'


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Implements R5. Computes fee for an active borrow; if none, computes
    fee based on most-recent historical borrow (using return_date).
    Returns: {'fee_amount': float, 'days_overdue': int, 'status': str}
    """
    now = datetime.now()

    # Try active borrow first
    active = get_patron_borrowed_books(patron_id)
    for r in active:
        if r["book_id"] == book_id:
            days_overdue = max(0, (now - r["due_date"]).days)
            return {
                "fee_amount": round(_fee_for_days(days_overdue), 2),
                "days_overdue": days_overdue,
                "status": "ok-active",
            }

    # Fallback: look up most recent borrow record (historical)
    try:
        conn = get_db_connection()
        row = conn.execute(
            """
            SELECT borrow_date, due_date, return_date
            FROM borrow_records
            WHERE patron_id = ? AND book_id = ?
            ORDER BY borrow_date DESC
            LIMIT 1
            """,
            (patron_id, book_id),
        ).fetchone()
        conn.close()
    except Exception:
        row = None

    if not row:
        return {"fee_amount": 0.00, "days_overdue": 0, "status": "no-record"}

    due = datetime.fromisoformat(row["due_date"])
    if row["return_date"]:
        returned = datetime.fromisoformat(row["return_date"])
        days_overdue = max(0, (returned - due).days)
        status = "ok-closed"
    else:
        # Unlikely (would have shown up as active), but handle gracefully
        days_overdue = max(0, (now - due).days)
        status = "ok-ambiguous"

    return {
        "fee_amount": round(_fee_for_days(days_overdue), 2),
        "days_overdue": days_overdue,
        "status": status,
    }

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Implements R6. type ∈ {'title','author','isbn'}.
    - title/author: partial, case-insensitive
    - isbn: exact match
    Returns a list of book dicts shaped like catalog rows.
    """
    if not search_type or search_type not in {"title", "author", "isbn"}:
        return []
    if not search_term or not search_term.strip():
        return []

    term = search_term.strip()
    books = get_all_books()

    if search_type == "isbn":
        return [b for b in books if str(b.get("isbn", "")).strip() == term]

    # Partial, case-insensitive for title/author
    term_lower = term.lower()
    key = "title" if search_type == "title" else "author"
    return [b for b in books if term_lower in str(b.get(key, "")).lower()]


def get_patron_status_report(patron_id: str) -> Dict:
    """
    Implements R7: report includes
      - currently borrowed (with due dates)
      - number of books currently borrowed
      - total late fees owed (sum over active borrows)
      - borrowing history (all past borrows with return dates)
    """
    # Basic validation (keep consistent with other functions)
    if not (isinstance(patron_id, str) and patron_id.isdigit() and len(patron_id) == 6):
        return {"status": "error", "message": "Invalid patron ID. Must be exactly 6 digits."}

    # Current borrows
    current = get_patron_borrowed_books(patron_id)
    now = datetime.now()

    # Enrich current borrows with overdue + fee
    current_items = []
    total_fees = 0.0
    for r in current:
        due = r["due_date"]
        days_overdue = max(0, (now - due).days)
        fee = _fee_for_days(days_overdue)
        total_fees += fee
        current_items.append({
            "book_id": r["book_id"],
            "title": r["title"],
            "author": r["author"],
            "borrow_date": r["borrow_date"].isoformat(),
            "due_date": r["due_date"].isoformat(),
            "days_overdue": days_overdue,
            "late_fee": round(fee, 2),
        })

    # History (all records for patron)
    history: List[Dict] = []
    try:
        conn = get_db_connection()
        rows = conn.execute(
            """
            SELECT br.book_id, br.borrow_date, br.due_date, br.return_date,
                   b.title, b.author
            FROM borrow_records br
            JOIN books b ON b.id = br.book_id
            WHERE br.patron_id = ?
            ORDER BY br.borrow_date DESC
            """,
            (patron_id,),
        ).fetchall()
        conn.close()

        for row in rows:
            borrow_date = datetime.fromisoformat(row["borrow_date"])
            due_date = datetime.fromisoformat(row["due_date"])
            return_date = datetime.fromisoformat(row["return_date"]) if row["return_date"] else None
            # Fee at return time (or as of now if still out)
            basis_time = return_date or now
            days_overdue = max(0, (basis_time - due_date).days)
            history.append({
                "book_id": row["book_id"],
                "title": row["title"],
                "author": row["author"],
                "borrow_date": borrow_date.isoformat(),
                "due_date": due_date.isoformat(),
                "return_date": return_date.isoformat() if return_date else None,
                "days_overdue": days_overdue,
                "late_fee": round(_fee_for_days(days_overdue), 2),
            })
    except Exception:
        # If anything goes wrong, still return the core info
        history = []

    return {
        "status": "ok",
        "patron_id": patron_id,
        "current_borrow_count": len(current_items),
        "total_late_fees": round(total_fees, 2),
        "currently_borrowed": current_items,
        "history": history,
    }