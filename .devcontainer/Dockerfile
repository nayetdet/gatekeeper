FROM mcr.microsoft.com/devcontainers/base:bookworm
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libasound2 \
        libgl1 \
        libglib2.0-0 \
        libgtk-3-0 \
        xauth \
        xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
