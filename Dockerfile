FROM python:3.11.9-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    patch

WORKDIR /code

COPY ./requirements_311.txt /code/requirements.txt

# Get Ubuntu packages
RUN apt-get install -y \
    build-essential \
    curl

# Update new packages
RUN apt-get update

# Get Rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

RUN echo 'source $HOME/.cargo/env' >> $HOME/.bashrc
ENV PATH="/root/.cargo/bin:${PATH}"

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN rustup self uninstall -y

COPY patches/aredis_python_3_10.patch aredis.patch
RUN patch -p1 /usr/local/lib/python3.11/site-packages/aredis/connection.py  < aredis.patch

COPY ./app /code/app

ENV STORAGE=REDIS
ENV REDIS_HOST_NAME=redis
ENV REDIS_TCP_PORT=6379
ENV REDIS_DEFAULT_DEB=0

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--workers", "2", "--bind", "0.0.0.0:80"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
