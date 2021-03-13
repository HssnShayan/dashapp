FROM python:3.9
WORKDIR /app
ENV DASH_DEBUG_MODE True
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8050
COPY . .
CMD ["python", "app.py"]