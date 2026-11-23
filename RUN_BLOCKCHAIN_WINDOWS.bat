@echo off
npm run compile
npm run deploy
call .venv\Scripts\activate.bat
set PYTHONPATH=.
python -m backend.main --events 5000 --batch-sizes 25,50,100,250,500,1000,2500,5000
npm run anchor
pause
