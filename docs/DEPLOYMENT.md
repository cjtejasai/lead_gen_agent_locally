# 🚀 EC2 Deployment Guide - Lyncsea Platform

## ✅ What We've Built

### Feature Flag System
- **STT_PROVIDER**: Toggle between `local_whisper` and `assemblyai`
- **Both support full speaker diarization** (who said what)
- Switch providers with ONE environment variable

---

## 📋 Environment Variables

```bash
# Required for all deployments
DATABASE_URL=postgresql://user:pass@localhost:5432/ayka
OPENAI_API_KEY=sk-...
EMAIL_USER=your@gmail.com
EMAIL_PASSWORD=app-password
SERPER_API_KEY=...

# Speech-to-Text Configuration
STT_PROVIDER=local_whisper          # or "assemblyai"
WHISPER_MODEL_SIZE=base             # tiny, base, small, medium, large
ENABLE_DIARIZATION=true             # Speaker detection
ASSEMBLYAI_API_KEY=...              # Only needed if using AssemblyAI

# Optional
SENTRY_DSN=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

---

## 🖥️ EC2 Setup for Local Whisper

### Instance Requirements

#### **Option A: GPU Instance (Recommended)**
- **Instance Type**: `g4dn.xlarge` or `g5.xlarge`
- **GPU**: NVIDIA T4 or A10G
- **RAM**: 16GB+
- **Storage**: 50GB
- **Cost**: ~$0.50-0.70/hour (~$360-500/month)

**Why GPU?**
- Whisper on CPU is **10x slower**
- 5-minute audio takes 30-50 minutes on CPU
- GPU processes in 30-60 seconds

#### **Option B: CPU Instance (Dev/Testing)**
- **Instance Type**: `c6i.2xlarge` (8 vCPU, 16GB RAM)
- **Cost**: ~$0.34/hour (~$245/month)
- **Performance**: Slow but works for testing

---

## 🛠️ EC2 Deployment Steps

### 1. Launch EC2 Instance

```bash
# Choose Ubuntu 22.04 LTS
# Security Group: Open ports 22 (SSH), 80 (HTTP), 8000 (API), 3000 (Frontend)
```

### 2. Connect and Install Dependencies

```bash
ssh ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-venv nodejs npm postgresql ffmpeg git nginx

# Install Docker (optional, for containerized deployment)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

### 3. Install NVIDIA Drivers (GPU Instance Only)

```bash
# Check if GPU is detected
lspci | grep -i nvidia

# Install NVIDIA drivers
sudo apt install -y nvidia-driver-525 nvidia-utils-525

# Install CUDA toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit-12-2

# Reboot
sudo reboot

# Verify installation
nvidia-smi
```

### 4. Clone and Setup Project

```bash
cd /home/ubuntu
git clone https://github.com/yourusername/ayka_lead_gen.git
cd ayka_lead_gen

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r poc_requirements.txt
pip install -r agent_requirements.txt

# For GPU: Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 5. Pre-download AI Models

```bash
# Activate venv
source venv/bin/activate

# Download Whisper models (choose size based on needs)
python -c "import whisper; whisper.load_model('base')"
# Models: tiny (39MB), base (145MB), small (466MB), medium (1.5GB), large (3GB)

# Download pyannote models (requires HuggingFace token)
# Get token from: https://huggingface.co/settings/tokens
export HF_TOKEN=hf_your_token_here

python -c "
from pyannote.audio import Pipeline
Pipeline.from_pretrained('pyannote/speaker-diarization@2.1', use_auth_token='${HF_TOKEN}')
"
```

### 6. Setup Database

```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE ayka;
CREATE USER ayka WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ayka TO ayka;
\q

# Run migrations
cd backend
alembic upgrade head
```

### 7. Configure Environment

```bash
# Create .env file in project root
cat > .env << 'EOF'
DATABASE_URL=postgresql://ayka:your_secure_password@localhost:5432/ayka
OPENAI_API_KEY=sk-...
EMAIL_USER=your@gmail.com
EMAIL_PASSWORD=your_app_password
SERPER_API_KEY=...

# STT Configuration
STT_PROVIDER=local_whisper
WHISPER_MODEL_SIZE=base
ENABLE_DIARIZATION=true

# HuggingFace token for pyannote
HF_TOKEN=hf_...
EOF
```

### 8. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Set API URL
echo "NEXT_PUBLIC_API_URL=http://your-ec2-ip:8000" > .env.production
```

### 9. Setup PM2 Process Manager

```bash
sudo npm install -g pm2

# Start backend
cd /home/ubuntu/ayka_lead_gen
pm2 start "uvicorn backend.app.main:app --host 0.0.0.0 --port 8000" --name backend

# Start frontend
cd frontend
pm2 start "npm start" --name frontend

# Save PM2 config
pm2 save
pm2 startup
```

### 10. Setup Nginx Reverse Proxy

```bash
sudo tee /etc/nginx/sites-available/lyncsea << 'EOF'
server {
    listen 80;
    server_name your-domain.com;  # or EC2 IP

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Increase timeout for long transcriptions
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }

    # WebSocket support (if needed)
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/lyncsea /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔄 Switching Between Providers

### Use Local Whisper (EC2 with GPU)

```bash
# In .env
STT_PROVIDER=local_whisper
WHISPER_MODEL_SIZE=base
ENABLE_DIARIZATION=true

# Restart backend
pm2 restart backend
```

### Use AssemblyAI (Any EC2, even t2.micro)

```bash
# In .env
STT_PROVIDER=assemblyai
ASSEMBLYAI_API_KEY=your_key
ENABLE_DIARIZATION=true

# Restart backend
pm2 restart backend
```

---

## 📊 Performance Comparison

### Local Whisper (GPU)
- **Speed**: 30-60s for 5min audio
- **Cost**: $0.50/hour instance = ~$360/month
- **Pros**: No per-minute costs, offline, private
- **Cons**: Need GPU, higher fixed cost

### AssemblyAI (Cloud)
- **Speed**: 60-120s for 5min audio
- **Cost**: $0.0125/min = $6.25 per 1000 minutes
- **Pros**: No GPU needed, pay-as-you-go, scales automatically
- **Cons**: Per-use costs, requires internet, data sent to third party

**Break-even point**: ~30,000 minutes/month

---

## 🎯 Recommended Setup

### For MVP / Low Volume (<5,000 min/month)
✅ Use **AssemblyAI** on small EC2 instance (t3.medium)
- Total cost: ~$30-50/month

### For Production / High Volume (>30,000 min/month)
✅ Use **Local Whisper** on GPU instance
- Total cost: ~$360-500/month

### Hybrid Approach
- Dev: Local Whisper on CPU (slow but free)
- Staging: AssemblyAI (fast, cheap for testing)
- Production: GPU instance with local Whisper

---

## 🔒 Security Checklist

- [ ] Change default PostgreSQL password
- [ ] Set strong SECRET_KEY in .env
- [ ] Setup firewall (ufw)
- [ ] Use HTTPS (Let's Encrypt)
- [ ] Restrict SSH to your IP
- [ ] Regular security updates
- [ ] Backup database daily
- [ ] Monitor logs with CloudWatch

---

## 📝 Monitoring

```bash
# Check backend logs
pm2 logs backend

# Check system resources
htop

# Check GPU usage (GPU instance only)
nvidia-smi

# Check nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🚨 Troubleshooting

### Whisper model download fails
```bash
# Set proxy if needed
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port

# Or download manually
wget https://openaipublic.azureedge.net/main/whisper/models/d3dd57d32accea0b295c96e26691aa14d8822fac51f9dd52892c9906c49af82b/base.pt
mv base.pt ~/.cache/whisper/
```

### Pyannote authentication error
```bash
# Accept user agreement: https://huggingface.co/pyannote/speaker-diarization
# Generate new token: https://huggingface.co/settings/tokens
```

### Out of memory
```bash
# Use smaller Whisper model
STT_PROVIDER=local_whisper
WHISPER_MODEL_SIZE=tiny  # or base

# Or increase swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## ✅ Summary

**You now have:**
1. ✅ Feature flag to switch between local/cloud STT
2. ✅ Full speaker diarization in both modes
3. ✅ EC2 deployment guide with GPU support
4. ✅ Cost optimization strategies
5. ✅ Production-ready setup with Nginx + PM2

**To deploy:**
1. Launch EC2 instance (GPU if using local Whisper)
2. Follow steps 1-10 above
3. Set `STT_PROVIDER` in .env
4. Done! 🚀