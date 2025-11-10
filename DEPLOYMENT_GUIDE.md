# HalalScanner Deployment Guide

## Quick Deploy Options (Free Tier)

### Option 1: Railway.app (Recommended - Easiest)

1. **Sign up at [Railway.app](https://railway.app/)**
2. **Connect your GitHub repository**
3. **Click "New Project" → "Deploy from GitHub repo"**
4. **Select `yourshopifyexpert/HalalScanner`**
5. **Railway auto-detects and deploys!**

Your app will be live at: `https://your-app-name.up.railway.app`

**Configuration:** Already included in `railway.json`

---

### Option 2: Render.com

1. **Sign up at [Render.com](https://render.com/)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repo**
4. **Use these settings:**
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3.11

Your app will be live at: `https://halalscanner.onrender.com`

**Configuration:** Already included in `render.yaml`

---

### Option 3: Fly.io

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login and deploy:**
   ```bash
   fly auth login
   fly launch --name halalscanner
   fly deploy
   ```

Your app will be live at: `https://halalscanner.fly.dev`

---

### Option 4: Heroku

1. **Install Heroku CLI**
2. **Deploy:**
   ```bash
   heroku login
   heroku create halalscanner-api
   git push heroku main
   ```

**Configuration:** Already included in `Procfile`

---

## Environment Variables (Set on Platform)

```bash
DATABASE_URL=sqlite:///./halalscanner.db
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-random-secret-key-here
```

For PostgreSQL (production):
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

---

## Quick Deploy Commands

### Railway (CLI)
```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

### Render (Git Push)
```bash
git add .
git commit -m "Deploy to Render"
git push origin main
# Then link repo in Render dashboard
```

---

## Testing Deployed App

Once deployed, test with:

```bash
# Replace with your deployed URL
export API_URL="https://your-app.railway.app"

# Health check
curl $API_URL/health

# Test scan
curl -X POST $API_URL/api/v1/scan/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "ocr_text": "Water, Sugar, Salt"
  }'
```

---

## Custom Domain (Optional)

After deployment, add your custom domain:
- Railway: Project Settings → Domains
- Render: Settings → Custom Domain
- Fly.io: `fly certs add yourdomain.com`

---

## Monitoring

All platforms provide:
- **Logs** - Real-time application logs
- **Metrics** - CPU, Memory, Request metrics
- **Alerts** - Email notifications on errors

---

## Database Persistence

**For production, upgrade to PostgreSQL:**

1. Add PostgreSQL service on your platform
2. Update `DATABASE_URL` environment variable
3. Backend will automatically use PostgreSQL

---

## Estimated Deployment Time

- **Railway:** 2-3 minutes
- **Render:** 3-5 minutes
- **Fly.io:** 5-7 minutes
- **Heroku:** 5-10 minutes

---

## Need Help?

- Railway: https://docs.railway.app/
- Render: https://render.com/docs
- Fly.io: https://fly.io/docs/
- Heroku: https://devcenter.heroku.com/

**Support:** Check platform-specific documentation for troubleshooting.
