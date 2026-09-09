FROM nginx:alpine
# Copy built assets
COPY dist /usr/share/nginx/html
# Custom nginx config to handle React Router pushState.
# The SPA shell is no-store, not just no-cache — required to keep Safari's
# back-forward cache from restoring a stale pre-logout JS state snapshot on
# the Identity auth redirect round-trip. Hashed assets stay cacheable forever.
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html index.htm; \
    location /assets/ { \
        add_header Cache-Control "public, max-age=31536000, immutable"; \
        try_files $uri =404; \
    } \
    location / { \
        add_header Cache-Control "no-store"; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
