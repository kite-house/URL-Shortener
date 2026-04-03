FROM nginx:1.28.3-alpine

RUN mkdir -p /usr/share/nginx/html

COPY . /usr/share/nginx/html/

RUN chmod -R 755 /usr/share/nginx/html

RUN rm -f /etc/nginx/conf.d/default.conf

RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    error_page 404 /404.html; \
    error_page 410 /expired.html; \
    \
    location /api/ { \
        proxy_pass http://backend:8000/api/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
    \
    location ~ ^/([a-zA-Z0-9_-]+)$ { \
        proxy_pass http://backend:8000/api/$1; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_intercept_errors on; \
    } \
    \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80