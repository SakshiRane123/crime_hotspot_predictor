# alerting.py
import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load env variables
load_dotenv()

TW_SID = os.getenv("TWILIO_SID")
TW_TOKEN = os.getenv("TWILIO_TOKEN")
TW_FROM = os.getenv("TWILIO_FROM")

def send_sms(to_number, message):
    if not (TW_SID and TW_TOKEN and TW_FROM):
        print("❌ Twilio not configured — skipping SMS")
        return False

    try:
        client = Client(TW_SID, TW_TOKEN)
        msg = client.messages.create(
            body=message,
            from_=TW_FROM,
            to=to_number
        )
        print(f"📩 SMS sent: SID={msg.sid}")
        return msg.sid
    except Exception as e:
        print("❌ SMS sending failed:", e)
        return False
