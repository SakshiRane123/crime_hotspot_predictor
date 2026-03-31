"""
AI Safety Assistant Chatbot Service
Enhanced with comprehensive crime-related knowledge and improved pattern matching
"""
import re
from datetime import datetime

def contains_any(message, keywords):
    """Check if message contains any of the keywords (case-insensitive)"""
    message_lower = message.lower()
    return any(keyword.lower() in message_lower for keyword in keywords)

def process_chatbot_message(message):
    """
    Process user message and generate safety-based response
    
    Args:
        message: User's message string
        
    Returns:
        dict with response text and suggestions
    """
    try:
        if not message or not isinstance(message, str):
            return get_default_response()
        
        message_lower = message.lower().strip()
        
        # Remove common filler words for better matching
        cleaned_message = re.sub(r'\b(hi|hello|hey|please|can you|tell me|i want to know|i need|about)\b', '', message_lower)
        cleaned_message = cleaned_message.strip()
        
        # ============================================
        # CRIME TYPES - Specific crime questions
        # ============================================
        
        # Theft/Robbery - More keywords
        if contains_any(message_lower, ['theft', 'robbery', 'steal', 'stolen', 'pickpocket', 'snatch', 'robbed', 'thief', 'thieves', 'loot', 'burglary']):
            return {
                "response": "🔒 Theft & Robbery Prevention:\n\n**Precautions:**\n• Keep valuables out of sight\n• Don't display expensive items in public\n• Be cautious in crowded areas (markets, buses, trains)\n• Keep bags zipped and close to your body\n• Avoid isolated ATMs, especially at night\n• Don't carry large amounts of cash\n• Use digital payment methods when possible\n\n**If Theft Occurs:**\n1. Stay calm and assess the situation\n2. Don't chase the thief (could be dangerous)\n3. Note the appearance and direction of escape\n4. Call police immediately (100)\n5. File an FIR at nearest police station\n6. Cancel stolen cards/phones immediately\n7. Report to your bank if cards stolen\n\n**After Theft:**\n• Check CCTV footage if available\n• Inform family/friends\n• Monitor accounts for unauthorized transactions",
                "suggestions": ["Report crime", "Emergency contacts", "Prevention tips"]
            }
        
        # Assault/Violence - More keywords
        if contains_any(message_lower, ['assault', 'attack', 'violence', 'beaten', 'hit', 'physical', 'fight', 'fighting', 'punch', 'hurt', 'injured']):
            return {
                "response": "⚔️ Assault & Violence Prevention:\n\n**Precautions:**\n• Avoid confrontations and arguments\n• Stay away from known trouble spots\n• Travel in groups when possible\n• Trust your instincts - leave if you feel unsafe\n• Avoid walking alone in isolated areas\n• Keep emergency contacts on speed dial\n• Learn basic self-defense techniques\n\n**If Assault Occurs:**\n1. **Priority: Get to Safety** - Run to a public, well-lit area\n2. **Call Emergency** - Dial 100 immediately\n3. **Seek Help** - Shout for help, attract attention\n4. **Don't Fight Back** - Unless absolutely necessary for escape\n5. **Document Injuries** - Take photos, get medical help\n6. **File Police Report** - Report immediately with details\n7. **Seek Medical Attention** - Even for minor injuries\n\n**Self-Defense Tips:**\n• Use pepper spray if legal in your area\n• Target vulnerable areas (eyes, throat, groin)\n• Create distance and escape\n• Make noise to attract attention",
                "suggestions": ["Emergency help", "Report crime", "Self-defense"]
            }
        
        # Harassment/Sexual Harassment - More keywords
        if contains_any(message_lower, ['harassment', 'harass', 'eve teasing', 'molest', 'abuse', 'stalking', 'tease', 'unwanted', 'inappropriate']):
            return {
                "response": "🚫 Harassment Prevention & Response:\n\n**Precautions:**\n• Be aware of your surroundings\n• Trust your instincts about people\n• Avoid sharing personal information with strangers\n• Block and report online harassers\n• Don't walk alone in isolated areas\n• Keep emergency apps ready\n• Inform trusted people about your location\n\n**If Harassment Occurs:**\n1. **Speak Up Firmly** - \"Stop!\" or \"Leave me alone!\"\n2. **Move to Public Area** - Get to a crowded, well-lit place\n3. **Call Emergency** - Dial 100 or women's helpline (1091)\n4. **Document Evidence** - Screenshots, recordings, photos\n5. **Report Immediately** - File complaint at police station\n6. **Seek Support** - Contact family, friends, support groups\n7. **Don't Blame Yourself** - It's never your fault\n\n**Legal Rights:**\n• Sexual harassment is a criminal offense\n• You have the right to file FIR\n• Support services available (counseling, legal aid)\n• Workplace harassment can be reported to HR",
                "suggestions": ["Emergency helpline", "Report crime", "Support services"]
            }
        
        # Cyber Crime - More keywords
        if contains_any(message_lower, ['cyber', 'online', 'fraud', 'scam', 'phishing', 'hack', 'identity theft', 'internet', 'digital', 'fake', 'cheat']):
            return {
                "response": "💻 Cyber Crime Prevention:\n\n**Precautions:**\n• Use strong, unique passwords\n• Enable two-factor authentication\n• Don't click suspicious links or emails\n• Verify before sharing personal/financial info\n• Keep software updated\n• Use secure Wi-Fi networks\n• Be cautious on social media\n• Don't share OTPs with anyone\n\n**If Cyber Crime Occurs:**\n1. **Disconnect** - Unplug from internet if hacked\n2. **Change Passwords** - All accounts immediately\n3. **Report to Bank** - If financial fraud, block cards\n4. **File Complaint** - Cyber crime cell (cybercrime.gov.in)\n5. **Document Evidence** - Screenshots, emails, transactions\n6. **Inform Authorities** - Local police + cyber crime unit\n7. **Monitor Accounts** - Check for unauthorized activity\n\n**Common Scams:**\n• Fake job offers asking for money\n• Lottery/prize scams\n• Phishing emails/messages\n• Fake tech support calls\n• Online shopping frauds",
                "suggestions": ["Report cyber crime", "Prevention tips", "Emergency contacts"]
            }
        
        # Domestic Violence - More keywords
        if contains_any(message_lower, ['domestic', 'abuse', 'family violence', 'home violence', 'spouse', 'partner']):
            return {
                "response": "🏠 Domestic Violence Help:\n\n**If You're in Immediate Danger:**\n• Call 100 (Police) or 1091 (Women's Helpline)\n• Leave the location if safe to do so\n• Go to nearest police station or shelter\n• Contact family/friends for support\n\n**Support Services:**\n• National Commission for Women: 7827170170\n• Women's Helpline: 1091\n• Child Helpline: 1098\n• Domestic Violence Helpline: 181\n\n**Legal Rights:**\n• Protection of Women from Domestic Violence Act, 2005\n• You can file complaint at police station\n• Protection orders available\n• Right to shelter and medical help\n\n**Safety Planning:**\n• Keep important documents safe\n• Have emergency contacts ready\n• Plan escape route\n• Save evidence (photos, recordings)\n• Seek counseling and support",
                "suggestions": ["Emergency helpline", "Legal help", "Support services"]
            }
        
        # ============================================
        # PRECAUTIONS & PREVENTION - More variations
        # ============================================
        
        if contains_any(message_lower, ['precaution', 'prevent', 'avoid', 'protect', 'safety tips', 'how to stay safe', 'safe', 'safety', 'secure', 'protection', 'preventive', 'measures']):
            return {
                "response": "🛡️ Comprehensive Safety Precautions:\n\n**General Safety:**\n• Stay alert and aware of surroundings\n• Trust your instincts - if something feels wrong, leave\n• Avoid isolated areas, especially at night\n• Travel in groups when possible\n• Keep emergency contacts on speed dial\n• Share your location with trusted people\n• Keep phone charged and have backup power\n\n**Personal Safety:**\n• Don't display expensive items in public\n• Keep valuables secure and out of sight\n• Use well-lit, populated routes\n• Avoid shortcuts through isolated areas\n• Be cautious with strangers\n• Don't share personal information unnecessarily\n\n**Home Safety:**\n• Lock doors and windows\n• Install security systems if possible\n• Know your neighbors\n• Don't open door to strangers\n• Keep emergency numbers handy\n• Install good lighting around home\n\n**Vehicle Safety:**\n• Lock car doors while driving\n• Park in well-lit areas\n• Don't leave valuables in car\n• Check backseat before entering\n• Keep windows up in traffic\n\n**Use Our App:**\n• Check crime hotspot map before going out\n• Report suspicious activities\n• Get real-time risk assessments",
                "suggestions": ["Check map", "Report crime", "Emergency contacts"]
            }
        
        # ============================================
        # ACTIONS DURING/AFTER CRIME - More variations
        # ============================================
        
        if contains_any(message_lower, ['what to do', 'action', 'steps', 'procedure', 'during crime', 'after crime', 'happened', 'occurred', 'do if', 'should i', 'how to handle']):
            return {
                "response": "📋 Actions During & After Crime:\n\n**During a Crime:**\n1. **Stay Calm** - Panic makes decisions harder\n2. **Assess Situation** - Is it safe to act or should you escape?\n3. **Prioritize Safety** - Your life is more important than property\n4. **Call Emergency** - Dial 100 immediately\n5. **Get to Safety** - Move to public, well-lit area\n6. **Attract Attention** - Shout, use whistle, make noise\n7. **Don't Confront** - Unless absolutely necessary for escape\n\n**Immediately After Crime:**\n1. **Ensure Safety** - Get to a safe location first\n2. **Call Police** - Dial 100, provide location and details\n3. **Seek Medical Help** - If injured, go to hospital\n4. **Preserve Evidence** - Don't touch or move anything\n5. **Document Everything** - Write down what happened\n6. **Contact Family** - Inform trusted people\n7. **File FIR** - Go to nearest police station\n\n**Filing Police Report:**\n• Go to nearest police station\n• Provide accurate details (time, location, description)\n• Get copy of FIR (First Information Report)\n• Note the FIR number\n• Follow up on investigation\n\n**After Filing Report:**\n• Keep all documents safe\n• Follow up with police regularly\n• Seek legal help if needed\n• Get counseling if traumatized\n• Join support groups if available",
                "suggestions": ["Emergency contacts", "Report crime", "Legal help"]
            }
        
        # ============================================
        # EMERGENCY PROCEDURES - More variations
        # ============================================
        
        if contains_any(message_lower, ['emergency', 'urgent', 'help', 'danger', 'immediate', 'dangerous', 'threat', 'unsafe']):
            return {
                "response": "🚨 Emergency Procedures:\n\n**Emergency Numbers (India):**\n• Police: 100\n• Women's Helpline: 1091\n• Child Helpline: 1098\n• Medical Emergency: 102 or 108\n• Fire: 101\n• Domestic Violence: 181\n\n**In Immediate Danger:**\n1. **Call 100** - Police emergency\n2. **Get to Safety** - Public area, well-lit place\n3. **Stay on Phone** - Keep operator informed\n4. **Describe Location** - Be specific about where you are\n5. **Describe Situation** - What's happening, who's involved\n6. **Follow Instructions** - Listen to emergency operator\n\n**If Unable to Call:**\n• Shout for help\n• Run to nearest public place\n• Enter any open shop/building\n• Wave for attention\n• Use emergency apps if available\n\n**Pre-Emergency Preparation:**\n• Save emergency numbers on speed dial\n• Share location with trusted contacts\n• Install emergency apps\n• Know nearest police station location\n• Keep whistle or alarm device",
                "suggestions": ["Emergency contacts", "Report crime", "Get help"]
            }
        
        # ============================================
        # CRIME STATISTICS & PATTERNS
        # ============================================
        
        if contains_any(message_lower, ['statistics', 'stats', 'data', 'pattern', 'trend', 'common', 'frequent', 'rate', 'incident']):
            return {
                "response": "📊 Crime Patterns & Statistics:\n\n**Common Crime Patterns:**\n• **Theft** - Most common in crowded areas (markets, public transport)\n• **Robbery** - Higher risk in isolated areas, especially at night\n• **Harassment** - More frequent in less populated areas\n• **Cyber Crime** - Increasing with digital adoption\n• **Domestic Violence** - Underreported but significant\n\n**Time-Based Patterns:**\n• **Night (8 PM - 6 AM)** - Highest crime risk\n• **Evening (6 PM - 8 PM)** - Moderate risk\n• **Daytime** - Generally safer but still be alert\n• **Weekends** - Slightly higher crime rates\n• **Festival Seasons** - Increased theft in crowded areas\n\n**Location Risk Factors:**\n• Isolated areas = Higher risk\n• Poor lighting = Higher risk\n• Low police presence = Higher risk\n• High population density = More theft/pickpocketing\n• Tourist areas = Higher theft risk\n\n**Use Our Features:**\n• Check crime hotspot map for real-time data\n• Get risk predictions for specific locations\n• View community-reported incidents\n• See AI-generated risk explanations",
                "suggestions": ["View map", "Check predictions", "See reports"]
            }
        
        # ============================================
        # LOCATION-SPECIFIC SAFETY - More cities
        # ============================================
        
        cities = {
            'mumbai': 'Mumbai',
            'delhi': 'Delhi',
            'bangalore': 'Bangalore',
            'chennai': 'Chennai',
            'kolkata': 'Kolkata',
            'hyderabad': 'Hyderabad',
            'pune': 'Pune',
            'bandra': 'Bandra (Mumbai)',
            'andheri': 'Andheri (Mumbai)',
            'kurla': 'Kurla (Mumbai)',
            'navi mumbai': 'Navi Mumbai',
            'gurgaon': 'Gurgaon',
            'noida': 'Noida'
        }
        
        location_found = None
        for city_key, city_name in cities.items():
            if city_key in message_lower:
                location_found = city_name
                break
        
        # Also check for generic location words
        if not location_found and contains_any(message_lower, ['location', 'area', 'place', 'city', 'where']):
            location_found = "this area"
        
        if location_found:
            if contains_any(message_lower, ['10 pm', '10pm', '11 pm', '11pm', '12 am', 'midnight', 'night', 'evening', 'late', 'dark']):
                return {
                    "response": f"🌙 Night Safety in {location_found}:\n\n**High-Risk Areas to Avoid:**\n• Isolated streets and alleys\n• Poorly lit areas\n• Empty parking lots\n• Railway stations after hours\n• Beaches at night\n• Industrial areas\n\n**Safe Practices:**\n• Use well-lit main roads\n• Travel in groups when possible\n• Use trusted transportation (registered cabs)\n• Share live location with family\n• Keep emergency contacts ready\n• Avoid displaying valuables\n• Stay in populated areas\n\n**Transportation Safety:**\n• Prefer app-based cabs (verify driver details)\n• Share trip details with someone\n• Sit in back seat\n• Keep windows slightly open\n• Trust your instincts - cancel if uncomfortable\n\n**Use Our App:**\n• Check real-time risk map before going out\n• Get AI risk assessment for your route\n• Report any incidents you witness",
                    "suggestions": ["Check map", "Get risk assessment", "Report crime"]
                }
            else:
                return {
                    "response": f"📍 Safety Tips for {location_found}:\n\n**General Safety:**\n• Be cautious in crowded markets and public transport\n• Avoid isolated areas, especially at night\n• Keep valuables secure in crowded places\n• Use well-lit routes\n• Stay alert in tourist areas\n\n**Area-Specific Tips:**\n• Check our crime hotspot map for high-risk zones\n• Avoid areas marked in red (high risk)\n• Be extra cautious in yellow zones (medium risk)\n• Green zones are generally safer\n\n**Reporting:**\n• Use Community Report feature to report incidents\n• Help keep the community safe by sharing information\n• Check map for recent community reports\n\n**Get Real-Time Info:**\n• Use Predict feature for risk assessment\n• Check AI explanations for why areas are risky\n• View community-reported crimes on map",
                    "suggestions": ["View map", "Check risk level", "Report crime"]
                }
        
        # ============================================
        # ROUTE & TRAVEL SAFETY
        # ============================================
        
        if contains_any(message_lower, ['route', 'path', 'way', 'directions', 'travel', 'commute', 'journey', 'go to', 'reach']):
            return {
                "response": "🗺️ Safe Route Planning:\n\n**Planning Your Route:**\n• Use our crime hotspot map to identify safe zones\n• Avoid high-risk areas (red markers)\n• Choose well-lit, main roads\n• Prefer routes with police stations nearby\n• Plan during daylight when possible\n• Share your route with trusted contacts\n\n**During Travel:**\n• Stay alert and aware\n• Keep phone charged\n• Avoid isolated shortcuts\n• Use populated routes\n• Trust your instincts - change route if needed\n• Keep emergency contacts accessible\n\n**Public Transport Safety:**\n• Be cautious in crowded buses/trains\n• Keep bags secure and zipped\n• Don't display expensive items\n• Sit near other passengers\n• Be alert at stations/stops\n• Report suspicious behavior\n\n**Vehicle Safety:**\n• Lock doors while driving\n• Park in well-lit, secure areas\n• Don't leave valuables visible\n• Check surroundings before entering/exiting\n• Keep windows up in traffic\n\n**Use Our Features:**\n• Get AI risk assessment for your route\n• View community reports along your path\n• Check real-time crime predictions",
                "suggestions": ["View map", "Get predictions", "Plan route"]
            }
        
        # ============================================
        # WITNESSING CRIMES - More variations
        # ============================================
        
        if contains_any(message_lower, ['witness', 'saw', 'see', 'happening', 'occurring', 'incident', 'witnessed', 'seen', 'watching']):
            return {
                "response": "👁️ If You Witness a Crime:\n\n**Immediate Actions:**\n1. **Stay Safe** - Don't put yourself in danger\n2. **Call Emergency** - Dial 100 immediately\n3. **Observe Details** - Note what's happening\n4. **Get to Safe Distance** - But stay in area if safe\n5. **Document if Safe** - Photos/videos (if legal and safe)\n6. **Note Details** - Time, location, people involved, descriptions\n\n**What to Note:**\n• Exact location and time\n• Number of people involved\n• Physical descriptions (height, build, clothing)\n• Vehicle details (if any) - number, color, model\n• Direction of escape\n• Any weapons visible\n• What exactly happened\n\n**Reporting:**\n• Call 100 immediately\n• Provide accurate information to police\n• Use Community Report feature in our app\n• File witness statement if needed\n• Cooperate with investigation\n\n**Important:**\n• Don't intervene directly (could be dangerous)\n• Your safety comes first\n• Accurate information helps police\n• False reports are illegal\n• Be a responsible citizen",
                "suggestions": ["Call emergency", "Report crime", "Get help"]
            }
        
        # ============================================
        # TIME-BASED SAFETY
        # ============================================
        
        if contains_any(message_lower, ['night', 'evening', 'morning', 'afternoon', 'pm', 'am', 'time', 'when', 'hour', 'o clock']):
            return {
                "response": "⏰ Time-Based Safety Guide:\n\n**Night (8 PM - 6 AM) - HIGHEST RISK:**\n• Avoid isolated areas completely\n• Use well-lit, main roads only\n• Travel in groups when possible\n• Use trusted transportation\n• Share location with family\n• Keep emergency contacts ready\n• Be extra alert and aware\n• Avoid shortcuts\n\n**Evening (6 PM - 8 PM) - MODERATE RISK:**\n• Be cautious in less populated areas\n• Prefer main roads\n• Stay in well-lit zones\n• Be alert but less restrictive than night\n\n**Daytime (6 AM - 6 PM) - GENERALLY SAFER:**\n• Still stay alert\n• Be cautious in crowded areas (theft risk)\n• Avoid isolated areas even during day\n• Report suspicious activities\n• Don't let guard down completely\n\n**Weekend Safety:**\n• Slightly higher crime rates\n• More crowded areas = more theft risk\n• Be extra cautious at night\n• Plan routes carefully\n\n**Festival/Event Times:**\n• Higher theft in crowded events\n• Be cautious with valuables\n• Stay with group\n• Know emergency exits",
                "suggestions": ["Check map", "Get predictions", "Plan route"]
            }
        
        # ============================================
        # REPORTING CRIMES - More variations
        # ============================================
        
        if contains_any(message_lower, ['report', 'file', 'complaint', 'fir', 'police station', 'inform', 'notify', 'register']):
            return {
                "response": "📝 How to Report a Crime:\n\n**Emergency Reporting (Active Crime):**\n• Call 100 immediately\n• Provide location and situation\n• Stay on line with operator\n• Follow instructions\n\n**Filing FIR (First Information Report):**\n1. Go to nearest police station\n2. Provide accurate details:\n   - What happened\n   - When it happened (date & time)\n   - Where it happened (exact location)\n   - Who was involved (descriptions)\n   - Any witnesses\n   - Evidence available\n3. Get copy of FIR (your right)\n4. Note FIR number for follow-up\n\n**Using Our App:**\n• Use Community Report feature\n• Report incidents you witness\n• Help build community safety database\n• Reports appear on map for others\n\n**After Filing Report:**\n• Keep FIR copy safe\n• Follow up regularly\n• Provide additional information if found\n• Seek legal help if needed\n• Get counseling if traumatized\n\n**Your Rights:**\n• Police must register FIR (cannot refuse)\n• You have right to get FIR copy\n• You can file complaint if police refuse\n• False reports are illegal",
                "suggestions": ["Report crime", "Emergency contacts", "Legal help"]
            }
        
        # ============================================
        # GENERAL HELP & INTRO - More variations
        # ============================================
        
        if contains_any(message_lower, ['help', 'what can you', 'how can you', 'what do you', 'capabilities', 'features', 'assist', 'support']):
            return {
                "response": "🤖 I'm your AI Safety Assistant! I can help with:\n\n**Crime Prevention:**\n✅ Safety precautions for different situations\n✅ Preventive measures for theft, assault, harassment\n✅ Home and personal safety tips\n✅ Cyber crime prevention\n\n**During & After Crimes:**\n✅ What to do if crime happens\n✅ Emergency procedures\n✅ Steps to file police reports\n✅ Legal rights and procedures\n\n**Location Safety:**\n✅ Safety advice for specific cities/areas\n✅ Time-based safety (night, evening, day)\n✅ Route planning and safe paths\n✅ Risk assessment guidance\n\n**Crime Information:**\n✅ Common crime patterns and statistics\n✅ Understanding crime trends\n✅ Area-specific risk factors\n\n**Try Asking:**\n• \"What precautions should I take?\"\n• \"What to do if I witness a theft?\"\n• \"Is Mumbai safe at night?\"\n• \"How to prevent cyber crime?\"\n• \"Steps to file a police complaint\"\n• \"Emergency procedures\"\n• \"Safe route suggestions\"",
                "suggestions": ["Prevention tips", "Emergency help", "Report crime"]
            }
        
        # ============================================
        # DEFAULT RESPONSE - More helpful
        # ============================================
        
        # If message is very short or unclear, provide helpful default
        if len(message_lower) < 5:
            return get_default_response()
        
        # Try to provide a more contextual default response
        return get_contextual_response(message_lower)
        
    except Exception as e:
        print(f"Error in process_chatbot_message: {e}")
        import traceback
        traceback.print_exc()
        return get_default_response()

def get_default_response():
    """Default response when query doesn't match specific patterns"""
    return {
        "response": "👋 I'm your AI Safety Assistant! I can help with crime-related questions.\n\n**I can answer questions about:**\n• Crime prevention and precautions\n• What to do during/after crimes\n• Emergency procedures\n• Location-specific safety\n• Reporting crimes\n• Crime patterns and statistics\n• Route safety planning\n\n**Try asking:**\n• \"What precautions should I take?\"\n• \"What to do if I witness a theft?\"\n• \"How to prevent cyber crime?\"\n• \"Is [location] safe at night?\"\n• \"Steps to file police complaint\"\n• \"Emergency procedures\"\n• \"Safe route suggestions\"\n\nOr ask me anything about crime safety, prevention, or actions!",
        "suggestions": ["Prevention tips", "Emergency help", "Report crime", "Location safety"]
    }

def get_contextual_response(message):
    """Provide a more contextual response based on message content"""
    # Check for question words
    question_words = ['what', 'how', 'when', 'where', 'why', 'who', 'which', 'is', 'are', 'can', 'should', 'will']
    has_question = any(word in message for word in question_words)
    
    if has_question:
        return {
            "response": "🤔 I understand you have a question about safety or crime.\n\n**I can help you with:**\n• Crime prevention and safety precautions\n• What to do during/after crimes\n• Emergency procedures and contacts\n• Location-specific safety advice\n• Reporting crimes and filing complaints\n• Crime patterns and statistics\n\n**Try rephrasing your question, for example:**\n• \"What precautions should I take?\"\n• \"How to prevent theft?\"\n• \"What to do if I witness a crime?\"\n• \"Is [location] safe?\"\n• \"How to file a police complaint?\"\n\nOr ask me about any specific crime type, safety measure, or emergency procedure!",
            "suggestions": ["Prevention tips", "Emergency help", "Report crime", "Location safety"]
        }
    else:
        return get_default_response()
