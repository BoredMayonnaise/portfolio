# Portfolio operations

The portfolio application runs as the Docker Compose `web` service. Source and templates are copied into its image. Restarting the legacy systemd service or restarting a container does not deploy source changes.

```bash
bash infra/service.sh deploy       # Build updated code, recreate web, verify HTTP/CSS
bash infra/service.sh restart      # Apply .env changes with the existing image
bash infra/service.sh status
bash infra/service.sh logs -f
```

Deployment builds before replacing the running container. The existing container startup runs migrations and collects static files before Gunicorn starts. Health checks require HTTP 200 for the homepage and its linked CSS; redirects do not count as success. These checks target the application inside Docker, not public DNS or TLS. Verify the public HTTPS endpoint separately after infrastructure changes.

These commands manage web only. They do not restart nginx, certbot, n8n, or the legacy systemd units. Proxy configuration and certificate management remain separate. The former `enable` and `disable` systemd commands are removed; Docker's `restart: unless-stopped` policy controls persistence.
