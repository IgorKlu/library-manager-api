# Library Manager API

A backend project built with Python and FastAPI.

## Features

- Find user by ID and name
- Create and list users
- Create and list books
- Create multiple copies for each book
- Show all copies for each book
- Show all copies for selected book
- Borrow an available book copy
- Return a borrowed book copy
- Delete book only if none of its copies are borrowed
- Custom domain exceptions
- Service tests with pytest

## Tech stack

- FastAPI
- Pydantic
- uvicorn
- uuid6
- pytest

## How to run

Install dependencies:
```
pip install -r requirements.txt
```

Run the API:
```
uvicorn app.main:app --reload
```

Open API docs:
```
http://127.0.0.1:8000/docs
```

Run tests:
```
python -m pytest
```

## Main API Endpoints

### Books

| Method | Endpoint | Description |
|---|---|---|
| GET | `/books/` | List all books |
| POST | `/books/` | Create a new book with copies |
| GET | `/books/{book_id}/copies` | List all copies of a book |
| DELETE | `/books/{book_id}` | Delete a book and its copies if none are borrowed |

### Users

| Method | Endpoint | Description                        |
|---|---|------------------------------------|
| GET | `/users/` | List all users                     |
| POST | `/users/` | Create a new user                  |
| POST | `/users/{user_id}/borrowed-books` | Borrow an available copy of a book |
| DELETE | `/users/{user_id}/borrowed-books/{book_copy_id}` | Return a borrowed book copy        |
| GET | `/users/{user_id}/borrowed-copy-ids` | List borrowed copy IDs for a user  |
| GET | `/users/search?name=...` | Search users by name               |
| GET | `/users/{user_id}` | Get users by ID                    |


## Current Limitations

- Data is stored in memory and disappears after restarting the server.
- There is no database integration yet.
- Borrowed books are currently returned as borrowed copy IDs.

## Next steps
- Add PostgreSQL + SQLAlchemy