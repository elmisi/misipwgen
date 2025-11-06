# GitHub Actions Deployment Workflows

This directory contains automated deployment workflows for various platforms.

## Available Workflows

### 1. Deploy to Render (`deploy-render.yml`)

**Easiest option** - Uses a webhook to trigger deployment.

#### Setup:

1. Create a web service on [Render.com](https://render.com)
2. In your Render dashboard, go to your service → Settings
3. Copy the "Deploy Hook" URL
4. In GitHub: Settings → Secrets and variables → Actions → New repository secret
   - Name: `RENDER_DEPLOY_HOOK`
   - Value: Your deploy hook URL

#### Trigger:
- Automatically on push to `main` branch
- Manually via "Actions" tab → "Deploy to Render" → "Run workflow"

---

### 2. Deploy to Railway (`deploy-railway.yml`)

Uses Railway CLI for deployment.

#### Setup:

1. Create a project on [Railway.app](https://railway.app)
2. Get your Railway token:
   - Go to Account Settings → Tokens
   - Create a new token
3. Get your service ID from the Railway dashboard URL
4. Add GitHub secrets:
   - `RAILWAY_TOKEN`: Your Railway token
   - `RAILWAY_SERVICE_ID`: Your service ID (optional if using railway.json)

#### Trigger:
- Automatically on push to `main` branch
- Manually via "Actions" tab → "Deploy to Railway" → "Run workflow"

---

### 3. Deploy to Fly.io (`deploy-fly.yml`)

Uses Fly.io CLI for deployment.

#### Setup:

1. Install flyctl locally: `curl -L https://fly.io/install.sh | sh`
2. Sign up: `flyctl auth signup`
3. Create app: `flyctl launch` (use the generated fly.toml)
4. Get your API token: `flyctl auth token`
5. Add GitHub secret:
   - Name: `FLY_API_TOKEN`
   - Value: Your Fly.io API token

#### Trigger:
- Automatically on push to `main` branch
- Manually via "Actions" tab → "Deploy to Fly.io" → "Run workflow"

---

## How to Choose

| Platform | Setup Difficulty | Free Tier | Auto-sleep | Custom Domain |
|----------|-----------------|-----------|------------|---------------|
| **Render** | ⭐ Easy | 750h/month | Yes (after 15min) | Yes |
| **Railway** | ⭐⭐ Medium | $5 credit/month | No | Yes |
| **Fly.io** | ⭐⭐⭐ Advanced | 3 VMs free | Yes | Yes |

**Recommendation**: Start with **Render** (simplest setup)

---

## Testing Workflows

You can test any workflow manually:

1. Go to the "Actions" tab in your GitHub repository
2. Select the workflow you want to run
3. Click "Run workflow"
4. Choose the branch (usually `main`)
5. Click "Run workflow"

---

## Workflow Status

Check deployment status:
- Go to "Actions" tab in GitHub
- Click on the latest workflow run
- View logs and status

---

## Troubleshooting

### "Secret not found" error
- Make sure you've added the required secrets in GitHub Settings → Secrets and variables → Actions

### Deployment fails
- Check the workflow logs in the Actions tab
- Verify your platform credentials are correct
- Ensure your platform service is properly configured

### Manual deployment still works but GitHub Action fails
- Check if the secret values are correct
- Verify the workflow has permission to access secrets
- Review platform API token permissions

---

## Disabling Workflows

If you want to use only one platform:

1. Go to `.github/workflows/`
2. Delete or rename (add `.disabled` extension) the workflows you don't need

Example:
```bash
# Disable Railway deployment
mv deploy-railway.yml deploy-railway.yml.disabled
```

---

## Multiple Environments

To deploy to different environments (staging/production):

1. Duplicate the workflow file
2. Change the branch trigger
3. Use different secrets for each environment

Example:
```yaml
on:
  push:
    branches:
      - staging  # Deploy staging branch to staging environment
```
