FROM python:alpine

RUN apk update && apk add curl git

RUN curl -O https://pubhub.devnetcloud.com/media/iox/docs/artifacts/ioxclient/ioxclient-v1.8.1.0/ioxclient_1.8.1.0_linux_amd64.tar.gz && tar -xzf ioxclient_1.8.1.0_linux_amd64.tar.gz && chmod +x ioxclient_1.8.1.0_linux_amd64/ioxclient && mv ioxclient_1.8.1.0_linux_amd64/ioxclient /usr/bin/ioxclient