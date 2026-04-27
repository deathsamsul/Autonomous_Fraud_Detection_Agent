ARG BASE_IMAGE="ghcr.io/cloudnative-pg/postgresql:17.5-standard-bookworm"
FROM $BASE_IMAGE

USER root

# Install pgvector
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-17-pgvector && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER 26