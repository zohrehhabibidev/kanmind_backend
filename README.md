# KanMind Backend

## Description

KanMind is a collaborative Kanban task management application. This backend provides a Django REST Framework API for user registration and login, boards and membership, tasks with assignees and reviewers, and task comments. Django Admin provides a separate interface for managing users, boards, tasks, comments, and authentication tokens.

The backend runs independently. No frontend installation is required.

## Requirements

- Python 3.12 or later, with `pip` and the `venv` module available. The installed Django package declares Python >=3.12; the existing development environment uses Python 3.14.6. Other Python versions have not been tested for this README.
- Git, to clone the repository.
- A terminal: PowerShell on Windows, or a shell such as Bash on macOS/Linux.
- Internet access to clone the repository and install dependencies.
- Write access to the project directory for the local SQLite database.

The exact dependency versions are defined in `requirements.txt`: Django 6.1.1, Django REST Framework 3.18.1, python-dotenv 1.2.4, asgiref 3.12.1, sqlparse 0.6.0, and tzdata 2026.5. Install them using that file. No separate database server is required.

## Installation

Follow the sections below in order. Run all commands after cloning from the repository root, which contains `manage.py` and `requirements.txt`.

### Windows

Open PowerShell:

```powershell
git clone https://github.com/zohrehhabibidev/kanmind_backend.git
cd kanmind_backend
py --version
```

Ensure that the selected Python interpreter meets the requirement above. If the `py` launcher is unavailable, use `python` instead after checking `python --version`.

### macOS / Linux

```bash
git clone https://github.com/zohrehhabibidev/kanmind_backend.git
cd kanmind_backend
python3 --version
```

Ensure that `python3` meets the requirement above. Some Linux distributions provide `pip` and `venv` as separate system packages; install the packages for your selected Python version if they are missing.

## Create Virtual Environment

Create an isolated environment for the backend dependencies.

Windows (PowerShell):

```powershell
py -m venv .venv
```

macOS / Linux:

```bash
python3 -m venv .venv
```

## Activate Virtual Environment

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script and your device policy permits it, allow scripts for the current terminal session, then retry activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Alternatively, use `.\.venv\Scripts\python.exe` in place of `python` in the remaining commands; activation is not required when invoking that interpreter directly.

macOS / Linux (Bash/Zsh):

```bash
source .venv/bin/activate
```

After activation, `python` and `python -m pip` refer to the virtual environment. Activate it again whenever you open a new terminal. Use `deactivate` to leave it.

## Install Dependencies

With the virtual environment active:

```text
python -m pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file beside `manage.py` using the tracked `.env.example` template.

Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

For an existing checkout, preserve any existing `.env` instead of overwriting it. Edit `.env` in a text editor:

```dotenv
SECRET_KEY=replace-with-a-unique-generated-secret
DEBUG=True
```

Generate a new secret locally using the active virtual environment:

```text
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the generated value into `.env`, enclosing it in single quotes so characters such as `#` are preserved: `SECRET_KEY='<generated-value>'`. Replace the placeholder; do not publish the generated value.

| Variable | Configuration and behavior |
| --- | --- |
| `SECRET_KEY` | Required, nonempty Django signing key. Read with `os.getenv("SECRET_KEY")`; there is no fallback value. |
| `DEBUG` | Set to exactly `True` for this local development setup. Only the case-sensitive string `True` enables debug mode; missing or other values result in `False`. |

`core/settings.py` loads variables with `python-dotenv` using `load_dotenv()`. Existing process environment variables take precedence over `.env`, so check them if your settings differ from the file.

`ALLOWED_HOSTS` is hardcoded to an empty list. With `DEBUG=True`, Django permits local development hosts such as `localhost` and `127.0.0.1`. Setting `DEBUG=False` alone does not provide a working production configuration. `ALLOWED_HOSTS` is not read from `.env`.

No database credentials, database URL, email credentials, or other environment variables are required by the current settings. `.env` is ignored by Git; `.env.example` contains placeholders only.

## Run Migrations

With `.env` configured and the virtual environment active:

```text
python manage.py migrate
```

This initializes SQLite at `db.sqlite3` in the repository root and applies the committed application migrations and Django migrations, including authentication tokens, Admin, and sessions. The application migrations are in `auth_app/migrations/` and `kanban_app/migrations/`. There is no need to run `makemigrations` for a fresh checkout.

The database file is local and ignored by Git. Preserve it if it already contains development data. No fixture import or seed command is required to start the backend.

## Create Superuser

```text
python manage.py createsuperuser
```

Follow the prompts for an email address, full name, and password. The custom user model uses a unique email address as its login identifier and has no username field. Use your chosen email and password to sign in to Django Admin. There are no preconfigured administrator credentials.

## Start Development Server

```text
python manage.py runserver
```

The default local server listens at `http://127.0.0.1:8000/`.

- Django Admin: `http://127.0.0.1:8000/admin/`
- Login API: `http://127.0.0.1:8000/api/login/` (POST)
- Registration API: `http://127.0.0.1:8000/api/registration/` (POST)
- Boards API: `http://127.0.0.1:8000/api/boards/` (requires an API token)

There is no application homepage at `/` and no API index at `/api/`; use the routes listed below. Opening a URL in a browser sends a GET request, which does not perform registration or login. Use an API client to send the required methods and headers. Stop the server with `Ctrl+C`.

## Project Structure

```text
kanmind_backend/
|-- manage.py
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- core/                   # Settings, central URLs, ASGI and WSGI entry points
|-- auth_app/               # Custom email-based user model, forms and Admin
|   |-- api/                # Registration/login views, serializers and URLs
|   `-- migrations/         # Committed user-model migration
|-- kanban_app/             # Board, Task and Comment models and Admin
|   |-- api/                # Views, serializers, permissions and URLs
|   `-- migrations/         # Committed board/task/comment migration
`-- docs/                   # Model and business requirements analysis
```

The setup creates `.venv/`, `.env`, and `db.sqlite3` locally. These are excluded from version control.

## Authentication

The API uses DRF `TokenAuthentication` with `rest_framework.authtoken`, rather than JWT. Registration and login allow unauthenticated requests. Other API endpoints listed below require authentication.

Send JSON with `Content-Type: application/json`:

- `POST /api/registration/`: supply `fullname`, `email`, `password`, and `repeated_password`.
- `POST /api/login/`: supply `email` and `password`.

Successful registration (201) and login (200) return `token`, `fullname`, `email`, and `user_id`. Use the returned token for subsequent API requests:

```http
Authorization: Token <your-token>
```

For example, send `GET http://127.0.0.1:8000/api/boards/` with this header to access the boards API. The result contains only boards owned by or associated with the authenticated user; a new account may receive an empty list.

Django Admin uses its own session login. Signing in to Admin does not authenticate API requests: obtain a token through the login endpoint and send it explicitly. A superuser can also use the login API with their email and password; API object permissions still apply.

## API Endpoints

The following overview was checked against the official **API Endpoint Dokumentation.pdf** and the application's URL configuration. The course PDF is supplied separately and is not included in this repository. All paths below include the required trailing slash. Replace IDs in braces with existing integer IDs.

All rows except registration and login require a token. Additional access rules are shown per endpoint.

| Method | Endpoint | Purpose and access |
| --- | --- | --- |
| POST | `/api/registration/` | Register a user; no authentication required. |
| POST | `/api/login/` | Obtain an authentication token; no authentication required. |
| GET | `/api/boards/` | List boards owned by or associated with the current user. |
| POST | `/api/boards/` | Create a board; authenticated user becomes its owner. |
| GET | `/api/boards/{board_id}/` | Retrieve board details and tasks; board owner or member. |
| PATCH | `/api/boards/{board_id}/` | Update title/membership; board owner or member. |
| DELETE | `/api/boards/{board_id}/` | Delete a board and its tasks/comments; board owner only. |
| GET | `/api/email-check/?email=<email>` | Look up a registered user by email; authenticated user. |
| GET | `/api/tasks/assigned-to-me/` | List tasks assigned to the current user as assignee. |
| GET | `/api/tasks/reviewing/` | List tasks with the current user as reviewer. |
| POST | `/api/tasks/` | Create a task within a board; board member. |
| PATCH | `/api/tasks/{task_id}/` | Update a task; member of its board. |
| DELETE | `/api/tasks/{task_id}/` | Delete a task; task creator or board owner. |
| GET | `/api/tasks/{task_id}/comments/` | List comments chronologically; member of the task's board. |
| POST | `/api/tasks/{task_id}/comments/` | Add a comment; member of the task's board. |
| DELETE | `/api/tasks/{task_id}/comments/{comment_id}/` | Delete a comment; comment author only. |

Board ownership does not automatically grant board membership. When creating a board, include your own user ID in `members` if you also need member-only task and comment actions. Task assignees and reviewers must be board members. Task status values are `to-do`, `in-progress`, `review`, and `done`; priorities are `low`, `medium`, and `high`. A task's board cannot be changed through task PATCH. Comment authors are taken from the authenticated user.

## Important Notes

- Follow the setup order: dependencies, `.env`, migrations, superuser, then server. Missing dependencies, a missing signing key, or unapplied migrations prevent normal use.
- The current configuration is for local development. `runserver` and `DEBUG=True` are unsuitable for production; production hosting requires separate configuration.
- The current backend has no CORS package or CORS middleware configured. Connecting a frontend on another origin requires separate integration configuration. This does not affect starting the backend independently or using an API client.
- Keep `.env`, tokens, credentials, `.venv/`, and the SQLite database out of commits. The repository already ignores the local environment and database files.
- Optional local configuration and dependency checks are `python manage.py check` and `python -m pip check`. These do not replace an actual fresh installation or endpoint verification.

## Verification Status

The setup instructions were reviewed against the repository configuration and official project checklists. In the existing Windows virtual environment, `python -B manage.py check` reported no issues and `python -B -m pip check` reported no broken requirements. Installed versions matched `requirements.txt`.

A Fresh Clone Test has **not** been performed for this README. Dependency installation, fresh database migrations, superuser creation, server startup, and Admin/API access have not been exercised as part of this documentation task. macOS/Linux commands were reviewed but not executed. Complete the official Fresh Clone Test before submission; these static checks do not certify overall project readiness or the required PM test result.
