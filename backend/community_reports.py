"""
Community Crime Reporting System - Backend Module
Handles storage and retrieval of community crime reports
"""
import json
import os
import uuid
from datetime import datetime
from flask import request, jsonify

# Get the directory where this script is located (backend directory)
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_FILE = os.path.join(BACKEND_DIR, 'community_reports.json')

def load_reports():
    """Load all community reports from JSON file"""
    if not os.path.exists(REPORTS_FILE):
        return []
    try:
        with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading reports: {e}")
        return []

def save_reports(reports):
    """Save all community reports to JSON file"""
    try:
        with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reports, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving reports: {e}")
        return False

def add_report(report_data):
    """Add a new community crime report"""
    reports = load_reports()
    
    # Create new report with required fields
    new_report = {
        "id": str(uuid.uuid4()),
        "location": report_data.get("location", ""),  # "latitude,longitude"
        "type": report_data.get("type", "other"),
        "time": datetime.now().isoformat(),
        "description": report_data.get("description", ""),
        "image": report_data.get("image", "")  # base64 or file URL
    }
    
    reports.append(new_report)
    
    if save_reports(reports):
        # Try to send alert for new community report
        try:
            from alerting import send_sms
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            admin_phone = os.getenv("ADMIN_PHONE")
            if admin_phone:
                alert_msg = f"🚨 New Community Report: {new_report['type']} at {new_report['location']}"
                send_sms(admin_phone, alert_msg)
        except Exception as e:
            print(f"Could not send alert for community report: {e}")
        
        return new_report
    return None

def get_all_reports():
    """Get all community reports"""
    return load_reports()

