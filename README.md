# openai-completion-ct2fast
Simple fastapi app cloning openai completion api


## Install

### Get the model

Download the model from <https://huggingface.co/piratos/ct2fast-docsgpt-14b>

# ENV

Make sure an environment variable `MODEL_PATH` is accessible to the container runtime
containing the path to the model folder

### Docker

```
docker build -t openai_backend

docker run -v <modelpath>:/app/ct2fast-docsgpt-14b -d openai_backend
```

### Docker compose

Adjust mounting volumes

```
docker compose build openai

docker compose up -d
```
