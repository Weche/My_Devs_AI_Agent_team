@echo off
echo Starting all 3 Dev Agents...

cd dev-agents\frontend-agent
start "Frontend Agent (Port 3001)" cmd /k npm run dev

cd ..\backend-agent
start "Backend Agent (Port 3002)" cmd /k npm run dev

cd ..\database-agent
start "Database Agent (Port 3003)" cmd /k npm run dev

cd ..\..
echo All agents started in separate windows!
echo Now run: python src\telegram\bot.py
