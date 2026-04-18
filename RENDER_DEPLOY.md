# Render Deployment Guide

## Step-by-Step Instructions

### 1. **Connect Your GitHub Repository to Render**
   - Go to https://render.com
   - Sign up or log in with your GitHub account
   - Connect your GitHub account to Render

### 2. **Create Backend Service**
   - Click "New" → "Web Service"
   - Select your GitHub repository: `Student-portal-management-system`
   - Configure:
     - **Name**: `student-portal-backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn backend.app:app`
     - **Region**: Choose your preferred region (e.g., Oregon, Frankfurt, Singapore)
     - **Plan**: Free (or Paid for better performance)

### 3. **Set Backend Environment Variables**
   In the Render dashboard for the backend service:
   - Click "Environment"
   - Add these variables:
     ```
     FLASK_ENV=production
     JWT_SECRET_KEY=generate_a_strong_random_key_here
     DATABASE_URL=sqlite:////mnt/data/database.db (for Free plan - data will persist)
     ```

### 4. **Create Frontend Service**
   - Click "New" → "Static Site"
   - Select your GitHub repository again
   - Configure:
     - **Name**: `student-portal-frontend`
     - **Build Command**: `cd frontend && npm install && npm run build`
     - **Publish Directory**: `frontend/build`
     - **Root Directory**: `.` (leave empty if not needed)

### 5. **Set Frontend Environment Variables**
   In the Render dashboard for the frontend service:
   - Click "Environment"
   - Add this variable:
     ```
     REACT_APP_API_URL=https://your-backend-service-name.onrender.com
     ```
   Replace `your-backend-service-name` with your actual backend service name on Render

### 6. **Configure CORS for Backend**
   - The backend already has CORS configured with `CORS(app)`
   - Make sure your frontend URL is properly set in environment variables

### 7. **Deploy**
   - Click "Deploy" button
   - Wait for both services to build and deploy
   - Once complete, you'll get URLs for both services

## 🚀 **Access Your Application**

- **Frontend**: `https://student-portal-frontend.onrender.com`
- **Backend API**: `https://your-backend-service-name.onrender.com`

## 🔐 **Demo Credentials for Render**

Use these to test the deployed application:

**Admin:**
- Email: `admin@school.com`
- Password: `password`

**Teacher:**
- Email: `teacher@school.com`
- Password: `password`

**Parent:**
- Email: `parent@school.com`
- Password: `password`

## ⚠️ **Important Notes**

1. **Free Tier Limitations:**
   - Services spin down after 15 minutes of inactivity
   - Limited to 100GB data transfers per month
   - 0.5 GB RAM
   - For production use, upgrade to a paid plan

2. **Database Persistence:**
   - Free tier uses SQLite with Render's `/mnt/data` for persistence
   - Data survives service restarts
   - For production, consider upgrading to PostgreSQL

3. **Build Time:**
   - Initial deployment may take 5-10 minutes
   - Subsequent deployments are faster with caching

4. **Updates:**
   - Push code changes to GitHub
   - Render automatically redeploys when you push to main branch
   - Disable auto-deploy and deploy manually if needed

## 🔧 **Troubleshooting**

### Frontend shows blank page or 404
- Check REACT_APP_API_URL environment variable
- Verify backend is running and accessible
- Check browser console for CORS errors

### Backend API errors
- Check backend environment variables
- Review Render logs for errors
- Verify Flask app is running correctly

### Can't log in
- Use credentials from demo data
- Check backend logs for authentication errors
- Ensure JWT_SECRET_KEY is set

## 📚 **Additional Resources**
- Render Docs: https://render.com/docs
- Flask Documentation: https://flask.palletsprojects.com
- React Documentation: https://react.dev
