FROM nginx:1.28.3-alpine

RUN mkdir -p /usr/share/nginx/html

COPY . /usr/share/nginx/html/

RUN ls -la /usr/share/nginx/html/ && \
    echo "Contents of /usr/share/nginx/html:" && \
    find /usr/share/nginx/html -type f | head -20

RUN chmod -R 755 /usr/share/nginx/html

RUN rm -f /etc/nginx/conf.d/default.conf

RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    autoindex off; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80