# Multi-stage build for admin-dashboard
# Stage 1: Build the React application
FROM node:20-alpine AS builder

WORKDIR /app

# Accept build argument for API base URL
# Empty string means use relative URLs (via nginx proxy)
# For Docker: don't set this or set to empty string
# For local dev: set to http://localhost:8000
ARG VITE_API_BASE_URL
# Set environment variable for Vite build
# If ARG is not provided or empty, ENV will be empty (which is correct)
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL:-}
# Debug: print the value during build (will be visible in build logs)
RUN echo "Building with VITE_API_BASE_URL='${VITE_API_BASE_URL:-<empty>}'"

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Install wget for health checks
RUN apk add --no-cache wget

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration for SPA routing
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Cache static assets \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
