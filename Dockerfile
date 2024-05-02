FROM python:3.12

# Install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN python3.12 -m pip install -r /app/requirements.txt

COPY . /app

WORKDIR /app

CMD ["python3.12", "-u", "client.py"]
