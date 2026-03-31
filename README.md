# 🚨 Crime Hotspot Predictor

A full-stack AI-powered web application that predicts crime hotspots and severity levels based on location and contextual data.

## 🎯 Features

- **Real-time Predictions**: Predict whether a location is a crime hotspot
- **Severity Classification**: Get severity levels (Low, Medium, High, Critical)
- **Interactive Map**: Visualize predictions on a color-coded heatmap
- **Auto-Detection**: Automatic time-based feature extraction
- **Geolocation**: Browser-based location detection
- **Responsive Design**: Beautiful UI with Tailwind CSS and Framer Motion animations

## 🛠️ Tech Stack

### Frontend
- React 18
- Vite
- Tailwind CSS
- React Router
- React Leaflet (Map visualization)
- Framer Motion (Animations)
- Axios (API calls)

### Backend
- Flask (Python)
- Scikit-learn (ML)
- Pandas & NumPy
- Flask-CORS

## 📁 Project Structure

```
crime-hotspot-predictor/
│
├── backend/
│   ├── app.py                  # Flask API server
│   ├── requirements.txt        # Python dependencies
│   └── (model.pkl)            # ML model (optional)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── LoginForm.jsx
│   │   │   ├── InputForm.jsx
│   │   │   ├── ResultCard.jsx
│   │   │   └── HeatMap.jsx
│   │   ├── pages/
│   │   │   ├── PredictPage.jsx
│   │   │   ├── MapPage.jsx
│   │   │   └── AboutPage.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
└── README.md
```

## 🚀 Installation & Setup

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn**
- **pip**

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd crime-hotspot-predictor/backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask server:
   ```bash
   python app.py
   ```

   The backend API will start at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd crime-hotspot-predictor/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will open automatically at `http://localhost:3000`

## 📱 Usage

### Step 1: Login
- Enter your username on the login page
- The current date and time will be automatically detected

### Step 2: Make a Prediction
- Navigate to the **Predict** page
- Fill in the required fields:
  - **City**: Enter the city name
  - **Coordinates**: Enter latitude/longitude or click "Get Location"
  - **Population Density**: Number of people per square km
  - **Previous Crimes in Area**: Historical crime count
  - **Police Station Distance**: Distance in km
  - **Patrol Intensity**: Low/Medium/High
  - **Crime Type**: Select from dropdown
- Time-based fields (Day, Month, Time Slot) are auto-filled
- Click **"Predict Hotspot"**

### Step 3: View Results
- See the **Hotspot Status** (Hotspot or Safe)
- View the **Severity Level** (Low, Medium, High, Critical)
- Results are displayed with color-coded indicators

### Step 4: Explore the Map
- Navigate to the **Map** page
- View all predictions on an interactive map
- Click on markers to see detailed information
- Color legend:
  - 🟢 **Green**: Low Risk
  - 🟡 **Yellow**: Medium Risk
  - 🟠 **Orange**: High Risk
  - 🔴 **Red**: Critical Risk

### Step 5: Learn More
- Visit the **About** page for project details and use cases

## 🔌 API Endpoints

### POST `/predict`

**Request Body:**
```json
{
  "Day_of_Week": "Friday",
  "Month": "October",
  "Time_Slot": "Night",
  "City": "Delhi",
  "Latitude": 28.7041,
  "Longitude": 77.1025,
  "Population_Density": 29000,
  "Previous_Crimes_Area": 15,
  "Police_Station_Distance": 1.2,
  "Patrol_Intensity": "Low",
  "Crime_Type": "Robbery"
}
```

**Response:**
```json
{
  "Hotspot_Label": 1,
  "Predicted_Severity_Level": "High",
  "input_data": { ... }
}
```

### GET `/health`

**Response:**
```json
{
  "status": "healthy",
  "message": "Crime Hotspot Prediction API is running"
}
```

## 🎨 Color Scheme

- **Primary**: `#1E3A8A` (Deep Blue)
- **Secondary**: `#3B82F6` (Sky Blue)
- **Low Risk**: `#22c55e` (Green)
- **Medium Risk**: `#eab308` (Yellow)
- **High Risk**: `#f97316` (Orange)
- **Critical Risk**: `#ef4444` (Red)

## 🧪 Demo Data Example

For testing purposes, you can use these sample inputs:

| Field | Value |
|-------|-------|
| City | Mumbai |
| Latitude | 19.0760 |
| Longitude | 72.8777 |
| Population Density | 25000 |
| Previous Crimes | 12 |
| Police Distance | 2.5 km |
| Patrol Intensity | Medium |
| Crime Type | Theft |

## 🔧 Customization

### Adding a Real ML Model

1. Train your model using scikit-learn
2. Save it as `model.pkl` and scaler as `scaler.pkl`
3. Place them in the `backend/` directory
4. Update `app.py` to load and use the actual model:

```python
import joblib

model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')

def predict_crime_hotspot(data):
    # Preprocess data
    features = preprocess(data)
    scaled_features = scaler.transform([features])
    prediction = model.predict(scaled_features)
    return prediction
```

### Modifying the Map Center

Edit `frontend/src/components/HeatMap.jsx`:

```javascript
const defaultCenter = [YOUR_LAT, YOUR_LNG];
const defaultZoom = YOUR_ZOOM_LEVEL;
```

## 🐛 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'flask'`
- **Solution**: Ensure virtual environment is activated and run `pip install -r requirements.txt`

**Problem**: CORS errors
- **Solution**: Flask-CORS is configured in `app.py`. Ensure it's properly installed.

### Frontend Issues

**Problem**: Map not displaying
- **Solution**: Check that Leaflet CSS is loaded in `index.html`

**Problem**: API connection errors
- **Solution**: Ensure backend is running on `http://localhost:5000`

### Windows PowerShell Script Execution

If you encounter script execution errors on Windows:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📄 License

This project is open-source and available for educational purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## 📧 Support

For questions or issues, please create an issue in the repository.

---

**Built with ❤️ using React, Flask, and Machine Learning**
