# 🌐 Production Deployment Guide

## Quick Deployment Options

### Option 1: Vercel (Frontend) + Railway (Backend) ⚡ FASTEST

**Perfect for:** Quick deployment, free tier available, easy setup

#### Frontend (Vercel)
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy frontend
cd resume-analyzer-frontend
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? resume-analyzer
# - Directory? ./
# - Override settings? No
```

**Result:** Your frontend will be live at `https://resume-analyzer-xyz.vercel.app`

#### Backend (Railway)
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Deploy backend
cd resume-analyzer-backend
railway init
railway up

# 4. Add environment variables in Railway dashboard:
# - GEMINI_API_KEY
# - SECRET_KEY
# - DATABASE_URL (Railway provides PostgreSQL)
```

**Result:** Backend live at `https://your-app.railway.app`

**Cost:** Free tier available, ~$5-10/month for production

---

### Option 2: AWS (Full Control) 🏢 PROFESSIONAL

**Perfect for:** Scalability, enterprise features, full control

#### Architecture:
```
Internet
    ↓
CloudFront (CDN)
    ↓
S3 (Frontend) + EC2 (Backend)
    ↓
RDS (PostgreSQL) + ElastiCache (Redis)
```

#### Setup:

**1. Frontend (S3 + CloudFront)**
```bash
# Build frontend
cd resume-analyzer-frontend
npm run build

# Upload to S3
aws s3 sync dist/ s3://your-bucket-name --acl public-read

# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name your-bucket-name.s3.amazonaws.com
```

**2. Backend (EC2)**
```bash
# Launch EC2 instance (Ubuntu 22.04)
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# Clone your repo
git clone https://github.com/your-username/resume-analyzer.git
cd resume-analyzer/resume-analyzer-backend

# Install Python packages
pip3 install -r requirements.txt

# Set up systemd service
sudo nano /etc/systemd/system/resume-analyzer.service
```

**Service file:**
```ini
[Unit]
Description=Resume Analyzer API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/resume-analyzer/resume-analyzer-backend
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/home/ubuntu/.local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl start resume-analyzer
sudo systemctl enable resume-analyzer

# Configure Nginx
sudo nano /etc/nginx/sites-available/resume-analyzer
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/resume-analyzer /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

**3. Database (RDS)**
- Create PostgreSQL instance in AWS RDS
- Update DATABASE_URL in environment variables

**Cost:** ~$20-50/month (t2.micro EC2 + db.t3.micro RDS)

---

### Option 3: Google Cloud Platform 🚀 SCALABLE

**Perfect for:** Auto-scaling, serverless, Google ecosystem

#### Frontend (Firebase Hosting)
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize
cd resume-analyzer-frontend
firebase init hosting

# Deploy
npm run build
firebase deploy
```

#### Backend (Cloud Run)
```bash
# Create Dockerfile
cd resume-analyzer-backend
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/your-project/resume-analyzer
gcloud run deploy resume-analyzer \
  --image gcr.io/your-project/resume-analyzer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Database:** Cloud SQL (PostgreSQL)

**Cost:** Pay-per-use, ~$10-30/month

---

### Option 4: Docker + DigitalOcean 🐳 SIMPLE

**Perfect for:** Docker experience, simple deployment, affordable

#### Create docker-compose.yml:
```yaml
version: '3.8'

services:
  backend:
    build: ./resume-analyzer-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/resume_analyzer
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - db
      - redis

  frontend:
    build: ./resume-analyzer-frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=resume_analyzer
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
```

#### Deploy to DigitalOcean:
```bash
# 1. Create Droplet (Ubuntu 22.04, 2GB RAM)

# 2. SSH into droplet
ssh root@your-droplet-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Clone repo
git clone https://github.com/your-username/resume-analyzer.git
cd resume-analyzer

# 5. Deploy
docker-compose up -d
```

**Cost:** $12-24/month (2-4GB droplet)

---

## 🔒 Security Checklist

Before deploying:

- [ ] Change SECRET_KEY to a strong random value
- [ ] Set up HTTPS/SSL (use Let's Encrypt)
- [ ] Enable CORS only for your domain
- [ ] Set up environment variables (don't commit .env)
- [ ] Enable database backups
- [ ] Set up monitoring (Sentry, LogRocket)
- [ ] Add rate limiting
- [ ] Enable firewall (UFW on Ubuntu)
- [ ] Set up CI/CD (GitHub Actions)
- [ ] Add health check endpoints

---

## 🚀 Post-Deployment

### 1. Set up custom domain
```bash
# Update DNS records:
# A record: @ → your-server-ip
# CNAME: www → your-domain.com
```

### 2. Enable HTTPS
```bash
# Using Certbot (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 3. Set up monitoring
```bash
# Install monitoring tools
pip install sentry-sdk

# Add to main.py
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

### 4. Enable backups
```bash
# Database backup script
#!/bin/bash
pg_dump resume_analyzer > backup_$(date +%Y%m%d).sql
aws s3 cp backup_$(date +%Y%m%d).sql s3://your-backup-bucket/
```

---

## 📊 Recommended Stack for B.Tech Project

**Best Balance: Vercel + Railway**

**Why:**
- ✅ Free tier available
- ✅ Easy deployment (5 minutes)
- ✅ Automatic HTTPS
- ✅ Good performance
- ✅ Easy to demo
- ✅ Professional URLs
- ✅ No server management

**Steps:**
1. Deploy frontend to Vercel (2 min)
2. Deploy backend to Railway (3 min)
3. Add custom domain (optional)
4. Share link with professors/recruiters

**Total Time:** 5-10 minutes
**Total Cost:** Free (or $5/month for better limits)

---

## 🎓 For Your Presentation

**Show:**
1. Live deployed application (not localhost)
2. Custom domain (looks professional)
3. HTTPS enabled (security)
4. Fast loading (CDN)
5. Mobile responsive
6. Analytics dashboard

**Mention:**
- Deployed on cloud (Vercel/Railway/AWS)
- CI/CD pipeline
- Scalable architecture
- Production-ready
- Security best practices

---

## 🆘 Quick Deploy Commands

```bash
# Frontend (Vercel)
cd resume-analyzer-frontend
npm install -g vercel
vercel --prod

# Backend (Railway)
cd resume-analyzer-backend
npm install -g @railway/cli
railway login
railway init
railway up

# Done! Your app is live! 🎉
```

---

**Need help? Check:**
- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- AWS Docs: https://aws.amazon.com/documentation
- GCP Docs: https://cloud.google.com/docs

**Your app will be live in minutes! 🚀**
