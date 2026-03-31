from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import os
from feature_engineering import create_advanced_features
from dotenv import load_dotenv
from web_scraper import (
    fetch_india_crime_news,
    get_scraping_stats,
    get_dataset_stats,
    run_all_sources,
)

# ✅ New feature imports
from community_reports import add_report, get_all_reports
from risk_explanation import explain_risk
from chatbot_service import process_chatbot_message

# ✅ Load environment variables
load_dotenv()

# ✅ Twilio import
from alerting import send_sms

# ✅ RSS scraping
from web_scraper import fetch_india_crime_news

# Flask app
app = Flask(__name__)
CORS(app)

# Twilio admin phone
ADMIN_PHONE = os.getenv("ADMIN_PHONE")

# Load trained models and encoders
print("Loading trained ML models...")
try:
    hotspot_model = joblib.load('hotspot_model.pkl')
    severity_model = joblib.load('severity_model.pkl')
    scaler = joblib.load('scaler.pkl')
    label_encoders = joblib.load('label_encoders.pkl')
    severity_encoder = joblib.load('severity_encoder.pkl')
    feature_columns = joblib.load('feature_columns.pkl')

    print("✓ Core models loaded successfully!")
    models_loaded = True
except Exception as e:
    print(f"⚠ Warning: Could not load core models: {e}")
    print("Using fallback prediction logic...")
    models_loaded = False
    hotspot_model = None
    severity_model = None
    scaler = None
    label_encoders = {}
    severity_encoder = None
    feature_columns = []

# Try to load precomputed model statistics (optional)
model_stats = None
if models_loaded:
    try:
        model_stats = joblib.load('model_stats.pkl')
        print("✓ Model stats loaded successfully!")
    except Exception as e:
        print(f"⚠ Warning: Could not load model_stats.pkl: {e}")
        print("   → Proceeding without global stats; features will be computed per-request.")

# -------------------------------
# Prediction functions
# -------------------------------
def predict_crime_hotspot(data):
    if not models_loaded:
        print("⚠ Using fallback prediction logic!")
        return predict_fallback(data)
    
    try:
        input_df = pd.DataFrame([data])
        if 'Latitude' in input_df.columns:
            input_df['Latitude_fixed'] = input_df['Latitude']
        if 'Longitude' in input_df.columns:
            input_df['Longitude_fixed'] = input_df['Longitude']

        input_df, _ = create_advanced_features(input_df, stats=model_stats)
        
        input_features = {}
        for col in feature_columns:
            input_features[col] = input_df[col].iloc[0] if col in input_df.columns else 0
        
        final_input_df = pd.DataFrame([input_features])

        categorical_cols = ['Day_of_Week', 'Month', 'Time_Slot', 'City', 'State', 
                           'Patrol_Intensity', 'Crime_Type', 'Age_Group_Mostly_Affected', 
                           'Police_Station_Area']
        
        for col in categorical_cols:
            if col in label_encoders and col in final_input_df.columns:
                le = label_encoders[col]
                val = str(final_input_df[col].values[0])
                if val not in le.classes_:
                    final_input_df[col] = 0
                else:
                    final_input_df[col] = le.transform([val])[0]
            elif col in final_input_df.columns:
                final_input_df[col] = 0

        final_input_df = final_input_df.fillna(0)
        
        print("Final features sent to model:\n", final_input_df.head())
        
        input_scaled = scaler.transform(final_input_df)
        
        hotspot_pred = hotspot_model.predict(input_scaled)[0]
        severity_pred = severity_model.predict(input_scaled)[0]
        severity_label = severity_encoder.inverse_transform([severity_pred])[0]

        # Ensure logical consistency
        if severity_label in ['Critical', 'High', 'Medium']:
            hotspot_pred = 1
        elif severity_label == 'Low':
            hotspot_pred = 0
        
        print(f"Predicted hotspot: {hotspot_pred}, severity: {severity_label}")
        
        return int(hotspot_pred), severity_label
        
    except Exception as e:
        print(f"Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return predict_fallback(data)

def predict_fallback(data):
    previous_crimes = data.get('Previous_Crimes_Area', 0)
    population_density = data.get('Population_Density', 0)
    police_distance = data.get('Police_Station_Distance', 0)
    patrol_intensity = data.get('Patrol_Intensity', 'Medium')
    
    risk_score = 0
    if previous_crimes > 10: risk_score += 3
    elif previous_crimes > 5: risk_score += 2
    else: risk_score += 1
    
    if population_density > 20000: risk_score += 2
    elif population_density > 10000: risk_score += 1
    
    if police_distance > 3: risk_score += 2
    elif police_distance > 1.5: risk_score += 1
    
    if patrol_intensity == 'Low': risk_score += 2
    elif patrol_intensity == 'Medium': risk_score += 1
    
    if risk_score >= 10: severity = "Critical"
    elif risk_score >= 7: severity = "High"
    elif risk_score >= 4: severity = "Medium"
    else: severity = "Low"
    
    hotspot_label = 1 if severity in ['Critical', 'High', 'Medium'] else 0
    
    print(f"[Fallback] Predicted hotspot: {hotspot_label}, severity: {severity}")
    
    return hotspot_label, severity

# -------------------------------
# Routes
# -------------------------------
@app.route('/news/india-crime', methods=['GET'])
def get_india_crime_news():
    """Return latest India crime news from Google News RSS."""
    try:
        limit = request.args.get('limit', default=10, type=int)
        result = fetch_india_crime_news(limit=limit)
        status_code = 200 if result.get("success") else 502
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "items": []}), 500


@app.route('/scraping/stats', methods=['GET'])
def scraping_stats():
    """Expose web-scraping statistics for the frontend dashboard."""
    try:
        stats = get_scraping_stats()
        # Even if stats["success"] is False, we still return 200 so the UI can show an error message.
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/dataset/stats', methods=['GET'])
def dataset_stats():
    """Combined dataset stats (original training CSV + scraped records)."""
    try:
        stats = get_dataset_stats()
        status = 200 if stats.get("success") else 500
        return jsonify(stats), status
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/scraping/run', methods=['POST'])
def scraping_run():
    """Trigger scrapers manually and return updated stats."""
    try:
        df = run_all_sources()
        rows = int(len(df)) if df is not None else 0
        stats = get_dataset_stats()
        return jsonify({"success": True, "rows_scraped": rows, "stats": stats}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        hotspot_label, severity = predict_crime_hotspot(data)

        # Generate alert message based on severity
        city = data.get('City', 'Unknown Location')
        alert_message = ""
        suggestions = ""
        
        if severity == 'Critical':
            alert_message = f"🚨 CRITICAL ALERT: Very high crime risk detected at {city}! Avoid this area immediately."
            suggestions = "• Do not visit this area\n• If already there, leave immediately\n• Travel in groups if necessary\n• Keep emergency contacts ready\n• Call 100 if you see suspicious activity"
        elif severity == 'High':
            alert_message = f"⚠️ HIGH RISK: Elevated crime risk at {city}. Exercise extreme caution."
            suggestions = "• Avoid this area if possible\n• If you must go, travel in groups\n• Stay in well-lit, populated areas\n• Keep emergency contacts ready\n• Be extra alert and aware"
        elif severity == 'Medium':
            alert_message = f"⚠️ MODERATE RISK: Moderate crime risk at {city}. Stay alert."
            suggestions = "• Be cautious in this area\n• Avoid isolated spots\n• Stay in populated areas\n• Keep phone charged\n• Trust your instincts"
        else:
            alert_message = f"✅ LOW RISK: Area appears relatively safe at {city}."
            suggestions = "• Still stay alert\n• Follow general safety precautions\n• Report any suspicious activity"

        # ✅ Send SMS for Medium, High, Critical predictions
        if severity in ['Medium', 'High', 'Critical']:
            sms_message = f"🚨 Crime Alert! Severity: {severity} at {city} ({data.get('Latitude','')}, {data.get('Longitude','')})"
            sms_sid = send_sms(ADMIN_PHONE, sms_message)
            if sms_sid:
                print(f"✅ SMS alert sent: SID={sms_sid}")
            else:
                print("⚠️ SMS alert not sent (Twilio not configured or failed)")

        response = {
            'Hotspot_Label': hotspot_label,
            'Predicted_Severity_Level': severity,
            'alert_message': alert_message,
            'suggestions': suggestions,
            'input_data': data
        }
        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Error in predict route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Crime Hotspot Prediction API is running'
    }), 200

# -------------------------------
# Feature 3: Community Crime Reporting
# -------------------------------
@app.route('/report-crime', methods=['POST'])
def report_crime():
    """Submit a community crime report"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Validate required fields
        if not data.get("location") or not data.get("type"):
            return jsonify({"success": False, "error": "Missing required fields: location and type"}), 400
        
        report = add_report(data)
        
        if report:
            return jsonify({"success": True, "report": report}), 201
        else:
            return jsonify({"success": False, "error": "Failed to save report"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get-community-reports', methods=['GET'])
def get_community_reports():
    """Get all community crime reports"""
    try:
        reports = get_all_reports()
        return jsonify({"success": True, "reports": reports}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "reports": []}), 500

# -------------------------------
# Feature 4: AI Risk Explanation
# -------------------------------
@app.route('/explain-risk', methods=['POST'])
def explain_risk_route():
    """Get AI explanation for why an area is high risk"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        
        if latitude is None or longitude is None:
            return jsonify({"success": False, "error": "Missing latitude or longitude"}), 400
        
        # Get explanation
        explanation = explain_risk(
            latitude=latitude,
            longitude=longitude,
            model_stats=model_stats,
            hotspot_model=hotspot_model if models_loaded else None,
            scaler=scaler if models_loaded else None,
            label_encoders=label_encoders if models_loaded else {},
            feature_columns=feature_columns if models_loaded else []
        )
        
        return jsonify({"success": True, **explanation}), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -------------------------------
# Feature 5: AI Safety Assistant Chatbot
# -------------------------------
@app.route('/chatbot-message', methods=['POST'])
def chatbot_message():
    """Process chatbot message and return safety advice"""
    try:
        print("🤖 Chatbot endpoint called")
        data = request.get_json()
        print(f"📥 Received data: {data}")
        
        if not data:
            print("⚠️ No data provided")
            return jsonify({
                "success": False, 
                "error": "No data provided",
                "response": "Please send a message to get help.",
                "suggestions": []
            }), 400
        
        message = data.get("message", "").strip()
        print(f"💬 Processing message: {message}")
        
        if not message:
            print("⚠️ Empty message")
            return jsonify({
                "success": False,
                "error": "No message provided",
                "response": "👋 I'm here to help! Please ask me a question about safety.",
                "suggestions": ["Location safety", "Route planning", "Emergency help"]
            }), 400
        
        # Process the message
        response = process_chatbot_message(message)
        print(f"✅ Generated response: {response.get('response', '')[:50]}...")
        
        # Ensure response has required fields
        if not isinstance(response, dict):
            response = {
                "response": "I'm here to help with safety questions. How can I assist you?",
                "suggestions": ["Location safety", "Route help", "Report crime"]
            }
        
        # Ensure response and suggestions exist
        bot_response = response.get("response", "I'm here to help with safety questions. How can I assist you?")
        suggestions = response.get("suggestions", [])
        
        if not bot_response:
            bot_response = "I'm here to help with safety questions. How can I assist you?"
        if not suggestions:
            suggestions = ["Location safety", "Route help", "Report crime"]
        
        result = {
            "success": True,
            "response": bot_response,
            "suggestions": suggestions
        }
        print(f"📤 Sending response: success={result['success']}, response_length={len(bot_response)}")
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        print(f"❌ Error in chatbot_message route: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "response": "I'm sorry, I encountered an error. Please try again or ask a different question.",
            "suggestions": ["Location safety", "Route help", "Report crime"]
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Crime Hotspot Prediction API...")
    print("📍 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
