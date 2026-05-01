# Flask Admin Portal Backend

A production-ready Flask backend for an admin opportunity portal with PostgreSQL, JWT authentication, and modular service structure.

## Features

- Admin auth: signup, login, forgot password, reset password
- Opportunity CRUD: create, read, update, delete
- JWT-secured endpoints
- Centralized error handling
- Input validation and password strength enforcement
- Request logging and error logging
- Pagination support for opportunity listing
- Simple API documentation route `/docs`

## Tech Stack

- Python
- Flask
- PostgreSQL
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- Flask-Bcrypt

## Project Structure

- `app.py` — Flask app factory and route registration
- `config.py` — environment-based application configuration
- `extensions.py` — initialized Flask extensions
- `models/` — database models for `Admin` and `Opportunity`
- `routes/` — API blueprints for auth and opportunity workflows
- `services/` — business logic and persistence operations
- `utils/` — validators, custom exceptions, logging, and error handlers
- `tests/` — integration tests for API workflows

## Environment Variables

Copy `.env.example` or update `.env` with:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=certifyme
DB_USER=postgres
DB_PASSWORD=your_db_password
JWT_SECRET_KEY=your-secret-key-with-32+chars
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=60
```

> Ensure `JWT_SECRET_KEY` is strong and never checked into version control.

## Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Database setup

```powershell
psql -U postgres -c "CREATE DATABASE certifyme;"
$Env:FLASK_APP = "app:create_app"
flask db init
flask db migrate -m "initial"
flask db upgrade
```

### Run the server

```powershell
python app.py
```

## API Endpoints

### Health & docs

- `GET /` — health check
- `GET /docs` — API documentation

### Authentication

- `POST /auth/signup`
  - body: `full_name`, `email`, `password`, `confirm_password`
- `POST /auth/login`
  - body: `email`, `password`, `remember_me`
- `POST /auth/forgot-password`
  - body: `email`
- `POST /auth/reset-password`
  - body: `token`, `new_password`, `confirm_password`

### Opportunities

- `GET /opportunities?page=1&limit=10`
- `POST /opportunities`
- `GET /opportunities/<id>`
- `PUT /opportunities/<id>`
- `DELETE /opportunities/<id>`

## Pagination

`GET /opportunities?page=1&limit=10`

Response format:

```json
{
  "page": 1,
  "limit": 10,
  "total": 25,
  "data": [ ... ]
}
```

## Testing

### Run tests

```powershell
python -m unittest discover -s tests
```

### Manual test checklist

1. Run server: `python app.py`
2. Signup
3. Login
4. Forgot password
5. Reset password
6. Create opportunity
7. Get all opportunities
8. Get single opportunity
9. Update opportunity
10. Delete opportunity
11. Pagination: `GET /opportunities?page=1&limit=2`
12. Error cases: invalid token, missing fields, wrong input format
13. Database verification: `admins` and `opportunities` tables exist and relation works

## Notes

- Use the `Authorization: Bearer <token>` header for protected routes.
- Validation and errors return consistent JSON responses.
- Logs are written to `logs/app.log`.
