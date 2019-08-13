FROM python:3.7.4-slim

#RUN apk add --no-cache git
RUN apt-get update && \
    apt-get install -y git make gcc g++ libyaml-dev libffi-dev libssl-dev time
#RUN apk add --no-cache --virtual .build-deps make gcc g++ py-yaml yaml-dev libffi-dev openssl-dev && pip install -r /work/requirements.txt && apk del .build-deps
COPY bin /ansible-review/bin
COPY lib /ansible-review/lib
COPY setup.py /ansible-review
RUN pip install /ansible-review
