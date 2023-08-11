# Use an official Python runtime as the base image
FROM python:3.11.4

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY /requirements.txt .

# Copy the requirements file into the container
#COPY ../config.json .

# Install application dependencies
RUN pip install -r requirements.txt


# Copy the application code into the container
COPY ./rafflebot .

COPY ./config/config.json /config/config.json

ENV LOGLEVEL=DEBUG
# Run the Python script
CMD ["python", "rafflebot/main.py"]