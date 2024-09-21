FROM python:3.10

EXPOSE 5001

WORKDIR /backend-app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

RUN pip install --upgrade pip
COPY requirements.txt /backend-app
RUN pip install -r requirements.txt

COPY . /backend-app

CMD python app.py