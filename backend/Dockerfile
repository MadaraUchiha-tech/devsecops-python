# ---- build stage: compile wheels into an isolated virtualenv ----
FROM python:3.12-slim AS build
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt && pip uninstall -y pip

# ---- runtime stage: only the venv + app code, running as a non-root user ----
FROM python:3.12-slim
LABEL org.opencontainers.image.source="https://github.com/MadaraUchiha-tech/devsecops-python" \
      org.opencontainers.image.description="CareSlot clinic appointments API (FastAPI)"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"
# Drop the base image's pip/setuptools (and their vendored libs): the app never installs at runtime.
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/* \
    && /usr/local/bin/python -m pip uninstall -y pip setuptools wheel || true \
    && rm -rf /usr/local/lib/python3.12/site-packages/pip* /usr/local/lib/python3.12/site-packages/setuptools* \
    && useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=20s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"
CMD ["sh", "-c", "alembic upgrade head && python -m app.seed && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers"]
