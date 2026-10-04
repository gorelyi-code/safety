FROM python:3.12-slim

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN useradd --create-home --uid 10001 imgdrop \
    && mkdir -p /srv/data \
    && chown imgdrop:imgdrop /srv/data
USER imgdrop

ENV STORAGE_DIR=/srv/data
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
