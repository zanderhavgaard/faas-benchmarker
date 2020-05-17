FROM python:3.8.2 as builder

RUN useradd \
        --create-home \
        --shell /bin/bash \
        docker

COPY . /home/docker/faas-benchmarker

# remove any .terraform directories we do not want..
RUN rm -rf $(find -type d -name ".terraform")

RUN chown -R docker:docker /home/docker

USER docker

WORKDIR /home/docker/faas-benchmarker

RUN pip install -r /home/docker/faas-benchmarker/requirements.txt

# ===========================

FROM python:3.8.2-slim

RUN useradd \
        --create-home \
        --shell /bin/bash \
        docker

USER docker

COPY --from=builder /home/docker/faas-benchmarker /home/docker/faas-benchmarker
COPY --from=builder /home/docker/.local /home/docker/.local

ENV fbrd /home/docker/faas-benchmarker
ENV PATH "$PATH:/home/docker/.local/bin"
ENV PYTHONPATH "$PYTHONPATH:/home/docker/faas-benchmarker/benchmark"

CMD /bin/bash
