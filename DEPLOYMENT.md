# Deployment Guide

This guide shows how to deploy the MisiPwGen web interface to various free hosting platforms.

## 🚀 Quick Deploy Options

### Option 1: Render.com (Recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Steps:**

1. Fork this repository on GitHub (if you haven't already)
2. Sign up for a free account at [render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure the service:
   - **Name**: `misipwgen` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn webapp:app`
   - **Instance Type**: Free
6. Click "Create Web Service"

Your app will be available at: `https://your-app-name.onrender.com`

### Option 2: Railway.app

**Steps:**

1. Sign up for a free account at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will automatically detect the configuration from `railway.json`
5. Your app will be deployed automatically

Your app will be available at: `https://your-app-name.railway.app`

### Option 3: Fly.io

**Steps:**

1. Install flyctl: `curl -L https://fly.io/install.sh | sh`
2. Sign up: `flyctl auth signup`
3. Create app: `flyctl launch`
4. Deploy: `flyctl deploy`

### Option 4: PythonAnywhere

**Steps:**

1. Sign up for a free account at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Open a Bash console and clone your repository:
   ```bash
   git clone https://github.com/yourusername/misipwgen.git
   cd misipwgen
   pip install --user -r requirements.txt
   ```
3. Go to the "Web" tab and click "Add a new web app"
4. Choose "Manual configuration" and Python 3.10
5. In the "Code" section:
   - Source code: `/home/yourusername/misipwgen`
   - Working directory: `/home/yourusername/misipwgen`
6. Edit the WSGI configuration file and replace it with:
   ```python
   import sys
   import os

   path = '/home/yourusername/misipwgen'
   if path not in sys.path:
       sys.path.append(path)

   os.chdir(path)
   from webapp import app as application
   ```
7. Reload the web app

Your app will be available at: `https://yourusername.pythonanywhere.com`

## 🔧 Environment Variables

For all platforms, you can optionally set:

- `PORT` - Port number (usually set automatically by the platform)
- `DEBUG` - Set to `false` for production (default: `true` in development)

## 📦 Files for Deployment

The repository includes these deployment configuration files:

- `requirements.txt` - Python dependencies with gunicorn
- `Procfile` - For Heroku-compatible platforms
- `render.yaml` - For Render.com
- `railway.json` - For Railway.app

## 🔄 Updating Your Deployment

Most platforms support automatic deployment:

1. Push changes to your GitHub repository
2. The platform will automatically rebuild and redeploy

Or manually trigger a deployment from the platform's dashboard.

## 💰 Cost

All the options listed above have **free tiers** that are sufficient for this application:

- **Render.com**: Free tier (with 750 hours/month)
- **Railway.app**: Free tier with $5 credit/month
- **Fly.io**: Free tier with 3 shared VMs
- **PythonAnywhere**: Free tier (always-on for one web app)

## 🐛 Troubleshooting

### App crashes on startup
- Check that `requirements.txt` includes all dependencies
- Verify the start command is `gunicorn webapp:app`
- Check platform logs for specific error messages

### 502 Bad Gateway
- The app may still be starting up (wait 1-2 minutes)
- Check that the PORT environment variable is properly configured

### Static files not loading
- Ensure `templates/` and `static/` directories are included in your repository
- Check that Flask is configured to serve static files

## 🌐 Custom Domain

Most platforms support custom domains:

- **Render**: Project Settings → Custom Domain
- **Railway**: Project Settings → Domains
- **Fly.io**: `flyctl domains add yourdomain.com`

## 📚 Additional Resources

- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Fly.io Docs](https://fly.io/docs)
- [PythonAnywhere Help](https://help.pythonanywhere.com)
