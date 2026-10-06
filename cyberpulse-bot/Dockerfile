FROM python:3.14-slim-bookworm

WORKDIR /bot

# Copiamos primero los requerimientos para optimizar caché
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN playwright install --with-deps chromium

# Copiamos el resto de las carpetas (app, data, media)
COPY . .

RUN groupadd --system cyberpulse \
	&& useradd --system --gid cyberpulse --create-home --home-dir /home/cyberpulse cyberpulse \
	&& mkdir -p /bot/data /bot/media/imagenes /bot/media/videos \
	&& chown -R cyberpulse:cyberpulse /bot /ms-playwright

USER cyberpulse

# El comando ahora apunta a la carpeta app/
CMD ["python", "-m", "app.bot_cyberpulse"]