FROM python:3.9

# Use subdirectory as working directory
RUN mkdir -p /app
WORKDIR /app
COPY . /app

# Copy any additional custom requirements, if necessary (uncomment next line)
COPY requirements.txt ./

# Change back to root user to install dependencies
USER root

# Install extra requirements for actions code, if necessary (uncomment next line)
RUN pip install -r requirements.txt

# Copy actions folder to working directory
COPY . /app

# By best practices, don't run the code with root user
USER 1001