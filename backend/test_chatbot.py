"""
Quick test script for chatbot functionality
Run this to verify the chatbot is working
"""
import requests
import json

def test_chatbot():
    base_url = "http://localhost:5000"
    
    test_messages = [
        "Is Bandra safe at 10 PM?",
        "Suggest a safe route",
        "What should I do if I witness a fight?",
        "Hello",
        "Help me"
    ]
    
    print("Testing Chatbot Service...")
    print("=" * 50)
    
    for message in test_messages:
        try:
            response = requests.post(
                f"{base_url}/chatbot-message",
                json={"message": message},
                timeout=5
            )
            
            print(f"\n📤 User: {message}")
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ Response: {data.get('response', 'No response')[:100]}...")
                    print(f"💡 Suggestions: {data.get('suggestions', [])}")
                else:
                    print(f"❌ Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Connection Error: Could not connect to {base_url}")
            print("   Make sure the Flask server is running!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_chatbot()


