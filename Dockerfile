FROM python:3.11-slim
WORKDIR /app
COPY . /app
EXPOSE 8765
CMD ["python", "-m", "skillos.cli", "serve", "--host", "0.0.0.0", "--port", "8765"]
