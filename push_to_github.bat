@echo off
echo ==========================================
echo Pushing Project to GitHub
echo ==========================================

echo 1. Configuring Git User...
git config user.email "yashaswiniganeeb24@gmail.com"
git config user.name "Yashaswini134"

echo 2. Setting up Remote Repository...
git remote remove origin 2>nul
git remote add origin https://github.com/Yashaswini134/Academic-records-validator-1.git

echo 3. Staging Files (This may take a moment)...
git add .

echo 4. Committing Changes...
git commit -m "Final project implementation"

echo 5. Pushing to GitHub...
echo    NOTE: If a popup appears, please enter your GitHub credentials.
git branch -M main
git push -u origin main

echo.
echo ==========================================
echo Done!
echo ==========================================
pause
