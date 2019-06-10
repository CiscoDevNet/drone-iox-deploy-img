FROM python:alpine

RUN apk update && apk add curl git

RUN pip install requests

ENV FOGD=10.10.20.50 username=admin password=admin_123 appname=ciscodevnet/go-escaperoom deviceip=10.10.20.51 imageTag=latest dockerReg=registry.hub.docker.io

WORKDIR /

COPY deploy2FogD.py .
COPY deploy2IOx.py .
COPY env_config.py .