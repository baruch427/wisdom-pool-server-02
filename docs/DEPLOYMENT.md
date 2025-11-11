# 🚀 Wisdom Pool Server Deployment Guide

## Quick Start Options

### Option 1: Google Cloud Run (Recommended)

**Pros:** Auto-scaling, pay-per-use, integrated with Firebase, enterprise-grade
**Cost:** ~$0-5/month for light usage

1. **Install Google Cloud SDK**:
   ```bash
   # Download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate**:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

3. **Deploy**:
   ```powershell
   cd "c:\Users\Home\Dropbox\___WisdomPools\pool-server"
   .\deploy\deploy-cloudrun.ps1
   ```

### Option 2: Railway (Easiest)

**Pros:** Extremely simple, GitHub integration, automatic SSL
**Cost:** Free tier available, then $5/month

1. **Connect GitHub**: Push your code to GitHub
2. **Deploy**: Visit [railway.app](https://railway.app) → "Deploy from GitHub"
3. **Configure**: Upload `firebase-credentials.json` as a file
4. **Environment Variables**:
   ```
   FIRESTORE_PROJECT_ID=wisdompools
   FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
   ENVIRONMENT=production
   ```

### Option 3: Render

**Pros:** Simple setup, automatic deployments, good free tier
**Cost:** Free tier available

1. **Connect GitHub**: Push code to GitHub
2. **Deploy**: Visit [render.com](https://render.com) → "New Web Service"
3. **Upload Credentials**: Add `firebase-credentials.json` as a secret file

### Option 4: DigitalOcean App Platform

**Pros:** Simple, good performance, predictable pricing
**Cost:** $5/month minimum

## Pre-Deployment Checklist

- [ ] Firebase project created and configured
- [ ] `firebase-credentials.json` file downloaded
- [ ] Environment variables configured
- [ ] Dependencies listed in `requirements-prod.txt`
- [ ] Code committed to Git repository

## Environment Variables for Production

| Variable | Value | Required |
|----------|-------|----------|
| `ENVIRONMENT` | `production` | ✅ |
| `DEBUG` | `false` | ✅ |
| `FIRESTORE_PROJECT_ID` | `wisdompools` | ✅ |
| `FIREBASE_CREDENTIALS_PATH` | `firebase-credentials.json` | ✅ |
| `HOST` | `0.0.0.0` | ✅ |
| `PORT` | Platform-specific | Auto |

## Post-Deployment Testing

1. **Health Check**: `GET https://your-app.com/health`
2. **API Docs**: `https://your-app.com/docs`
3. **Create Test Drop**:
   ```bash
   curl -X POST https://your-app.com/api/v1/drops \
     -H "Content-Type: application/json" \
     -d '{"title":"Test","content":{"type":"portable_text","body":"Hello World!"},"source":"api","author":"Test","tags":["test"]}'
   ```

## Domain Setup (Optional)

1. **Purchase Domain**: Use any domain registrar
2. **Configure DNS**: Point your domain to the deployment platform
3. **SSL Certificate**: Most platforms provide free SSL automatically

## Monitoring & Maintenance

- **Logs**: Available in your platform's dashboard
- **Firebase Console**: Monitor database usage
- **Uptime Monitoring**: Consider UptimeRobot or similar
- **Error Tracking**: Consider Sentry for production error monitoring

## Cost Estimates

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| Railway | 500 hours/month | $5/month | Hobby projects |
| Render | 750 hours/month | $7/month | Small apps |
| Google Cloud Run | Generous free tier | Pay-per-use | Production apps |
| DigitalOcean | None | $5/month | Predictable costs |

## Security Notes

- ✅ Firebase credentials are properly secured
- ✅ HTTPS enforced by platforms
- ✅ Environment variables used for secrets
- ✅ Non-root user in Docker container
- ⚠️ Add authentication before going public
- ⚠️ Configure CORS for your domain
- ⚠️ Set up monitoring and alerts

## Next Steps After Deployment

1. **Add Authentication**: Integrate with Clerk or Auth0
2. **Custom Domain**: Point your domain to the deployment
3. **CI/CD**: Set up automatic deployments from GitHub
4. **Monitoring**: Add error tracking and performance monitoring
5. **Scaling**: Configure auto-scaling based on traffic