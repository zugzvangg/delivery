FROM python:3.11-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.9.9 /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system .

COPY . .

EXPOSE 8082

CMD ["python", "-m", "uvicorn", "api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8082"]
