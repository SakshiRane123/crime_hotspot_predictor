# 🧪 Coordinate Testing Guide

## How to Test

1. **Open the application**: http://localhost:3000
2. **Open browser console**: Press F12 (Chrome/Edge) or Ctrl+Shift+I
3. **Go to Predict page**
4. **Enter test coordinates**:
   - City: Mumbai
   - Latitude: 19.0760
   - Longitude: 72.8777
   - Fill in other fields (Population: 25000, Previous Crimes: 10, etc.)
5. **Click "Predict Hotspot"**
6. **Check Console Logs**:
   - Look for "📍 Prediction Coordinates:" - Shows what was entered
   - Look for "🗺️ Map Centering on:" - Shows where map centers
   - Look for "🎯 All Predictions for Map:" - Shows all markers
   - Look for "📍 Rendering marker" - Shows each marker placement

7. **Go to Map page**
8. **Verify**:
   - Map should center on Mumbai (19.0760, 72.8777)
   - Marker should appear at exact coordinates
   - Click marker to see popup with coordinates

## Test Coordinates

### Mumbai
- Lat: 19.0760, Lng: 72.8777

### Delhi
- Lat: 28.6139, Lng: 77.2090

### Bangalore
- Lat: 12.9716, Lng: 77.5946

### Kolkata
- Lat: 22.5726, Lng: 88.3639

## What to Look For

✅ **Correct**: Marker appears at entered coordinates
❌ **Wrong**: Marker appears somewhere else

## Console Output Example

```
📍 Prediction Coordinates: {
  inputLat: "19.0760",
  inputLng: "72.8777",
  parsedLat: 19.076,
  parsedLng: 72.8777
}

🗺️ Map Centering on: {
  lat: 19.076,
  lng: 72.8777,
  city: "Mumbai"
}

🎯 All Predictions for Map: [{
  city: "Mumbai",
  lat: 19.076,
  lng: 72.8777
}]

📍 Rendering marker 0: [19.076, 72.8777]
```

All numbers should match!
