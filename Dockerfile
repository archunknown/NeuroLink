# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install system dependencies for OpenCV and PyQt6
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libx11-6 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libegl1 \
    libfontconfig1 \
    libdbus-1-3 \
    libxcb-randr0 \
    libxcb-shm0 \
    libxcb-util1 \
    libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.docker.txt

# Make sure the app can connect to the X server
ENV DISPLAY=:0

# Run the application
CMD ["python", "-m", "app.ui"]
