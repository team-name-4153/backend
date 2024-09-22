# Dockerfile
FROM python:3.10

EXPOSE ${FLASK_RUN_PORT}

WORKDIR /backend-app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg

RUN pip install --upgrade pip
COPY requirements.txt /backend-app
RUN pip install -r requirements.txt

# Copy the entire app directory
COPY . /backend-app

# Set environment variables for Flask
ENV FLASK_APP=/backend-app/app.py
ENV FLASK_ENV=${FLASK_ENV}

# Use the flask command for development with reloading enabled
CMD python ${FLASK_APP}