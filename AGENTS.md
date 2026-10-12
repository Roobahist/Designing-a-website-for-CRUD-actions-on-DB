# Developer and agent guidance

This repository is a small Flask/SQLAlchemy database administration project. Make evidence-driven, minimal improvements while protecting its existing MySQL data.

- The application factory is `crud_app.create_app(settings=None, engine=None)`. Inject `Settings` and a SQLAlchemy `Engine` in tests rather than touching real databases.
- `crud_app/repository.py` is the only layer that assembles SQL. Keep table access restricted to `SUPPORTED_TABLES`. Do not use `eval`, arbitrary model names, or raw string-concatenated SQL.
- `crud_app/views.py` owns HTTP behavior, authentication, CSRF, and the HTML flow. Destructive actions must remain POST-only with CSRF validation.
- Use reflected primary keys, including composite keys. Do not infer key names from table names: attendance and exam tables use `participant_id`.
- `database/schema.sql` is the historic database contract. Do not silently change columns or drop tables. Any migration needs a backup, a tested upgrade path, and explicit review.
- Keep configuration in `Settings` or injected dependencies; do not commit secrets or provide insecure production defaults.
- Preserve the old read-only table URL redirects. Changes to public URLs require documentation and compatibility assessment.
- Shared Jinja templates implement generic forms and listings. Keep input labels, keyboard focus, escaped output, CSRF tokens, and responsive tables functional.
- Use the smallest clear abstraction. No new frontend framework, service layer, or deployment target without a practical requirement.
- Run `ruff check .`, `python -m compileall -q crud_app main.py tests`, and `pytest -q` before merging. Tests use disposable SQLite fixtures; any MySQL-specific SQL changes additionally need a real MySQL smoke test.
- Keep architecture diagrams and README accurate. Report tests that could not be executed.
