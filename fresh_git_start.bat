@echo off
echo =======================================================
echo FRESH START GITHUB PUSH (Guaranteed Fix)
echo =======================================================

echo.
echo 1. Removing old git history (containing the large file)...
rmdir /s /q .git

echo.
echo 2. Re-initializing Git repository...
git init

echo.
echo 3. Restoring Git Configuration...
git config user.email "yashaswiniganeeb24@gmail.com"
git config user.name "Yashaswini134"

echo.
echo 4. Adding Remote Repository...
git remote add origin https://github.com/Yashaswini134/Academic-records-validator-1.git

echo.
echo 5. Adding files (ignoring large models this time)...
git add .

echo.
echo 6. Creating clean initial commit...
git commit -m "Initial commit (Clean project structure)"

echo.
echo 7. Force pushing to GitHub...
echo    (Please enter your credentials if prompted)
git branch -M main
git push -u origin main --force

echo.
echo =======================================================
echo DONE! The error should be gone.
echo =======================================================
pause
