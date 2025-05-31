
FROM python:3.12-slim


WORKDIR /app


COPY . /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 5000


CMD ["python", "wsgi.py"]