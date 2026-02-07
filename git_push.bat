@echo off
echo ===========================================
echo Git Push Script
echo ===========================================

echo 1. Initializing Git...
git init

echo 2. Removing old remote (if any)...
git remote remove origin 2>nul

echo 3. Adding remote origin...
git remote add origin https://github.com/Yashaswini134/Academic-records-validator-1.git

echo 4. Adding files...
git add .

echo 5. Committing...
git commit -m "Final project implementation (Cleaned)"

echo 6. Renaming branch to main...
git branch -M main

echo 7. Pushing to GitHub...
echo    (Please enter credentials in the pop-up if requested)
git push -u origin main

echo.
echo Done!
pause
