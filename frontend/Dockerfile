# Build stage
FROM debian:latest AS build-env

# Install Flutter dependencies
RUN apt-get update 
RUN apt-get install -y curl git wget unzip libgconf-2-4 gdb libstdc++6 libglu1-mesa fonts-droid-fallback python3
RUN apt-get clean

# Clone the flutter repo
RUN git clone https://github.com/flutter/flutter.git /usr/local/flutter

# Set flutter path
ENV PATH="/usr/local/flutter/bin:/usr/local/flutter/bin/cache/dart-sdk/bin:${PATH}"

# Run flutter doctor
RUN flutter doctor -v

# Enable flutter web
RUN flutter channel stable
RUN flutter upgrade
RUN flutter config --enable-web

# Copy files to container and build
WORKDIR /app
COPY . .

# Configure Git for Flutter
RUN git config --global --add safe.directory /usr/local/flutter

# Get app dependencies
RUN flutter pub get

# Build the app for the web with environment variables
ARG API_BASE_URL=/api/v1/database
ARG APP_TITLE="Database Sync"
ARG IS_DEVELOPMENT=false
ARG ENABLE_DEBUG=false

RUN flutter build web --base-href / \
  --dart-define=API_BASE_URL=$API_BASE_URL \
  --dart-define=APP_TITLE="$APP_TITLE" \
  --dart-define=IS_DEVELOPMENT=$IS_DEVELOPMENT \
  --dart-define=ENABLE_DEBUG=$ENABLE_DEBUG

# Update the HTML title with the environment variable
RUN sed -i "s/<title>database_sync_frontend<\/title>/<title>$APP_TITLE<\/title>/g" build/web/index.html && \
    sed -i "s/content=\"database_sync_frontend\"/content=\"$APP_TITLE\"/g" build/web/index.html

# Production stage
FROM nginx:alpine

# Copy the built app from the build stage
COPY --from=build-env /app/build/web /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 