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
MINIOTOKEN = os.environ.get("MINIOUSER","")
