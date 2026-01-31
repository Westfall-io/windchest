"""
Environment configuration for Windchest.

This module centralizes environment variable defaults and provides
module-level constants used across the Windchest codebase. Values
are read from environment variables where available and fall back
to sensible defaults where appropriate.

Examples of provided constants:
- `VOLUME`: mounted volume path used for temporary storage
- `WINDSTORMAPIHOST`: base URL for the Windstorm API
- `MINIOHOST`: host and port for MinIO storage
"""

import os
VOLDEF = "/mnt/vol"
VOLUME = os.environ.get("VOLUME",VOLDEF)
WINDRUNNERHOST = os.environ.get(
    "WINDRUNNERHOST",
    "http://windrunner-webhook-eventsource-svc.argo-events:12000/windrunner"
)
WINDSTORMAPICLIENT = os.environ.get("WINDSTORMAPICLIENT","")
WINDSTORMAPISECRET = os.environ.get("WINDSTORMAPISECRET","")

WINDSTORMAPIHOST = os.environ.get(
    "WINDSTORMAPIHOST",
    "http://windstorm-api-service.windstorm:8000/"
)

## MINIO VALUES
MINIOHOST = os.environ.get("MINIOHOST","storage-minio.artifacts:9000")
MINIOUSER = os.environ.get("MINIOUSER","")
MINIOTOKEN = os.environ.get("MINIOTOKEN","")
MINIORETENTIONDAYS = os.environ.get("MINIORETENTIONDAYS", 7)

## KEYCLOAK VALUES
KEYCLOAKHOST = os.environ.get("KEYCLOAKHOST","https://keycloak.digitalforge.app")
KEYCLOAKREALM = os.environ.get("KEYCLOAKREALM","test")
