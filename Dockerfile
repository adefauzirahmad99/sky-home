FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN python -m pip install --no-cache-dir -r requirements.txt
EXPOSE 7860
CMD ["flet", "run", "app.py", "--web", "--port", "7860", "--host", "0.0.0.0"]
