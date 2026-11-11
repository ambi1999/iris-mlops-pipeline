# ------------------------------------------------------------------
# Dockerfile — Step 4 of the pipeline: PACKAGE everything into an image.
#
# Build the image:   docker build -t iris-mlops-pipeline .
# Run a container:   docker run -p 8000:8000 iris-mlops-pipeline
# Then open:         http://localhost:8000/docs
#
# Docker reads this file top to bottom. Each instruction creates a
# "layer"; Docker caches layers and only rebuilds what changed.
# ------------------------------------------------------------------

# Build arguments: values that can be changed at build time with
#   docker build --build-arg PYTHON_VERSION=3.13 ...
# CI passes the value from .python-version, so there is ONE source of truth.
# The default below must match .python-version for local builds.
ARG PYTHON_VERSION=3.13
# Tip: replace "latest" with your local uv version (run: uv --version),
# e.g. 0.9.5, so the image always uses exactly the same uv.
ARG UV_VERSION=latest

# Stage 1: grab the uv program from its official image.
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

# Stage 2: the real image. Start from an official, small ("slim")
# image that already has the right Python version.
FROM python:${PYTHON_VERSION}-slim

# Copy only the uv executables from stage 1 into this image.
COPY --from=uv /uv /uvx /bin/

# All following commands run inside the /app folder of the container.
WORKDIR /app

# uv settings for containers:
#   UV_COMPILE_BYTECODE=1   pre-compile Python files so the app starts faster
#   UV_LINK_MODE=copy       copy files instead of linking (avoids warnings in Docker)
#   UV_PYTHON_DOWNLOADS=never  use the image's Python; fail loudly if it
#                              doesn't match .python-version
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Copy ONLY the dependency files first, then install packages.
# Why? Dependencies change rarely; code changes often. Because this layer
# is cached, editing app.py won't force a slow reinstall of every package.
COPY pyproject.toml uv.lock .python-version ./

# Install the exact versions from uv.lock.
#   --locked               fail if uv.lock is out of date with pyproject.toml
#   --no-dev               skip dev tools (pytest, jupyter...) to keep the image small
#   --no-install-project   install only dependencies, not the project itself
RUN uv sync --locked --no-dev --no-install-project

# Put the virtual environment uv created (/app/.venv) first on the PATH,
# so "python" and "uvicorn" below come from it.
ENV PATH="/app/.venv/bin:$PATH"

# Now copy the application code into the image.
COPY train.py app.py ./

# Train the model while building, so the image ships with model.joblib.
# If the quality gate fails, this step fails and no image is produced.
RUN python train.py

# Document that the app listens on port 8000. (Publishing the port to
# your machine is done with -p 8000:8000 in `docker run`.)
EXPOSE 8000

# The command that runs when a container starts.
# --host 0.0.0.0 makes the server reachable from outside the container.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
