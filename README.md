# Employee Training Database Admin

A small Flask web application for creating, viewing, updating, and deleting records in an employee training database. The project originated as a 2022 database coursework application. The modernization preserves its MySQL table structure while replacing the unsafe dynamic evaluation and repeated handwritten forms with a database-driven interface.

This is a **single-administrator educational application**, not an internet-facing HR system. Employee records may contain personally identifiable information.

## Features

- Manage the 11 original tables: departments, roles, employees, skills, teachers, courses, course class days, course-skill links, employee-skill links, employee-course attendance, and exam attempts.
- Support multi-column primary keys without guessing field names.
- Browse paginated records, create and edit forms from reflected column metadata, and safely delete records.
- Require HTTP Basic authentication and CSRF tokens for changes.
- Use SQLAlchemy parameterized SQL operations and an explicit table allowlist.
- Keep the original `/<table>` and `/relation/<table>` *read-only* links working through redirects.
- Run locally or with a MySQL container and a Flask application container.

## Repository layout

```text
crud_app/
  config.py             Environment-driven settings
  repository.py         Safe, reflected table operations
  views.py              Authentication and HTML endpoints
  templates/            Shared accessible table/form layout
  static/style.css      Responsive styling
  wsgi.py               Production WSGI entry point
database/
  schema.sql            Original compatible MySQL schema, without seed data
  demo_seed.sql         Corrected synthetic example rows
tests/                  SQLite-backed regression tests
docs/architecture.md    Real component and data-flow diagrams
docs/security.md        Security model and known limitations
main.py                 Compatible local Python entry point
compose.yaml            Optional application + MySQL environment
```

## Quick start with Docker Compose

Install Docker with Compose, then:

1. Copy `.env.example` to `.env`.
2. Replace all placeholder credentials and the session key with strong, unique values. The password embedded in `DATABASE_URL` must match `MYSQL_APP_PASSWORD`, and URL-encode reserved characters in the connection string.
3. Run `docker compose up --build -d`.
4. Open **http://127.0.0.1:8000/** and enter the configured administrator username and password.

The MySQL database is initialized from `database/schema.sql` **only when its data volume is created for the first time**. The default dataset is empty. To load optional, synthetic demonstration rows into a fresh database:

```sh
docker compose exec -T db sh -c 'exec mysql -ucrud -p"$MYSQL_PASSWORD" db_project' < database/demo_seed.sql
```

Do not import demonstration rows twice without first resetting the disposable demonstration database. **Never delete a database volume that contains real data.** Use `docker compose down` without `-v` to stop the stack while retaining its data.

Compose binds the application to `127.0.0.1` by default. For remote access, place it behind HTTPS and a properly secured reverse proxy, and configure `COOKIE_SECURE=true`. The included password form is HTTP Basic authentication, so HTTPS is mandatory outside local development.

## Run with an existing MySQL installation

Requirements: Python 3.11+, MySQL 8.x, and a database initialized with `database/schema.sql`.

1. Create an isolated Python environment and install the project:

   ```sh
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install -e ".[dev]"
   ```

2. Create an empty MySQL database called `db_project`, import `database/schema.sql`, and create a dedicated least-privilege account with SELECT/INSERT/UPDATE/DELETE on that database. Do not use MySQL root for application access.
3. Export `DATABASE_URL`, `CRUD_ADMIN_PASSWORD`, and `FLASK_SECRET_KEY`. For local MySQL, use a URL of the form `mysql+pymysql://USERNAME:URL_ENCODED_PASSWORD@127.0.0.1:3306/db_project`. Generate a random session key of at least 32 characters.
4. Run `python main.py` and open **http://127.0.0.1:5000/**.

`DATABASE_URL` has no hardcoded fallback. Missing configuration prevents startup instead of silently connecting to a root account. Optional values are `CRUD_ADMIN_USERNAME` (default `admin`), `PAGE_SIZE` (default 50, maximum 200), and `COOKIE_SECURE` (default false for local HTTP only). `.env` is read by Docker Compose; the Python entry point does **not** implicitly load it.

## Development and testing

```sh
python -m pip install -e ".[dev]"
ruff check .
python -m compileall -q crud_app main.py tests
pytest -q
```

Unit and HTTP regression tests use disposable in-memory SQLite tables. A separate CI job initializes MySQL 8 with the original schema and synthetic seed records, then exercises the application against real reflected MySQL types. Neither job touches a production database. A deployment-specific smoke test is still recommended.

## CRUD behavior and compatibility

The app reflects the supported table definitions at startup, using the database's column types and primary keys. Missing tables are not displayed; unexpected tables are never exposed. Tables must have primary keys. Foreign keys and uniqueness constraints are enforced by the database, and rejected changes return a 409 error without leaking SQL details.

Courses' weekdays are managed through the **Course Class Days** table, rather than a special checkbox widget. All relationship tables can be edited directly, including multi-column keys. Existing bookmarks to `/course`, `/employee`, `/relation/employee_attends_course`, and other original read-only table URLs redirect to the updated views.

The old `/insert/...`, `/update/...`, and GET `/delete/...` mutation endpoints are intentionally retired: they could not safely remain compatible without reintroducing CSRF and unsafe-method vulnerabilities.

## Known limitations

- Single administrator; no accounts, audit trail, fine-grained permissions, or multi-user editing.
- MySQL schema intentionally retains historical design limitations: `employee.phone_number` and `ssn` are integers, financial amounts use floating-point columns, and course dates are not constrained by application-specific business rules. Correcting these requires a reviewed migration and data compatibility plan.
- The generic form enforces database types and constraints, not all possible domain rules.
- HTML pagination uses primary-key ordering and offsets; it is intended for a small training database.
- No automatic production database migrations, deployment, or backup process.
- The prior Git commit remains in repository history. Its code included an insecure demonstration secret and sample names; history has not been rewritten. Review the original history separately before treating this as a confidential-data repository.

Read [architecture](docs/architecture.md) and [security considerations](docs/security.md) before extending or deploying.
