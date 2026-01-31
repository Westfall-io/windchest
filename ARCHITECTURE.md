# Windchest Architecture

This document provides a block/interaction diagram for the Windchest code in `src/` and its runtime relationships with external services.

## Diagram (Mermaid)

```mermaid
flowchart TB
  subgraph App[Windchest Application]
    direction TB
    M(main.py):::appEntry["main.py\n(orchestration)"]
    E(env.py):::config["env.py\n(configuration)"]
    LJ(local_junit.py):::helper["local_junit.py\n(local tester)"]
  end

  subgraph Windbinder[windbinder package (external/placeholder)]
    direction TB
    WB1["windbinder.minio\n(login, bucket)"]
    WB2["windbinder.windstorm\n(authentication, thread)"]
    WB3["windbinder.git\n(repo utilities)"]
    WB4["windbinder.junit\n(file verifiers)"]
    SAB[SAMPLE_ACTION]:::data
  end

  subgraph External[External Services]
    direction TB
    Minio[MinIO storage]
    Windstorm[Windstorm API]
    Git[Git repository]
    Keycloak[Keycloak / OIDC]
  end

  %% Relationships
  M -->|reads| E
  M -->|uses| WB1
  M -->|uses| WB2
  M -->|uses| WB3
  M -->|uses| WB4

  WB1 -->|store/upload| Minio
  WB2 -->|update/status, auth token| Windstorm
  WB3 -->|discover changes| Git
  WB4 -->|verify junit files| M

  M -->|triggers (dependent tasks)| WB2
  M -->|invokes sample action| SAB
  E -.->|provides config to| WB1
  E -.->|provides config to| WB2
  E -.->|provides config to| WB1

  classDef appEntry fill:#f9f,stroke:#333,stroke-width:1px;
  classDef config fill:#fffbcc,stroke:#333;
  classDef helper fill:#f0f0f0,stroke:#333;
  classDef data fill:#e0f7fa,stroke:#333;
```

## Narrative / Notes

- `src/main.py` is the orchestration entrypoint. It:
  - logs into MinIO and Windstorm APIs
  - fetches updated files from Git (via `windbinder.git.repo`)
  - runs verification checks (via `windbinder.junit.files.check_files`)
  - uploads artifacts to MinIO (via `windbinder.minio.bucket.create_bucket`)
  - updates Windstorm thread execution status and triggers dependent threads

- `src/env.py` centralizes environment variables used across modules. Important variables include `VOLUME`, `MINIOHOST`, `WINDSTORMAPIHOST`, and Keycloak settings.

- `src/local_junit.py` is a minimal local helper that reads `src/junit.xml` for quick verification and developer testing.

- The `windbinder` package referenced by the code is not present in this repository (empty `src/windbinder/` folder). The diagram treats these modules as implementation points for:
  - MinIO login and bucket operations
  - Windstorm authentication and thread operations
  - Git repository utilities and changed-file detection
  - JUnit based verification helpers

- External dependencies and services:
  - MinIO: object storage to persist changed files / verification artifacts.
  - Windstorm API: used to update thread execution state and to trigger dependent tasks.
  - Git repository: source-of-truth for changed files; discovered via git utilities.
  - Keycloak (OIDC): identity provider used for Windstorm authentication (when applicable).

## Next steps / improvements
- If you prefer a PNG/SVG export, add a PlantUML or Mermaid renderer step in CI or use a local tool to export the diagram.
- Optionally expand this to include sequence diagrams for a detailed call flow (login → status updates → verification → upload → trigger).

