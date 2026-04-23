FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG UBUNTU_MIRROR=mirrors.tencent.com
ARG PG_MAJOR=17
ARG PG_VERSION=17.5
ARG PGVECTOR_VERSION=v0.8.2
ARG PG_TEXTSEARCH_REF=v1.1.0

ENV TZ=Asia/Shanghai \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PG_HOME=/opt/postgresql \
    PGDATA=/var/lib/postgresql/data \
    PATH=/opt/postgresql/bin:$PATH

RUN rm -f /etc/apt/sources.list /etc/apt/sources.list.d/*.sources /etc/apt/sources.list.d/*.list \
    && printf 'Acquire::https::Verify-Peer "false";\nAcquire::https::Verify-Host "false";\nAcquire::AllowInsecureRepositories "true";\nAcquire::AllowDowngradeToInsecureRepositories "true";\n' > /etc/apt/apt.conf.d/99tencent-mirror-insecure \
    && printf 'deb [trusted=yes] https://%s/ubuntu/ noble main restricted universe multiverse\n' "$UBUNTU_MIRROR" > /etc/apt/sources.list \
    && printf 'deb [trusted=yes] https://%s/ubuntu/ noble-updates main restricted universe multiverse\n' "$UBUNTU_MIRROR" >> /etc/apt/sources.list \
    && printf 'deb [trusted=yes] https://%s/ubuntu/ noble-backports main restricted universe multiverse\n' "$UBUNTU_MIRROR" >> /etc/apt/sources.list \
    && printf 'deb [trusted=yes] https://%s/ubuntu/ noble-security main restricted universe multiverse\n' "$UBUNTU_MIRROR" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        git \
        gosu \
        locales \
        tzdata \
        build-essential \
        clang \
        make \
        pkg-config \
        flex \
        bison \
        libreadline-dev \
        zlib1g-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        libicu-dev \
        libzstd-dev \
        liblz4-dev \
        libpam0g-dev \
        libedit-dev \
        libcurl4-openssl-dev \
        uuid-dev \
    && locale-gen C.UTF-8 \
    && rm -f /etc/apt/apt.conf.d/99tencent-mirror-insecure \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -r -m -d /var/lib/postgresql -s /bin/bash postgres \
    && mkdir -p /var/lib/postgresql /docker-entrypoint-initdb.d /bootstrap /var/run/postgresql \
    && chown -R postgres:postgres /var/lib/postgresql /docker-entrypoint-initdb.d /bootstrap /var/run/postgresql

WORKDIR /tmp
RUN wget -O postgresql.tar.gz https://ftp.postgresql.org/pub/source/v${PG_VERSION}/postgresql-${PG_VERSION}.tar.gz \
    && tar -xzf postgresql.tar.gz \
    && cd postgresql-${PG_VERSION} \
    && ./configure \
        --prefix=${PG_HOME} \
        --with-openssl \
        --with-libxml \
        --with-libxslt \
        --with-icu \
        --with-zstd \
        --with-lz4 \
        --with-uuid=e2fs \
    && make -j"$(nproc)" world-bin \
    && make install-world-bin \
    && cd /tmp \
    && rm -rf postgresql-${PG_VERSION} postgresql.tar.gz

RUN git clone --branch ${PGVECTOR_VERSION} https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && make -C /tmp/pgvector PG_CONFIG=${PG_HOME}/bin/pg_config \
    && make -C /tmp/pgvector PG_CONFIG=${PG_HOME}/bin/pg_config install \
    && rm -rf /tmp/pgvector

RUN git clone --branch ${PG_TEXTSEARCH_REF} https://github.com/timescale/pg_textsearch.git /tmp/pg_textsearch \
    && make -C /tmp/pg_textsearch PG_CONFIG=${PG_HOME}/bin/pg_config \
    && make -C /tmp/pg_textsearch PG_CONFIG=${PG_HOME}/bin/pg_config install \
    && rm -rf /tmp/pg_textsearch

COPY conf/postgresql.conf ${PG_HOME}/share/postgresql.conf.template
COPY scripts/entrypoint.sh /usr/local/bin/pg-entrypoint.sh
COPY scripts/process-init-files.sh /usr/local/bin/process-init-files.sh
RUN chmod +x /usr/local/bin/pg-entrypoint.sh /usr/local/bin/process-init-files.sh

VOLUME ["/var/lib/postgresql/data"]
EXPOSE 5432
ENTRYPOINT ["/usr/local/bin/pg-entrypoint.sh"]
CMD ["postgres"]
