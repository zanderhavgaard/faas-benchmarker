FROM python:3.8.2 as builder

RUN useradd \
        --create-home \
        --shell /bin/bash \
        docker

COPY . /home/docker/webserver

RUN chown -R docker:docker /home/docker

USER docker

WORKDIR /home/docker/webserver

RUN pip install -r /home/docker/webserver/requirements.txt

# ===========================

FROM python:3.8.2-slim

RUN useradd \
        --create-home \
        --shell /bin/bash \
        docker

COPY --from=builder /home/docker/webserver /home/docker/webserver
COPY --from=builder /home/docker/.local /home/docker/.local

RUN chown -R docker:docker /home/docker

USER docker

ENV PATH "$PATH:/home/docker/.local/bin"

WORKDIR /home/docker/webserver

CMD bash start.sh production
