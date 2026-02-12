@echo off
echo ========================================
echo   RESUME ANALYZER - DEPLOYMENT SCRIPT
echo ========================================
echo.

echo Step 1: Installing Vercel CLI...
call npm install -g vercel
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Vercel CLI
    pause
    exit /b 1
)
echo ✓ Vercel CLI installed
echo.

echo Step 2: Installing Railway CLI...
call npm install -g @railway/cli
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Railway CLI
    pause
    exit /b 1
)
echo ✓ Railway CLI installed
echo.

echo ========================================
echo   FRONTEND DEPLOYMENT (Vercel)
echo ========================================
echo.

cd resume-analyzer-frontend
echo Current directory: %cd%
echo.

echo Building frontend...
call npm install
if %errorlevel% neq 0 (
    echo ERROR: npm install failed
    pause
    exit /b 1
)

call npm run build
if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo ✓ Frontend built successfully
echo.

echo ========================================
echo   DEPLOYING TO VERCEL
echo ========================================
echo.
echo Please follow the Vercel prompts:
echo - Login when prompted
echo - Accept default settings
echo - Note the deployment URL
echo.
pause

call vercel --prod
echo.
echo ✓ Frontend deployed to Vercel!
echo.

cd ..

echo ========================================
echo   BACKEND DEPLOYMENT (Railway)
echo ========================================
echo.

cd resume-analyzer-backend
echo Current directory: %cd%
echo.

echo ========================================
echo   DEPLOYING TO RAILWAY
echo ========================================
echo.
echo Please follow the Railway prompts:
echo - Login when prompted
echo - Create new project
echo - Note the deployment URL
echo.
pause

call railway login
call railway init
call railway up
echo.
echo ✓ Backend deployed to Railway!
echo.

cd ..

echo ========================================
echo   DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Your application is now live!
echo.
echo Next steps:
echo 1. Note your frontend URL from Vercel
echo 2. Note your backend URL from Railway
echo 3. Update environment variables in Railway dashboard
echo 4. Update API URL in frontend and redeploy
echo.
echo See DEPLOYMENT_INSTRUCTIONS.md for details
echo.
pause
