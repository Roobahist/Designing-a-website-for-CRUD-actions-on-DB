# Security considerations

## Current protections

- Every route requires a configured administrator name and password using HTTP Basic authentication. The password is not stored in the repository. Credentials are compared in constant time.
- All mutations require POST and a session-bound CSRF token; GET requests never change records.
- A named-table allowlist and reflected SQLAlchemy columns replace `eval()` and unchecked attribute access. Bound statements prevent form fields from becoming SQL syntax.
- Session cookies are HttpOnly and SameSite=Lax. Set `COOKIE_SECURE=true` behind HTTPS.
- Server rejects unknown fields, invalid values, oversized requests, unknown table names, invalid composite record identities, and missing records.
- Constraint errors are returned without leaking SQL statements or sensitive database information.
- Docker publishes the application on loopback by default; MySQL is not published to the host.

## Limits and deployment cautions

This is an educational single-admin project, not a hardened personnel information system.

- **TLS is mandatory outside localhost.** Basic authentication transmits an encoded password with each request. HTTPS protects it in transit.
- A network-exposed installation additionally needs rate limiting, operational access controls, appropriate cookie settings, monitoring, backup and recovery, and possibly a real identity provider with MFA.
- All authenticated administrators can view and change every record, including sensitive employee data. There is no audit log, RBAC, column-level restriction, account lockout, or login throttling.
- The database account should be limited to SELECT, INSERT, UPDATE, and DELETE on `db_project`. Initialization is a separate privileged operation.
- Do not paste credentials into public logs or issue reports. Never commit `.env`.
- SQLite regression tests validate most HTTP behavior. MySQL dialect-specific behavior requires separate verification.
- The original 2022 commit contains a hardcoded demonstrative Flask secret, an unprotected root connection configuration, and example personal names. Its history is preserved intentionally; changing current files does not remove old commits. Rotate any actual credentials that might ever have reused those values.
- The original schema still has design problems, including integer phone numbers and social security identifiers and approximate floating-point monetary columns. Remediate with a reviewed migration rather than changing existing deployed tables silently.

No claim is made that the repository is safe to expose directly on the public internet.
