@echo off
echo ===========================================
echo Git Push Script (Authenticated)
echo ===========================================

echo 1. Configuring Git identity...
git config user.email "yashaswiniganeeb24@gmail.com"
git config user.name "Yashaswini134"

echo 2. Adding files...
git add .

echo 3. Committing files...
git commit -m "Final project implementation"

echo 4. Setting branch and remote...
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/Yashaswini134/Academic-records-validator-1.git

echo 5. Pushing to GitHub...
echo    (If a window pops up asking for a password/token, please enter it)
git push -u origin main

echo.
echo Done!
pause
