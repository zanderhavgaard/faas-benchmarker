FROM python:3.8.2

RUN useradd \
        --create-home \
        --shell /bin/bash \
        docker

COPY . /home/docker/faas-benchmarker

RUN chown -R docker:docker /home/docker

USER docker

ENV fbrd /home/docker/faas-benchmarker
ENV PATH "$PATH:/home/docker/.local/bin"
ENV PYTHONPATH "$PYTHONPATH:/home/docker/faas-benchmarker/benchmark"

WORKDIR /home/docker/faas-benchmarker

RUN pip install -r requirements.txt

CMD /bin/bash
