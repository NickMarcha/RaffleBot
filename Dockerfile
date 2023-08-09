FROM python:3.11
WORKDIR /rafflebot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV LOGLEVEL=DEBUG
ENTRYPOINT ["python", "main.py"]