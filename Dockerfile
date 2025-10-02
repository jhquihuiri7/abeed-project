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

# Random variable to prevent caching
ARG RAND
# Copy the Dash app code
COPY . .

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose ports
EXPOSE 8000
#
# Command to start both Nginx and the Dash app
CMD ["sh", "-c", "nginx -g 'daemon off;' & python server.py"]


# Build command
# docker buildx build --build-arg RAND=$RANDOM -t dash_app .
# Run command
# docker run -d -p 8000:8000 dash_app
# Build and run command
# docker ps -q --filter "ancestor=dash_app:latest" | xargs -r docker stop && docker build --build-arg RAND=$RANDOM -t dash_app . && docker run --name dash_app --rm -d --network host dash_app:latest

