# NGINX CONFIG

To Generate self-signed keys:

```
# Generate a private key
openssl genrsa -out selfsigned.key 2048

# Generate a self-signed certificate
openssl req -new -x509 -key selfsigned.key -out selfsigned.crt -days 365
```

# NGINX CONF

```nginx.conf
server {
    resolver 127.0.0.11 valid=300s
    listen 443 ssl default_server;

    # this is the mounted by docker compose
    ssl_certificate /etc/ssl/certs/selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/selfsigned.key;

    location /services {
        proxy_pass http://server/services;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

# Mount locations

```yaml

volumes:
- <root>/selfsigned.crt:/etc/ssl/certs/selfsigned.crt
- <root>/selfsigned.key:/etc/ssl/private/selfsigned.key
- <root>/nginx.conf:/etc/nginx/conf.d/default.conf
```

# Sample Docker Compose

```yaml

  nginx:
    image: nginx:latest
    env_file:
      - .env
    ports:
      - 80:80
      - 443:443
    volumes:
      - ./nginx/selfsigned.crt:/etc/ssl/certs/selfsigned.crt
      - ./nginx/selfsigned.key:/etc/ssl/private/selfsigned.key
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf

```