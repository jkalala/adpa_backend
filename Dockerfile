# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install netcat
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Make the entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Expose port 8000 for the Django app
EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"] 