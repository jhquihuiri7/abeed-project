FROM python:3.10.15-slim

# Install Nginx
RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory for the app
WORKDIR /app

# Copy the requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Dash app code
COPY . .

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose ports
EXPOSE 8000
#
# Command to start both Nginx and the Dash app
CMD ["sh", "-c", "service nginx start && python app.py"]
# CMD ["sh", "-c", "python dash_app.py"]