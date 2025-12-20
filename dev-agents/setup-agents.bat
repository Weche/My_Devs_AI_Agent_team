@echo off
echo Installing dependencies for all Dev Agents...
echo.

echo [1/3] Installing Frontend Agent dependencies...
cd frontend-agent
call npm install
cd ..

echo.
echo [2/3] Installing Backend Agent dependencies...
cd backend-agent
call npm install
cd ..

echo.
echo [3/3] Installing Database Agent dependencies...
cd database-agent
call npm install
cd ..

echo.
echo ✅ All agents ready!
echo.
echo Now you can run: npm start
pause
