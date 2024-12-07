# Use the official Python image from the Docker Hub
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy all Python files into the container
COPY . .

# Install any dependencies if you have a requirements.txt file
# Uncomment the next line if you have a requirements.txt file
# RUN pip install -r requirements.txt

# Command to run your main.py when the container starts
CMD ["python", "main.py"]
