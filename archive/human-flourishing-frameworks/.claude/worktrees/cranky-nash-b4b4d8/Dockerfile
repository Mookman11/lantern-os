FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home --shell /usr/sbin/nologin hff \
    && mkdir -p /app/data \
    && chown -R hff:hff /app
USER hff
EXPOSE 5000
CMD gunicorn safe_app:app --bind 0.0.0.0:${PORT:-5000} --log-file -

