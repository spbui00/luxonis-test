# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y postgresql-client

COPY postgres-wait.sh /postgres-wait.sh
RUN chmod +x /postgres-wait.sh

# Make port 80 available to the world outside this container
EXPOSE 80

CMD ["python", "main.py"]