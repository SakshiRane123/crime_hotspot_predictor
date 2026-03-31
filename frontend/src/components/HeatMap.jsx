import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icon issue in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Component to update map view when predictions change
function MapUpdater({ predictions }) {
  const map = useMap();
  
  useEffect(() => {
    if (predictions && predictions.length > 0) {
      // Center on latest prediction
      const latest = predictions[predictions.length - 1];
      console.log('🗺️ Map Centering on:', {
        lat: latest.location.lat,
        lng: latest.location.lng,
        city: latest.location.city
      });
      map.setView([latest.location.lat, latest.location.lng], 8, {
        animate: true,
        duration: 1
      });
    }
  }, [predictions, map]);
  
  return null;
}

// Component to handle map clicks
function MapClickHandler({ onMapClick }) {
  useMapEvents({
    click: (e) => {
      if (onMapClick) {
        onMapClick(e.latlng.lat, e.latlng.lng);
      }
    }
  });
  return null;
}

const HeatMap = ({ predictions, communityReports = [], onLocationClick }) => {
  const defaultCenter = [20.5937, 78.9629]; // India center
  const defaultZoom = 5;

  const severityColors = {
    Low: '#22c55e',      // Green
    Medium: '#eab308',   // Yellow
    High: '#f97316',     // Orange
    Critical: '#ef4444'  // Red
  };

  const getMarkerSize = (severity) => {
    const sizes = {
      Low: 15,
      Medium: 20,
      High: 25,
      Critical: 30
    };
    return sizes[severity] || 20;
  };

  // Debug: Log all predictions
  console.log('🎯 All Predictions for Map:', predictions.map(p => ({
    city: p.location.city,
    lat: p.location.lat,
    lng: p.location.lng
  })));

  return (
    <div className="h-full w-full rounded-xl overflow-hidden shadow-lg">
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <MapUpdater predictions={predictions} />
        <MapClickHandler onMapClick={onLocationClick} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Prediction markers */}
        {predictions.map((prediction, index) => {
          console.log(`📍 Rendering marker ${index}:`, [prediction.location.lat, prediction.location.lng]);
          return (
          <CircleMarker
            key={`prediction-${index}`}
            center={[prediction.location.lat, prediction.location.lng]}
            radius={getMarkerSize(prediction.Predicted_Severity_Level)}
            fillColor={severityColors[prediction.Predicted_Severity_Level]}
            color={severityColors[prediction.Predicted_Severity_Level]}
            weight={2}
            opacity={0.8}
            fillOpacity={0.6}
            eventHandlers={{
              click: () => {
                if (onLocationClick) {
                  onLocationClick(prediction.location.lat, prediction.location.lng);
                }
              }
            }}
          >
            <Popup>
              <div className="p-2">
                <h3 className="font-bold text-lg">{prediction.location.city}</h3>
                <p className="text-sm">
                  <span className="font-semibold">Status:</span>{' '}
                  {prediction.Hotspot_Label === 1 ? '⚠️ Hotspot' : '✓ Safe'}
                </p>
                <p className="text-sm">
                  <span className="font-semibold">Severity:</span>{' '}
                  {prediction.Predicted_Severity_Level}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  <span className="font-semibold">Coordinates:</span> {prediction.location.lat.toFixed(4)}, {prediction.location.lng.toFixed(4)}
                </p>
                <p className="text-xs text-gray-600">
                  {new Date(prediction.timestamp).toLocaleString()}
                </p>
              </div>
            </Popup>
          </CircleMarker>
          );
        })}

        {/* Community report markers (orange) */}
        {communityReports.map((report, index) => {
          const [lat, lng] = report.location.split(',').map(coord => parseFloat(coord.trim()));
          if (isNaN(lat) || isNaN(lng)) return null;
          
          return (
            <CircleMarker
              key={`report-${report.id}`}
              center={[lat, lng]}
              radius={20}
              fillColor="#ff8c00"  // Orange color
              color="#ff6600"
              weight={2}
              opacity={0.9}
              fillOpacity={0.7}
              eventHandlers={{
                click: () => {
                  if (onLocationClick) {
                    onLocationClick(lat, lng);
                  }
                }
              }}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-bold text-lg">Community Report</h3>
                  <p className="text-sm">
                    <span className="font-semibold">Type:</span> {report.type}
                  </p>
                  <p className="text-sm">
                    <span className="font-semibold">Description:</span> {report.description || 'No description'}
                  </p>
                  <p className="text-xs text-gray-600 mt-1">
                    <span className="font-semibold">Time:</span> {new Date(report.time).toLocaleString()}
                  </p>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default HeatMap;
