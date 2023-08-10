# Use an official Python runtime as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /rafflebot

# Copy the requirements file into the container
COPY ../requirements.txt .

# Install application dependencies
RUN pip install -r requirements.txt

# Copy the application code into the container
COPY ../rafflebot .

# Run the Python script
CMD ["python", "main.py"]