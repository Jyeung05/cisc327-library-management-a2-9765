"""End-to-end browser tests using Playwright.

These tests launch the Flask server and drive a real browser session to
validate user workflows for adding and borrowing books.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import uuid
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

APP_URL = "http://127.0.0.1:5000"


def _wait_for_server(url: str, timeout: float = 15) -> None:
    """Poll the given URL until it becomes reachable or timeout expires."""
    start = time.time()
    last_error: Exception | None = None

    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url):
                return
        except Exception as exc:  # noqa: BLE001 - broad to keep retrying until ready
            last_error = exc
            time.sleep(0.5)
    raise RuntimeError(f"Server did not become ready: {last_error}")


@pytest.fixture(scope="session", autouse=True)
def start_app_server():
    """Start the Flask development server for the duration of the test session."""
    db_path = Path("library.db")
    if db_path.exists():
        db_path.unlink()

    env = os.environ.copy()
    env["FLASK_ENV"] = "testing"

    process = subprocess.Popen(
        [sys.executable, "app.py"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    try:
        _wait_for_server(f"{APP_URL}/catalog")
        yield
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


@pytest.fixture(scope="session")
def browser() -> Browser:
    """Launch a single Chromium browser instance for all tests."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture()
def page(browser: Browser) -> Page:
    """Create a fresh page for each test to keep state isolated."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


def test_add_book_is_listed(page: Page):
    """Add a new book through the UI and verify it appears in the catalog."""
    unique_title = f"Test Book {uuid.uuid4().hex[:6]}"
    unique_isbn = f"978{uuid.uuid4().int % 10**10:010d}"

    page.goto(APP_URL)
    page.get_by_role("link", name="➕ Add Book").click()

    page.fill("input#title", unique_title)
    page.fill("input#author", "E2E Tester")
    page.fill("input#isbn", unique_isbn)
    page.fill("input#total_copies", "3")

    page.get_by_role("button", name="Add Book to Catalog").click()
    page.wait_for_url(f"{APP_URL}/catalog")

    success_flash = page.get_by_text(f"Book \"{unique_title}\" has been successfully added")
    assert success_flash.is_visible()

    matching_rows = page.locator("tbody tr", has_text=unique_title)
    assert matching_rows.count() >= 1
    assert matching_rows.nth(0).locator("td", has_text=unique_isbn).is_visible()


def test_borrow_book_flow(page: Page):
    """Borrow the most recently added book and confirm the success message."""
    page.goto(f"{APP_URL}/catalog")

    newest_row = page.locator("tbody tr").last
    title_text = newest_row.locator("td").nth(1).inner_text()

    newest_row.locator("input[name='patron_id']").fill("777888")
    newest_row.get_by_role("button", name="Borrow").click()
    page.wait_for_url(f"{APP_URL}/catalog")

    confirmation = page.get_by_text(f"Successfully borrowed \"{title_text}\"")
    assert confirmation.is_visible()

    availability_text = newest_row.locator("td").nth(4).inner_text()
    assert "Available" in availability_text or "Not Available" in availability_text
