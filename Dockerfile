#  base
FROM python:3.13.3-slim-bookworm AS base
RUN apt-get update && apt-get install -y --no-install-recommends libmimalloc2.0

#  builder
FROM base AS builder
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
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
FROM base
WORKDIR /code
COPY --from=builder /code/venv_313 /code/venv_313
# activate virtual environment
ENV VIRTUAL_ENV=/code/venv_313
ENV PATH="/code/venv_313/bin:$PATH"

COPY ./app /code/app

ENV STORAGE=REDIS
ENV REDIS_HOST_NAME=redis
ENV REDIS_TCP_PORT=6379
ENV REDIS_DEFAULT_DEB=0

CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--workers", "6", "--bind", "0.0.0.0:80"]
