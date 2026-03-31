# 🚀 Quick Start Guide

## ✅ All Errors Fixed!

The project has been configured and all dependencies are installed.

## 🎯 How to Run the Project

### Option 1: Automated Startup (Easiest!)

Simply double-click or run:
```powershell
.\START_PROJECT.ps1
```

This will open 2 PowerShell windows:
- **Window 1**: Backend (Flask API) on port 5000
- **Window 2**: Frontend (React App) on port 3000

### Option 2: Manual Startup

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python app.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

## 🌐 Access the Application

After starting (wait 10-15 seconds):

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## 📝 What Was Fixed

1. ✅ Removed unused numpy dependency from backend
2. ✅ Installed Flask and flask-cors successfully
3. ✅ Created automated startup scripts
4. ✅ Configured proper virtual environment for Python
5. ✅ Installed all npm dependencies for frontend

## 🎮 How to Use

1. **Login Page**: Enter any username
2. **Predict Page**: 
   - Fill in location details
   - Click "Get Location" to auto-fill coordinates
   - Click "Predict Hotspot"
3. **View Results**: See hotspot status and severity level
4. **Map Page**: View all predictions on interactive map
5. **About Page**: Learn about the project

## 🛑 How to Stop

Press `Ctrl+C` in each PowerShell window or simply close them.

## ⚠️ Troubleshooting

**If backend doesn't start:**
- Check if Python is installed: `python --version`
- Make sure you're in the backend directory
- Run: `.\venv\Scripts\python.exe app.py`

**If frontend doesn't start:**
- Check if Node.js is installed: `node --version`
- Run: `npm install` again
- Then: `npm run dev`

**Port already in use:**
- Kill existing process on port 5000 or 3000
- Or restart your computer

## 📞 Need Help?

Check the main README.md for detailed documentation.
