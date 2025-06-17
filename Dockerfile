#  builder
FROM python:3.13.4-slim-bookworm AS builder
WORKDIR /code
COPY ./requirements_313.txt /code/requirements.txt
RUN python3.13 -m venv /code/venv_313
ENV PATH="/code/venv_313/bin:$PATH"
# Get Rust
ENV PATH="/root/.cargo/bin:${PATH}"
COPY patches/* ./
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    patch \
    build-essential \
    curl && \
    apt-get update && \
    curl https://sh.rustup.rs -sSf | bash -s -- -y && \
    echo 'source $HOME/.cargo/env' >> $HOME/.bashrc && \
    pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r /code/requirements.txt && \
    rustup self uninstall -y && \
    patch -p1 /code/venv_313/lib/python3.13/site-packages/aredis/connection.py  < aredis_python_3_10.patch && \
    patch -p1 /code/venv_313/lib/python3.13/site-packages/aredis/utils.py  < aredis_utils_python_3_13.patch && \
    rm aredis_python_3_10.patch && \
    rm aredis_utils_python_3_13.patch && \
    apt-get -y remove curl && \
    apt-get -y clean

#  runner from base
FROM python:3.13.3-slim-bookworm AS base
WORKDIR /code
COPY --from=builder /code/venv_313 /code/venv_313
RUN apt-get update && \
    apt-get install -y --no-install-recommends libmimalloc2.0 && \
    apt-get -y clean && \
    rm -rf /var/cache/apt/archives && \
    rm -rf /code/venv_313/lib/python3.13/site-packages/pip && \
    find /code/venv_313/ -name "test*" -type d | xargs rm -rf && \
    rm -rf /var/lib/apt/lists/*
# activate virtual environment
ENV VIRTUAL_ENV=/code/venv_313
ENV PATH="/code/venv_313/bin:$PATH"

COPY ./app /code/app

ENV STORAGE=REDIS
ENV REDIS_HOST_NAME=redis
ENV REDIS_TCP_PORT=6379
ENV REDIS_DEFAULT_DEB=0

CMD ["granian", "--interface", "asgi", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "6", "--loop", "uvloop", "--ws" ]
