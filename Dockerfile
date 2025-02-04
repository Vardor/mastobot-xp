# Set base image (host OS)
FROM python:3.12-alpine

# Set timezone
ENV TZ=America/Santiago

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

#
RUN mkdir data

# Copy the content of the local src directory to the working directory
COPY app.py .
COPY xposter/ xposter/
COPY templates/ templates/

# Specify the command to run on container start
CMD [ "python", "./app.py" ]