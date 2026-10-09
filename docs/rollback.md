# Rollback plan

- Keep the legacy Python/Android paths runnable during feature migration.
- Introduce the C ABI additively and retain legacy exports until parity tests pass.
- Tag each milestone and preserve old release artifacts.
- Do not delete or overwrite user history during data migration.
- Version saved workspaces and make migrations idempotent.
- If native loading fails, use the backend fallback and report capability status.
- After Flutter parity is accepted, remove the old UI from release workflows. The
  old UI remains available through its release tag, not as a second production UI.
