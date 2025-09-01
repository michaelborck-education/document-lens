# 🇦🇺 DocumentLens VPS Deployment Guide

Two deployment options for your Australian VPS: **Raw/Native** and **Docker**.

## 📋 Prerequisites

- Ubuntu/Debian VPS with sudo access
- Python 3.11+ (for raw deployment)
- Docker & Docker Compose (for container deployment)
- 1GB+ RAM recommended
- 10GB+ disk space

## 🚀 Option 1: Raw/Native Deployment

Perfect for direct control and debugging.

### Quick Start
```bash
# Clone the repository
git clone https://github.com/michael-borck/document-lens.git
cd document-lens

# Make deployment script executable
chmod +x deploy.sh

# Deploy with default settings (port 8000)
./deploy.sh

# Or with custom settings
./deploy.sh --port 8080 --host 0.0.0.0 --workers 2
```

### Manual Setup (if you prefer step-by-step)
```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

# 2. Optional: Install uv for faster package management
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# 3. Clone and setup
git clone https://github.com/michael-borck/document-lens.git
cd document-lens

# 4. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt
# OR with uv: uv sync

# 6. Configure environment
cp .env.example .env  # Edit with your settings

# 7. Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Production Service (systemd)
```bash
# Create service file
sudo tee /etc/systemd/system/documentlens.service << 'EOF'
[Unit]
Description=DocumentLens Australian Document Analysis Service
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/documentlens
Environment=PATH=/opt/documentlens/.venv/bin
ExecStart=/opt/documentlens/.venv/bin/gunicorn app.main:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile - \
    --error-logfile -
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable documentlens
sudo systemctl start documentlens
sudo systemctl status documentlens
```

## 🐳 Option 2: Docker Deployment

Perfect for isolation and easy updates.

### Quick Start (Simple)
```bash
# Clone the repository
git clone https://github.com/michael-borck/document-lens.git
cd document-lens

# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f documentlens

# Stop
docker-compose down
```

### Production Deployment with Nginx
```bash
# Clone repository
git clone https://github.com/michael-borck/document-lens.git
cd document-lens

# Edit configuration
nano docker-compose.yml  # Update environment variables
nano nginx.conf          # Update server_name to your domain

# Deploy with Nginx reverse proxy
docker-compose --profile production up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### Manual Docker Commands
```bash
# Build image
docker build -t documentlens .

# Run container
docker run -d \
  --name documentlens \
  --port 8000:8000 \
  --env DEBUG=false \
  --env SECRET_KEY=your-secret-key \
  --restart unless-stopped \
  documentlens

# View logs
docker logs -f documentlens

# Stop container
docker stop documentlens && docker rm documentlens
```

## ⚙️ Configuration

### Environment Variables
Create `.env` file with your settings:

```bash
# Application
DEBUG=false
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Security - IMPORTANT: Change in production!
SECRET_KEY=your-super-secret-key-here

# File processing
MAX_FILE_SIZE=52428800    # 50MB
MAX_FILES_PER_REQUEST=10

# Rate limiting
RATE_LIMIT=30/minute

# CORS (update for your domain)
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### Performance Tuning
```bash
# For VPS with 1GB RAM
WORKERS=2

# For VPS with 2GB+ RAM
WORKERS=4

# For high-traffic sites
WORKERS=8
```

## 🌐 Reverse Proxy Setup

### Nginx (Recommended)
```bash
# Install Nginx
sudo apt install nginx

# Create site configuration
sudo tee /etc/nginx/sites-available/documentlens << 'EOF'
server {
    listen 80;
    server_name document-lens.serveur.au;  # Your domain

    client_max_body_size 50M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/documentlens /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL/TLS with Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d document-lens.serveur.au

# Auto-renewal (already configured)
sudo systemctl status certbot.timer
```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Check service status
curl http://your-domain.com/health

# Expected response:
# {"status": "healthy", "version": "1.0.0", "uptime": 3600}
```

### Logs
```bash
# Raw deployment logs
tail -f deploy.log

# Docker logs
docker-compose logs -f documentlens

# System service logs
sudo journalctl -u documentlens -f
```

### Updates
```bash
# Raw deployment
cd document-lens
git pull
source .venv/bin/activate
pip install -r requirements.txt  # or: uv sync
sudo systemctl restart documentlens

# Docker deployment
cd document-lens
git pull
docker-compose down
docker-compose up -d --build
```

## 🔧 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

2. **Permission denied**
   ```bash
   sudo chown -R $USER:$USER /path/to/document-lens
   ```

3. **Out of memory**
   ```bash
   # Reduce workers in .env
   WORKERS=1
   ```

4. **File upload too large**
   ```bash
   # Increase limits in .env
   MAX_FILE_SIZE=104857600  # 100MB
   ```

### Performance Issues
```bash
# Check resource usage
htop
docker stats  # For Docker deployment

# Monitor API performance
curl -w "@curl-format.txt" -s -o /dev/null http://your-domain.com/health
```

## 🚦 Testing Deployment

```bash
# Health check
curl http://localhost:8000/health

# Text analysis
curl -X POST http://localhost:8000/text \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test of the Australian DocumentLens service."}'

# File upload test
curl -X POST http://localhost:8000/files \
  -F "files=@test.txt" \
  -F "analysis_type=full"
```

## 📚 API Endpoints

Once deployed, your DocumentLens service provides:

- **`GET /health`** - Service health check
- **`POST /text`** - Analyse raw text (JSON)
- **`POST /academic`** - Academic analysis (JSON)
- **`POST /files`** - Upload and analyse files
- **`GET /docs`** - API documentation (if DEBUG=true)

## 🔐 Security Considerations

1. **Change default secret key** in `.env`
2. **Configure CORS** for your domain only
3. **Use HTTPS** in production
4. **Set up firewall** (ufw or iptables)
5. **Regular updates** of dependencies
6. **Monitor logs** for suspicious activity

---

## 🆘 Support

If you encounter issues:
1. Check the logs first
2. Verify your `.env` configuration
3. Ensure all dependencies are installed
4. Test with curl commands above

Your Australian DocumentLens service should now be running smoothly! 🇦🇺