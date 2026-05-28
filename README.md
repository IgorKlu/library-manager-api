## 📌 Overview
Library Manager API is a backend application for library staff. It handles core library 
workflows like creating books and users, adding physical book copies, borrowing books using `book_id`
and `user_id`, returning book copies, viewing a user's active borrowings and borrowing history.

The application separates routing, validation, business logic and database access.
The project initially started as an in-memory OOP service to test core logic and was later extended
with PostgreSQL database support and FastAPI endpoints.

## ✨ Features

- Create and manage books and library users
- Add physical book copies
- Borrow books using `book_id` and `user_id`
- Return borrowed book copies
- View active borrowings for each user
- View a user's full borrowing history 
- View copies for a book
- View available copies for a book
- Search books by title or author
- Search users by first or last name
- Test business logic and endpoints with isolated test database sessions

## ⚙️ Tech Stack
- Python
- PostgreSQL
- SQLAlchemy
- pytest
- Uvicorn
- Pydantic
- FastAPI TestClient
- GitHub Actions
- psycopg

## 🧱 Architecture
The project is split into separate layers:

- `/app/database/` contains database connection setup
- `/app/db_models/` contains SQLAlchemy ORM models
- `/app/routers/` defines FastAPI endpoints
- `/app/schemas/` defines request and response data structures
- `/app/services/` contains the main business logic
- `/app/utils/` contains small reusable helper functions
- `/app/main.py` creates the FastAPI application and includes routers
- `/app/exceptions.py` contains custom exceptions
- `/tests/` contains service and API tests

##  🧠 Technical Focus

* **Architecture**: Maintainable backend structure with a clear separation between routing, validation, business logic and database access.
* **Data Persistence**: PostgreSQL integration using SQLAlchemy ORM models.
* **Validation**: Request and response validation handled with Pydantic schemas.
* *Testing*: Automated service and API tests using isolated database sessions.
* **Dependency** Management: FastAPI dependency overrides used to replace the standard database session during API tests.

## 🔗 API Endpoints

### Books

| Method | Endpoint                             | Description                          |
|--------|--------------------------------------|--------------------------------------|
| GET    | `/books/`                            | List all books                       |
| POST   | `/books/`                            | Create a book                        |
| GET    | `/books/search/`                     | Search books by title or author      |
| GET    | `/books/{book_id}/`                  | Get book by ID                       |
| DELETE | `/books/{book_id}/`                  | Delete book by ID                    | 
| GET    | `/books/{book_id}/copies/`           | List all copies for a book           |
| POST   | `/books/{book_id}/copies/`           | Add a copy to a book                 |
| GET    | `/books/copies/{copy_id}/`           | Get a book copy by ID                |
| GET    | `/books/{book_id}/copies/available/` | List all available copies for a book |

### Users

| Method | Endpoint                               | Description                        |
|--------|----------------------------------------|------------------------------------|
| GET    | `/users/`                              | List all users                     |
| POST   | `/users/`                              | Create a user                      |
| GET    | `/users/search/`                       | Search users by first or last name |
| GET    | `/users/{user_id}/`                    | Get user by ID                     |
| GET    | `/users/{user_id}/borrowings/active/`  | List active borrowings for a user  |
| GET    | `/users/{user_id}/borrowings/history/` | List borrowing history for a user  |

### Borrowings

| Method | Endpoint              | Description        |
|--------|-----------------------|--------------------|
| POST   | `/borrowings/`        | Borrow a book      |
| POST   | `/borrowings/return/` | Return a book copy | 

## 🧪 Testing

The tests cover service-layer business logic and FastAPI router endpoints. Router tests use
`TestClient`, while database tests use rollback fixtures to keep test data isolated between test
cases.

FastAPI dependency overrides replace the standard `get_db` dependency with a test database
session during API tests.

```bash
python -m pytest
```

## 🚀 Running Locally

### 1. Clone the repository
```bash
git clone https://github.com/IgorKlu/library-manager-api
cd library-manager-api
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt 
```

### 3. Configure environment variables

Create a `.env` file in your project root and add your PostgreSQL database URL:

The project uses the `psycopg` driver, so the URL should start with `postgresql+psycopg://`.

```env
DATABASE_URL=postgresql+psycopg://username:password@host/database_name
```

If your database provider requires a port, include this after the host:

```env
DATABASE_URL=postgresql+psycopg://username:password@host:port/database_name
```

### 4. Run the application

```bash
uvicorn app.main:app --reload
```

Swagger documentation will be available at:

```text
http://127.0.0.1:8000/docs
```
