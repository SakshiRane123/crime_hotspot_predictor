# test_sms.py
from dotenv import load_dotenv
import os

# ✅ Load .env first
load_dotenv()

# ✅ Check environment variables
print("TWILIO_SID:", os.getenv("TWILIO_SID"))
print("TWILIO_TOKEN:", os.getenv("TWILIO_TOKEN"))
print("TWILIO_FROM:", os.getenv("TWILIO_FROM"))
print("ADMIN_PHONE:", os.getenv("ADMIN_PHONE"))

# Now import your send_sms function
from alerting import send_sms

# Send a test SMS
send_sms(os.getenv("ADMIN_PHONE"), "Test alert from Crime Hotspot API")
