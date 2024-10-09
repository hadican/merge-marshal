FROM python:3.11-alpine

WORKDIR /app

VOLUME /config/author_mapping.yml

RUN pip install --no-cache-dir slack-sdk==3.33.1 PyYAML==6.0.2 aiohttp==3.10.9

COPY *.py /app/

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]