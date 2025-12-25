# iOps Production Deployment Guide

This guide covers deploying the iOps platform to production using Vercel (frontend) and Render (backend with PostgreSQL).

## Prerequisites

- GitHub account with the repository pushed
- Vercel account (free tier available)
- Render account (free tier available)
- Domain name (optional, for custom domain)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                         │
│                 https://your-app.vercel.app                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS API Calls
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Render)                          │
│              https://iops-backend.onrender.com               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                PostgreSQL Database (Render)                  │
│                    iops_production                           │
└─────────────────────────────────────────────────────────────┘
```

## Step 1: Deploy Backend to Render

### Option A: Using Render Blueprint (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Select the repository containing `backend/render.yaml`
5. Render will automatically create:
   - Web service for the backend
   - PostgreSQL database
6. Configure environment variables in Render dashboard:
   - `GROQ_API_KEY`: Your Groq API key
   - `RESEND_API_KEY`: Your Resend API key
   - `CORS_ORIGINS`: Your frontend URL (e.g., `https://your-app.vercel.app`)
   - `FRONTEND_URL`: Your frontend URL

### Option B: Manual Setup

1. **Create PostgreSQL Database:**
   - Go to Render Dashboard → "New" → "PostgreSQL"
   - Name: `iops-db`
   - Database: `iops_production`
   - User: `iops_user`
   - Region: Oregon (or closest to your users)
   - Plan: Free
   - Click "Create Database"
   - Copy the "Internal Database URL"

2. **Create Web Service:**
   - Go to Render Dashboard → "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - Name: `iops-backend`
     - Root Directory: `backend`
     - Runtime: Python 3
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add Environment Variables:
     - `DATABASE_URL`: (paste Internal Database URL from step 1)
     - `SECRET_KEY`: (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
     - `GROQ_API_KEY`: Your Groq API key
     - `RESEND_API_KEY`: Your Resend API key
     - `CORS_ORIGINS`: `https://your-app.vercel.app`
     - `FRONTEND_URL`: `https://your-app.vercel.app`
     - `ENVIRONMENT`: `production`
     - `DEBUG`: `false`
     - `SEND_VERIFICATION_EMAILS`: `true`

3. Click "Create Web Service"

## Step 2: Deploy Frontend to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. Add Environment Variables:
   - `VITE_API_URL`: Your Render backend URL (e.g., `https://iops-backend.onrender.com`)
6. Click "Deploy"

## Step 3: Configure CORS

After both services are deployed:

1. Go to Render Dashboard → Your backend service → Environment
2. Update `CORS_ORIGINS` to include your Vercel URL:
   ```
   https://your-app.vercel.app,https://your-custom-domain.com
   ```
3. Update `FRONTEND_URL` to your Vercel URL
4. Click "Save Changes" (service will redeploy)

## Step 4: Custom Domain Setup (Optional)

### Frontend (Vercel)

1. Go to Vercel Dashboard → Your project → Settings → Domains
2. Add your custom domain (e.g., `app.yourdomain.com`)
3. Follow Vercel's DNS configuration instructions
4. SSL certificate is automatically provisioned

### Backend (Render)

1. Go to Render Dashboard → Your service → Settings
2. Scroll to "Custom Domains"
3. Add your custom domain (e.g., `api.yourdomain.com`)
4. Follow Render's DNS configuration instructions
5. SSL certificate is automatically provisioned

### Update CORS After Custom Domain

Update the `CORS_ORIGINS` environment variable to include your custom domains:
```
https://app.yourdomain.com,https://your-app.vercel.app
```

## Environment Variables Reference

### Backend (Render)

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes (auto-set by Render) |
| `SECRET_KEY` | JWT signing key | Yes |
| `GROQ_API_KEY` | Groq AI API key | Yes |
| `CORS_ORIGINS` | Allowed frontend origins | Yes |
| `FRONTEND_URL` | Frontend URL for email links | Yes |
| `RESEND_API_KEY` | Email service API key | Yes |
| `ENVIRONMENT` | `production` | Yes |
| `DEBUG` | `false` | Yes |
| `SEND_VERIFICATION_EMAILS` | `true` | Yes |

### Frontend (Vercel)

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_URL` | Backend API URL | Yes |

## SSL/TLS Configuration

Both Vercel and Render automatically provision and renew SSL certificates via Let's Encrypt. No manual configuration is required.

- All traffic is served over HTTPS
- TLS 1.2+ is enforced
- HTTP requests are automatically redirected to HTTPS

## Health Checks

The backend exposes a health check endpoint at `/health`:

```bash
curl https://your-backend.onrender.com/health
# Response: {"status": "healthy", "sessions": 0}
```

Render automatically monitors this endpoint and will restart the service if it becomes unhealthy.

## Troubleshooting

### Backend Not Starting

1. Check Render logs for errors
2. Verify all required environment variables are set
3. Ensure `DATABASE_URL` is correctly formatted

### CORS Errors

1. Verify `CORS_ORIGINS` includes your frontend URL
2. Ensure the URL doesn't have a trailing slash
3. Check that the protocol matches (https vs http)

### Database Connection Issues

1. Verify `DATABASE_URL` is set correctly
2. Check if the database is running in Render dashboard
3. Ensure the database and web service are in the same region

### Frontend API Calls Failing

1. Verify `VITE_API_URL` is set correctly in Vercel
2. Check browser console for CORS errors
3. Ensure the backend is running and healthy

## Monitoring

### Render

- View logs: Dashboard → Service → Logs
- View metrics: Dashboard → Service → Metrics
- Set up alerts: Dashboard → Service → Settings → Notifications

### Vercel

- View deployments: Dashboard → Project → Deployments
- View analytics: Dashboard → Project → Analytics
- View logs: Dashboard → Project → Functions (for serverless functions)

## Scaling

### Free Tier Limitations

- **Render Free**: Service spins down after 15 minutes of inactivity
- **Vercel Free**: 100GB bandwidth/month, serverless function limits

### Upgrading

- **Render Starter ($7/month)**: Always-on service, more resources
- **Vercel Pro ($20/month)**: More bandwidth, team features

## Security Checklist

- [ ] `SECRET_KEY` is a strong, unique value
- [ ] `DEBUG` is set to `false`
- [ ] `CORS_ORIGINS` only includes trusted domains
- [ ] Database credentials are not exposed
- [ ] API keys are stored as environment variables
- [ ] HTTPS is enforced on all endpoints
