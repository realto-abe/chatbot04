FROM python:3.9-slim

RUN mkdir -p /app
WORKDIR /app
COPY . /app

# Copy any additional custom requirements, if necessary (uncomment next line)
COPY requirements.txt ./

# Change back to root user to install dependencies
USER root

# COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5055

# CMD python -m rasa_core_sdk.endpoint --actions actions