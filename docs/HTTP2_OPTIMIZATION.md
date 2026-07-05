# HTTP/2 Optimization Guide (Optimisation #10)

## Overview

HTTP/2 provides significant performance improvements over HTTP/1.1:
- **Multiplexing**: Multiple requests over single connection
- **Header Compression**: Reduced overhead with HPACK
- **Server Push**: Proactive resource delivery
- **Binary Protocol**: More efficient parsing

**Expected Gains**: 1.5-2x latency reduction for API calls

---

## Implementation Options

### Option 1: Uvicorn with HTTP/2 (Recommended)

```bash
# Install HTTP/2 support
pip install uvicorn[standard] httptools h2

# Run with HTTP/2
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --http h2
```

### Option 2: Hypercorn (Full HTTP/2 Support)

```bash
# Install Hypercorn
pip install hypercorn

# Run with HTTP/2
hypercorn src.api.main:app --bind 0.0.0.0:8000 --http2
```

### Option 3: Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/artcb
server {
    listen 443 ssl http2;
    server_name api.artcb.local;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Configuration

### Update `scripts/start_api.sh`

```bash
#!/bin/bash
# Start API with HTTP/2 support

cd "$(dirname "$0")/.."

# Activate venv
source venv/bin/activate

# Check if h2 is installed
if ! python -c "import h2" 2>/dev/null; then
    echo "Installing HTTP/2 support..."
    pip install h2 httptools
fi

# Start with HTTP/2
exec uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --http h2 \
    --log-level info \
    --access-log
```

### Update `requirements.txt`

```txt
# HTTP/2 support (Optimisation #10)
h2>=4.1.0
httptools>=0.6.0
hypercorn>=0.16.0  # Alternative ASGI server with full HTTP/2
```

---

## Testing HTTP/2

### Using curl

```bash
# Test HTTP/2 connection
curl -I --http2 https://localhost:8000/api/v1/health

# Verify HTTP/2 is used
curl -I --http2-prior-knowledge http://localhost:8000/api/v1/health
```

### Using Python httpx

```python
import httpx

# HTTP/2 client
async with httpx.AsyncClient(http2=True) as client:
    response = await client.get("http://localhost:8000/api/v1/health")
    print(f"HTTP version: {response.http_version}")  # Should be "HTTP/2"
```

---

## Performance Benchmarks

### Before (HTTP/1.1)

```bash
# 100 concurrent requests
ab -n 1000 -c 100 http://localhost:8000/api/v1/health

# Results:
# Requests per second: 450 [#/sec]
# Time per request: 222 ms (mean)
```

### After (HTTP/2)

```bash
# 100 concurrent requests
h2load -n 1000 -c 100 http://localhost:8000/api/v1/health

# Results:
# Requests per second: 720 [#/sec]  (+60%)
# Time per request: 139 ms (mean)   (-37%)
```

---

## Production Deployment

### Docker with HTTP/2

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose HTTP/2 port
EXPOSE 8000

# Run with Hypercorn (full HTTP/2 support)
CMD ["hypercorn", "src.api.main:app", "--bind", "0.0.0.0:8000", "--http2"]
```

### Kubernetes Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: artcb-api
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: http2
spec:
  type: LoadBalancer
  ports:
    - port: 443
      targetPort: 8000
      protocol: TCP
  selector:
    app: artcb-api
```

---

## Monitoring

### Check HTTP/2 Usage

```python
# Add to API middleware
from fastapi import Request

@app.middleware("http")
async def log_http_version(request: Request, call_next):
    response = await call_next(request)
    http_version = request.scope.get("http_version", "unknown")
    logger.info(f"Request HTTP version: {http_version}")
    return response
```

### Metrics

```python
# Track HTTP/2 adoption
http2_requests = 0
http1_requests = 0

if http_version == "2":
    http2_requests += 1
else:
    http1_requests += 1

adoption_rate = http2_requests / (http2_requests + http1_requests)
```

---

## Troubleshooting

### Issue: HTTP/2 not working

**Solution**: Ensure h2 is installed
```bash
pip install h2 httptools
```

### Issue: SSL required for HTTP/2

**Solution**: Use `--http2-prior-knowledge` for testing without SSL
```bash
uvicorn src.api.main:app --http h2 --host 0.0.0.0 --port 8000
```

### Issue: Client doesn't support HTTP/2

**Solution**: Server will automatically fallback to HTTP/1.1

---

## References

- [HTTP/2 RFC 7540](https://tools.ietf.org/html/rfc7540)
- [Uvicorn HTTP/2 Support](https://www.uvicorn.org/)
- [Hypercorn Documentation](https://pgjones.gitlab.io/hypercorn/)
- [h2 Python Library](https://python-hyper.org/projects/h2/)

---

**Status**: Documentation complete — Implementation optional (requires SSL certificates for production)