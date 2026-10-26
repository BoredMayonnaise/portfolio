#!/usr/bin/env bash
# Probe Gunicorn over HTTP, including actual static URLs from the homepage.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
compose exec -T web python - <<'PY'
import os
import re
from urllib.request import Request, build_opener, HTTPRedirectHandler
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')
import django
django.setup()
from django.conf import settings
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None
opener = build_opener(NoRedirect)
host = next(h for h in settings.ALLOWED_HOSTS if h and h != '*' and not h.startswith('.'))
def fetch(path):
    req = Request('http://127.0.0.1:8000' + path, headers={'Host': host, 'X-Forwarded-Proto': 'https'})
    with opener.open(req, timeout=5) as response:
        assert response.status == 200, (path, response.status)
        return response.read().decode()
html = fetch('/')
styles = re.findall(r'<link[^>]+href="([^"]+)"[^>]*>', html)
styles = [url for url in styles if url.startswith('/static/') and '.css' in url]
assert styles, 'No stylesheet links found'
for url in styles:
    fetch(url)
print('HTTP 200: homepage and all linked stylesheets')
PY
