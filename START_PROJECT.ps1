Write-Host "Starting Crime Hotspot Predictor..." -ForegroundColor Cyan

$backendPath = "C:\Users\Aayush Tolmare\Desktop\EDAI_NEW2\crime-hotspot-predictor\backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; .\venv\Scripts\Activate.ps1; python app.py"

Start-Sleep -Seconds 3

$frontendPath = "C:\Users\Aayush Tolmare\Desktop\EDAI_NEW2\crime-hotspot-predictor\frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev"

Write-Host "Servers starting! Wait 15 seconds then open http://localhost:3000" -ForegroundColor Green
