Jeffrey Yeung 
Student Number 20429765
NetID 23ct5
Group 5

| Function                                      | Implementation Status | What's Missing                                                  |
|-----------------------------------------------|-----------------------|-----------------------------------------------------------------|
| Title                                         | Done                  |                                                                 |
| Author                                        | Done                  |                                                                 |
| ISBN                                          | Partial               | Does not check if only digits are inputed                       |
| Total Copies                                  | Done                  |                                                                 |
| Addition Message                              | Done                  |                                                                 |
|-----------------------------------------------|-----------------------|-----------------------------------------------------------------|
| Book ID, Title, Author, ISBN                  | Done                  |                                                                 |
| Available / Total Copies                      | Done                  |                                                                 |
| Actions                                       | Done                  |                                                                 |
|-----------------------------------------------|-----------------------|-----------------------------------------------------------------|
| Accepts Patron ID And Book ID                 | Done                  |                                                                 |
| Validates Patron ID                           | Done                  |                                                                 |
| Book Availability / Patron Limit              | Done                  |                                                                 |
| Create Borrowing Record / Update Availability | Done                  |                                                                 |
| Displays Success / Error Messages             | Done                  |                                                                 |
|-----------------------------------------------|-----------------------|-----------------------------------------------------------------|
| Calulates Late Fees For Overdue Books         | Not Done              |                                                                 |
| Returns JSON With Fee Amount / Days Overdue   | Not Done              |                                                                 |
|-----------------------------------------------|-----------------------|-----------------------------------------------------------------|
| Search Term                                   | Not Done              |                                                                 |
| Search Type                                   | Not Done              |                                                                 |
| Support Partial Matching For Title / Author   | Not Done              |                                                                 |
| Support Exact Matching For ISBN               | Not Done              |                                                                 |
| Return Same Results As Catalog Display        | Not Done              |                                                                 |
|-----------------------------------------------| Not Done              |                                                                 |
| Currently Borrowed Books With Due Dates       | Not Done              |                                                                 |
| Total Late Fees Owed                          | Not Done              |                                                                 |
| Number Of Books Currently Borrrowed           | Not Done              |                                                                 |
| Borrowing History                             | Not Done              |                                                                 |

TESTS

R1:
  - Title length validation (>200 fails, =200 passes)
  - ISBN length/digit validation
  - Positive author input
  - Total copies must be positive
R2:
  - Catalog has at least one book
  - Titles are sorted alphabetically
R3:
  - Successful borrow case
  - Invalid patron ID and invalid book ID cases
  - Borrowing limit (>5) rejection
  - Borrow record presence after borrowing
R4:
  - Invalid patron ID
  - Invalid book ID
  - Reject return when patron hasn’t borrowed the book
R5:
  - No-late-fee scenario: days overdue = 0 → fee = 0
R6:
  - Invalid search type and empty search term return no results
  - Partial title match and exact ISBN match return one result
R7:
  - After borrowing: borrowed list count, zero late fee, and borrowed title appears in report

Assignment Notes:
I had trouble creating some unit tests as concepts such as databases and testing have not been formally taught at Queen's. Specifically I had trouble understanding how to write tests to check "display all books in the catalog in a table format" and "system shall provide an API endpoint GET". I think it was also hard for many other people as these web dev / database concepts are not aligned with what the lectures were covering at all.

I spent an hour with a TA during a help session, however, she was unable to answer many questions citing that she will send a message to the head TA and professor and then get back to me. However, I never got a response back, even after emailing them with a follow up.

Just some feedback.
