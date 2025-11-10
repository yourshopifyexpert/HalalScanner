# Get Your Universal URL in 3 Minutes

## Option 1: Railway.app (Recommended - Easiest)

### Step 1: Sign Up
Go to **https://railway.app/** and sign up with GitHub

### Step 2: Deploy
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose **`yourshopifyexpert/HalalScanner`**
4. Select branch: **`claude/halal-classifier-system-design-011CUztKVjzgBc8vZmjS5RHz`**
5. Railway auto-detects `railway.json` and deploys automatically

### Step 3: Get Your URL
Your app will be live at: **`https://halalscanner-[random].up.railway.app`**

The URL will appear in your Railway dashboard under "Deployments"

---

## Option 2: Render.com (Free Tier)

### Step 1: Sign Up
Go to **https://render.com/** and sign up

### Step 2: Deploy
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub account
3. Select **`yourshopifyexpert/HalalScanner`**
4. Select branch: **`claude/halal-classifier-system-design-011CUztKVjzgBc8vZmjS5RHz`**
5. Render auto-detects `render.yaml` and configures everything

### Step 3: Get Your URL
Your app will be live at: **`https://halalscanner-[random].onrender.com`**

---

## Testing Your Deployed App

Once deployed, test with these commands:

```bash
# Replace with your actual deployed URL
export API_URL="https://your-app.railway.app"

# Health check
curl $API_URL/health

# Test scan
curl -X POST $API_URL/api/v1/scan/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "ocr_text": "Ingredients: Water, Sugar, Pork Gelatin, Salt"
  }'
```

Expected response:
```json
{
  "verdict": "HARAM",
  "confidence": 0.99,
  "ingredients": [
    {
      "name": "pork gelatin",
      "status": "HARAM",
      "reason": "Pork-derived ingredients are haram"
    }
  ]
}
```

---

## Web Interface

Once deployed, you can also access the web interface directly by visiting your URL in a browser:
**`https://your-app.railway.app/`**

This provides a visual interface to scan ingredients without using curl commands.

---

## Deployment Status

All deployment configuration files have been committed and pushed to branch:
`claude/halal-classifier-system-design-011CUztKVjzgBc8vZmjS5RHz`

Files ready for deployment:
- `railway.json` - Railway configuration
- `render.yaml` - Render configuration
- `Procfile` - Heroku configuration
- `vercel.json` - Vercel configuration
- All backend code and database models
- Web interface at `/backend/app/static/index.html`

---

## What's Included

Your deployed app includes:
- Full FastAPI backend with 8 REST API endpoints
- SQLite database with ingredient rules engine
- 8 classification rules (haram blacklist, halal whitelist, suspicious patterns)
- 15 master ingredients pre-loaded
- Web UI for easy testing
- Automatic ingredient classification
- Confidence scoring
- Evidence-based explanations

---

## Support

If deployment fails:
- **Railway:** Check logs in Dashboard → Deployments → View Logs
- **Render:** Check logs in Dashboard → Your Service → Logs tab

Common issues:
- **Port binding:** Automatically handled by `$PORT` variable
- **Python version:** Set to 3.11 in all configs
- **Database:** Uses SQLite (file-based, no external DB needed)

For detailed deployment options, see `DEPLOYMENT_GUIDE.md`
