# Flask User Management (JWT + Bootstrap)

Modern Flask user-management sample with:
- PostgreSQL via SQLAlchemy
- Alembic (Flask-Migrate) for DB migrations
- JWT access cookies (flask-jwt-extended)
- Bcrypt password hashing
- Clean Bootstrap templates (shared header/footer, hero home page, dashboard, users table)

## Routes (final set)

**Public pages**
- `GET /` — landing page (hero + auth-aware buttons)
- `GET/POST /auth/register` — register a new user
- `GET/POST /auth/login` — login with email + password (sets JWT cookie)
- `GET/POST /auth/reactivate` — 2-step reactivation (email step + password step)

**Authenticated (JWT cookie required)**
- `GET /auth/dashboard` — current user dashboard
- `GET/POST /auth/logout` — clear auth cookie and redirect to login
- `GET /auth/check` — tiny JSON helper for header to know if user is logged in
- `GET /users/list` — HTML table of all users (supports status/sort query params)
- `POST /users/` — create a user over JSON API
- `PATCH /users/<id>` — update current user over JSON API
- `DELETE /users/<id>` — soft-delete (deactivate) current user over JSON API

User schema (core fields):
- id, name, email, dob, password_hash,
- is_active, last_login_datetime, created_at, updated_at

## Project layout

```text
flask_user_app/
├─ app.py                  # FLASK_APP entry point (uses app:create_app)
├─ requirements.txt        # Python dependencies
├─ .env, .env.example      # Environment variables for local dev
├─ .flaskenv               # Flask CLI config (FLASK_APP, FLASK_ENV)
├─ README.md               # This file (project overview + curl examples)
├─ example_README.md       # Older, more verbose example README (reference only)
├─ postman_collection.json # Postman collection for all auth/user endpoints
├─ migrations/             # Alembic migration scripts (Flask-Migrate)
├─ myenv/                  # Local virtualenv (should not be committed)
└─ app/
   ├─ __init__.py          # create_app(), blueprint registration, JWT error handlers
   ├─ config.py            # Config class (reads DATABASE_URL, JWT_SECRET_KEY, etc.)
   ├─ extensions.py        # db, migrate, bcrypt, jwt instances
   ├─ models/
   │  └─ user.py           # User model (id, name, email, dob, is_active, timestamps, ...)
   ├─ auth/
   │  └─ routes.py         # /auth/login, /auth/register, /auth/dashboard, /auth/logout, /auth/reactivate, /auth/check
   ├─ users/
   │  ├─ routes.py         # /users/list + JSON API routes (create/update/delete/deactivate)
   │  └─ services.py       # User CRUD helpers, soft delete, profile update logic
   ├─ templates/
   │  ├─ base.html         # Global shell, header/footer, toast container
   │  ├─ header.html       # Navbar, toggles links using /auth/check
   │  ├─ footer.html       # Footer bar
   │  ├─ home.html         # Landing page with banner image + auth-aware buttons
   │  ├─ login.html        # Login form (toast errors + password eye toggle)
   │  ├─ register.html     # Registration form (client-side password checks + eye toggle)
   │  ├─ dashboard.html    # Dashboard (status, member since, last login, quick links)
   │  ├─ reactivate.html   # Unified email + password reactivation flow
   │  └─ users/
   │     ├─ list.html      # Users table (created/updated/last-login + filters/sorting)
   │     ├─ edit_auth.html # Password gate before editing profile
   │     └─ edit.html      # AJAX profile edit form (name/dob/password)
   └─ static/
      ├─ css/
      │  └─ style.css          # Layout, hero, tables, navbar/footer, button styles
      ├─ js/
      │  ├─ create_user.js     # (Optional) helper for creating users via API
      │  ├─ dashboard.js       # (Legacy) dashboard data helper, not used in final flow
      │  ├─ delete_user.js     # Calls DELETE /users/<id> and reloads
      │  ├─ login.js           # (Optional) client-side helpers for login flows
      │  ├─ register.js        # (Optional) client-side helpers for register flows
      │  ├─ toasts_and_password.js # Toasts for flash() + password eye toggles (used globally)
      │  └─ update_user.js     # (Optional) client-side helpers for updating users
      └─ images/
         └─ fcbflag.jpg        # Banner image used on home page
```

## 1) Setup environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
```

Create `.env` in the project root (adjust values):

```env
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=postgresql://postgres:password@localhost:5432/CRUD_USER_APP
JWT_SECRET_KEY=jwt-secret-key-change-in-production
ACCESSTOKEN_LIFETIME=10m
```

## 2) Initialize DB (migrations)

```bash
flask db upgrade
```

This will create the `users` table and any other schema managed by Alembic.

## 3) Run the app

With `.flaskenv` pointing at the app factory you can simply run:

```bash
flask run
```

App will be available at `http://127.0.0.1:5000/`.

## 4) Postman collection

A complete Postman collection is tracked at the project root:

- `postman_collection.json`

Usage:
- Import into Postman
- Set `baseUrl` to `http://127.0.0.1:5000`
- Adjust `userId` and `reactivateEmail` variables
- Use **Auth** folder for login/register/dashboard/reactivation
- Use **Users** folder for list/create/update/delete

## 5) curl examples

Base URL (dev):

```bash
BASE_URL="http://127.0.0.1:5000"
```

> Note: authenticated routes rely on an HTTP-only cookie set by `/auth/login`. Below we show cookie jar usage with `curl`.

### Auth

**Register**

```bash
curl -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=Test User" \
  -d "email=test@example.com" \
  -d "password=Test@1234"
```

**Login (store cookie)**

```bash
curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@example.com" \
  -d "password=Test@1234" \
  -c cookies.txt
```

**Dashboard (HTML, requires cookie)**

```bash
curl "$BASE_URL/auth/dashboard" -b cookies.txt
```

**Logout**

```bash
curl -X POST "$BASE_URL/auth/logout" -b cookies.txt -c cookies.txt
```

**Auth check JSON**

```bash
curl "$BASE_URL/auth/check" -b cookies.txt
```

### Reactivation (single endpoint)

**Step 1 – Submit email (form style)**

```bash
curl -X POST "$BASE_URL/auth/reactivate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@example.com"
```

If the account exists and is **inactive**, the browser will be redirected to `/auth/reactivate?email=...` to show the password form.

**Step 2 – Submit password for that email**

```bash
curl -X POST "$BASE_URL/auth/reactivate?email=test@example.com" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "password=Test@1234"
```

### Users JSON API

> All the following require a valid JWT cookie (login first and reuse `cookies.txt`).

**List users (HTML)**

```bash
# Default: all users, sorted by id asc
curl "$BASE_URL/users/list" -b cookies.txt

# Example: only active users, sorted by last_login desc
curl "$BASE_URL/users/list?status=active&sort_by=last_login&order=desc" -b cookies.txt
```

**Create user via API**

```bash
curl -X POST "$BASE_URL/users/" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "API User",
    "email": "apiuser@example.com",
    "password": "Api@1234",
    "dob": "2000-01-01"
  }'
```

**Update current user (example: id = 1)**

```bash
curl -X PATCH "$BASE_URL/users/1" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "Updated Name",
    "dob": "1999-12-31"
  }'
```

**Soft-delete (deactivate) current user**

```bash
curl -X DELETE "$BASE_URL/users/1" -b cookies.txt
```

## Notes

- JWT is stored as an HTTP-only cookie; only authenticated routes may be accessed after login.
- User deactivation is a soft delete (`is_active = False`).
- Reactivation requires the correct password; already-active accounts are redirected back to login with a helpful message.
