@echo off
echo =================================================
echo Fixing GitHub Large File Error (History Rewrite)
echo =================================================

echo.
echo Step 1: Soft resetting recent commits...
echo (This keeps your files but removes the commit history that contained the large file)
:: Try resetting back 3 steps to be safe. Errors are ignored if history is shorter.
git reset --soft HEAD~3 2>nul || git reset --soft HEAD~2 2>nul || git reset --soft HEAD~1 2>nul

echo.
echo Step 2: Explicitly removing the large model from Git tracking...
git rm --cached ai/model/certificate_forgery_model.h5 2>nul

echo.
echo Step 3: Re-staging files...
:: .gitignore is now active, so the large file won't be added back
git add .

echo.
echo Step 4: Creating a new, clean commit...
git commit -m "Final project release (Model excluded)"

echo.
echo Step 5: Force pushing to GitHub...
echo (You may need to enter your credentials again)
git push -u origin main --force

echo.
echo =================================================
echo Done! If you see 'Writing objects: 100%' without errors, it worked.
echo =================================================
pause
