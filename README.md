# Library Management System - Flask Web Application with SQLite

## Overview

This project contains a partial implementation of a Flask-based Library Management System with SQLite database, designed for CISC 327 (Software Quality Assurance) coursework.

Students are provided with:

- [`requirements_specification.md`](requirements_specification.md): Complete requirements document with 7 functional requirements (R1-R7)
- [`app.py`](app.py): Main Flask application with application factory pattern
- [`routes/`](routes/): Modular Flask blueprints for different functionalities
  - [`catalog_routes.py`](routes/catalog_routes.py): Book catalog display and management routes
  - [`borrowing_routes.py`](routes/borrowing_routes.py): Book borrowing and return routes
  - [`api_routes.py`](routes/api_routes.py): JSON API endpoints for late fees and search
  - [`search_routes.py`](routes/search_routes.py): Book search functionality routes
- [`database.py`](database.py): Database operations and SQLite functions
- [`library_service.py`](library_service.py): **Business logic functions** (your main testing focus)
- [`templates/`](templates/): HTML templates for the web interface
- [`requirements.txt`](requirements.txt): Python dependencies

## ❗ Known Issues
The implemented functions may contain intentional bugs. Students should discover these through unit testing (to be covered in later assignments).

## Database Schema
**Books Table:**
- `id` (INTEGER PRIMARY KEY)
- `title` (TEXT NOT NULL)
- `author` (TEXT NOT NULL)  
- `isbn` (TEXT UNIQUE NOT NULL)
- `total_copies` (INTEGER NOT NULL)
- `available_copies` (INTEGER NOT NULL)

**Borrow Records Table:**
- `id` (INTEGER PRIMARY KEY)
- `patron_id` (TEXT NOT NULL)
- `book_id` (INTEGER FOREIGN KEY)
- `borrow_date` (TEXT NOT NULL)
- `due_date` (TEXT NOT NULL)
- `return_date` (TEXT NULL)

## Assignment Instructions
See [`student_instructions.md`](student_instructions.md) for complete assignment details.

**Resources for students:**

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Test Driven Development](https://www.datacamp.com/tutorial/test-driven-development-in-python)
- [Pytest framework](https://realpython.com/pytest-python-testing/)
- [Python Blueprint](https://flask.palletsprojects.com/en/stable/blueprints)

## End-to-End browser tests

Browser-based tests live in `tests/test_e2e_playwright.py` and drive a real Chromium session with [Playwright](https://playwright.dev/python/).

1. Install dependencies: `pip install -r requirements.txt`
2. Install browser binaries (first-time only): `python -m playwright install --with-deps`
3. Run the suite: `pytest tests/test_e2e_playwright.py`

The tests automatically launch the Flask app on port `5000`, add a book through the UI, verify it appears in the catalog, and borrow it with a patron ID while checking the success messages.

## Docker usage (Task 2)

The repository now includes a `Dockerfile` to containerize the Flask application.

1. Build the image: `docker build -t library-app .`
2. Run the container: `docker run -p 5000:5000 library-app`
3. Visit the app at [http://localhost:5000](http://localhost:5000).

### Why `docker` is missing locally

`docker` is a system-level tool, not a Python dependency, so it is **not** listed in `requirements.txt`. If your shell reports `docker: command not found` (as on Windows PowerShell), install Docker Desktop first:

1. Download **Docker Desktop for Windows** from <https://docs.docker.com/desktop/install/windows-install/>.
2. Run the installer and enable the recommended WSL 2 option if prompted.
3. After installation, restart PowerShell and verify: `docker --version`.
4. Run the commands above from a directory your user owns (e.g., inside your project folder). If you use WSL, open the project there and run the same commands in the Linux terminal.

If you cannot install Docker on your machine, you can still complete Task 2 by documenting the steps above in your report and running the Flask app natively with `flask run` while noting the Docker limitation.

## Docker Hub walkthrough (Task 3)

Follow these steps to publish and validate the image in Docker Hub:

1. Create/sign in to your Docker Hub account at https://hub.docker.com/.
2. Log in from the terminal: `docker login` (enter your Hub username/password when prompted).
3. Tag the local image so it targets your repository: `docker tag library-app YOUR_DOCKERHUB_USERNAME/library-app:v1`
4. Push the image: `docker push YOUR_DOCKERHUB_USERNAME/library-app:v1`
5. Remove the local copy to prove reproducibility: `docker rmi YOUR_DOCKERHUB_USERNAME/library-app:v1`
6. Pull it back from Docker Hub: `docker pull YOUR_DOCKERHUB_USERNAME/library-app:v1`
7. Run from the pulled image: `docker run -p 5000:5000 YOUR_DOCKERHUB_USERNAME/library-app:v1`
8. Capture screenshots of the push, removal, pull, and run commands succeeding for your submission report.


