FROM python:3.15-slim-bookworm@sha256:4e03260adeeebafccd084f3584e6b84823aba5651cfb53ef8a078ed441ddf9cd

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /bot

COPY requirements.txt .
RUN python -m pip install --disable-pip-version-check -r requirements.txt \
    && playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system cyberpulse \
	&& useradd --system --gid cyberpulse --create-home --home-dir /home/cyberpulse cyberpulse \
	&& mkdir -p /bot/data /bot/media/imagenes /bot/media/videos \
	&& chown -R cyberpulse:cyberpulse /bot

COPY --chown=cyberpulse:cyberpulse . .

USER cyberpulse

CMD ["python", "-m", "app.bot_cyberpulse"]
