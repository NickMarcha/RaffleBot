# Use an official Python runtime as the base image
FROM python:3.11.4

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY /requirements.txt .

# Install application dependencies
RUN pip install -r requirements.txt

# Copy the application code into the container
COPY ./rafflebot .

# Copy the config file into the container
COPY $CONFIG_FILE_PATH /config/config.json

ENV LOGLEVEL=DEBUG
# Run the Python script
CMD ["python", "rafflebot/main.py"]