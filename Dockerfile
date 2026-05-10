FROM python:3-alpine

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /opt/r53dyndns

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY r53dyndns.py .

ENTRYPOINT ["/opt/r53dyndns/.venv/bin/python", "r53dyndns.py"]
