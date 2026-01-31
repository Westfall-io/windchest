# Windchest — README_GIT

## Purpose
This document explains what the Windchest code in `src/` does and how the main orchestration flow works. It is intended to help developers understand runtime behavior, environment configuration, and how to run the project locally for development.

## Key files
- `src/main.py`: entrypoint and workflow orchestration. Logs into services, updates Windstorm thread status, discovers changed files, runs verification checks, uploads artifacts to MinIO, and triggers dependent threads.
- `src/env.py`: environment configuration and defaults read from environment variables.
- `src/local_junit.py`: simple local reader for a `junit.xml` file used for quick verification checks during development.

## High-level runtime flow (what `main()` does)
1. Log into MinIO using `windbinder.minio.login.login_minio()`.
2. Authenticate to Windstorm API via `windbinder.windstorm.authentication.login_windstorm_api()`.
3. Update the Windstorm thread execution status using `update_thread_status()`.
4. Discover modified files from the repository via `windbinder.git.repo.git_configure()`.
5. Create temporary directories under `/tmp/digitalforge` and copy changed files there.
6. Run verification checks on the collected files using `windbinder.junit.files.check_files()` and update verification results using `update_verification()`.
7. Upload collected changed files/artifacts to MinIO with `windbinder.minio.bucket.create_bucket()`.
8. Find dependent tasks (`find_dependent_tasks_by_id`) and execute them via `execute_dependent_thread()` when present.
9. Update the thread execution status again to indicate completion.

## Environment variables (see `src/env.py`)
- `VOLUME` (default: `/mnt/vol`): expected mounted volume used by the application.
- `WINDRUNNERHOST` (default: `http://windrunner-webhook-eventsource-svc.argo-events:12000/windrunner`)
- `WINDSTORMAPICLIENT` and `WINDSTORMAPISECRET`: credentials for Windstorm API client.
- `WINDSTORMAPIHOST` (default: `http://windstorm-api-service.windstorm:8000/`): Windstorm API base URL.
- `MINIOHOST` (default: `storage-minio.artifacts:9000`): MinIO host:port for storage.
- `MINIOUSER`, `MINIOTOKEN`: MinIO credentials.
- `MINIORETENTIONDAYS` (default: `7`): retention for uploaded artifacts.
- `KEYCLOAKHOST`, `KEYCLOAKREALM`: Keycloak OIDC provider configuration.

## Running locally (developer notes)
- The CLI uses `fire` to expose `main`. Example (from repo root):

```bash
python -m src.main
```

- The `main` function signature is `main(action=SAMPLE_ACTION, thread_execution_id=0)`. For development, `SAMPLE_ACTION` provides a default action payload.

- The script expects the `VOLUME` mount (or the configured default) to exist; otherwise it will raise `NotImplementedError`.

## Development / quick checks
- A minimal local JUnit parsing example lives in `src/local_junit.py`. It reads `src/junit.xml` and prints whether failing cases are `Failure` entries.

- To validate imports and static correctness, install dependencies from `requirements.txt` and run linters/tests as appropriate.

## Notes and assumptions
- This README documents the current code flow; most heavy lifting occurs in the `windbinder` package modules (e.g., MinIO helpers, Windstorm thread API wrappers, git utilities, and junit verification helpers). See those modules for implementation details.

- This project is intended to run inside an environment where Windstorm and MinIO services are reachable; local runs may need service mocks or Docker compose to emulate dependencies.

## Next steps
- Expand this README with example `action` payloads and expected MinIO bucket structure if desired.
- Add contribution and testing guidelines if this will be used by additional developers.
