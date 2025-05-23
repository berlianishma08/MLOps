# Use an official alpine nodeJS image as the base image
FROM node:alpine

# Gunakan image Python
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Copy the rest of the application code into the container
COPY . .

# Install dependencies Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the app on a port
EXPOSE 3000

# Command that runs the app
CMD ["npm", "start", "python", "app.py"]

