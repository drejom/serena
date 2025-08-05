# Use Ubuntu base with R binary packages
FROM ubuntu:22.04 AS r-python-base

# Set timezone to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install system dependencies and R binary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    dirmngr \
    wget \
    gnupg \
    ca-certificates \
    && add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu jammy-cran40/" \
    && wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        r-base \
        r-base-dev \
        python3 \
        python3-dev \
        python3-venv \
        python3-pip \
        curl \
        build-essential \
        git \
        ssh \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3 /usr/bin/python

# Base stage with common dependencies
FROM r-python-base AS base
SHELL ["/bin/bash", "-c"]

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install pipx via pip
RUN python3 -m pip install --user pipx \
    && python3 -m pipx ensurepath

# Add local bin to the path
ENV PATH="${PATH}:/root/.local/bin"

# Install the latest version of uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Install core R dependencies and languageserver
RUN apt-get update && apt-get install -y --no-install-recommends \
    r-cran-jsonlite \
    r-cran-r6 \
    r-cran-stringr \
    r-cran-xml2 \
    r-cran-roxygen2 \
    && rm -rf /var/lib/apt/lists/* \
    && R -e "chooseCRANmirror(ind=1); install.packages('languageserver')"

# Set the working directory
WORKDIR /workspaces/serena

# Development target
FROM base AS development
# Copy all files for development
COPY . /workspaces/serena/

# Create virtual environment and install dependencies with dev extras
RUN uv venv
RUN . .venv/bin/activate
RUN uv pip install --all-extras -r pyproject.toml -e .
ENV PATH="/workspaces/serena/.venv/bin:${PATH}"

# Entrypoint to ensure environment is activated
ENTRYPOINT ["/bin/bash", "-c", "source .venv/bin/activate && $0 $@"]

# Production target
FROM base AS production
# Copy only necessary files for production
COPY pyproject.toml /workspaces/serena/
COPY README.md /workspaces/serena/
COPY src/ /workspaces/serena/src/

# Create virtual environment and install dependencies (production only)
RUN uv venv
RUN . .venv/bin/activate
RUN uv pip install -r pyproject.toml -e .
ENV PATH="/workspaces/serena/.venv/bin:${PATH}"

# Entrypoint to ensure environment is activated
ENTRYPOINT ["/bin/bash", "-c", "source .venv/bin/activate && $0 $@"]

