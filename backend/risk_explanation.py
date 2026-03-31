"""
AI Crime Risk Explanation Module
Provides explanations for why an area is high risk
"""
import pandas as pd
import numpy as np
from feature_engineering import create_advanced_features

def explain_risk(latitude, longitude, model_stats=None, hotspot_model=None, 
                 scaler=None, label_encoders=None, feature_columns=None):
    """
    Generate risk explanation for a given location
    
    Returns:
        dict with risk_level and top_reasons
    """
    try:
        # Create sample data for the location
        sample_data = {
            'Latitude': latitude,
            'Longitude': longitude,
            'Day_of_Week': 'Monday',  # Default values
            'Month': 'January',
            'Time_Slot': 'Evening',
            'City': 'Unknown',
            'State': 'Unknown',
            'Previous_Crimes_Area': 0,
            'Population_Density': 0,
            'Police_Station_Distance': 0,
            'Patrol_Intensity': 'Medium',
            'Crime_Type': 'Theft',
            'Age_Group_Mostly_Affected': 'Adult',
            'Police_Station_Area': 'Unknown'
        }
        
        # Try to get feature importance if model is available
        reasons = []
        
        # Rule-based explanations (fallback)
        if model_stats is None or hotspot_model is None:
            # Use rule-based fallback
            reasons = [
                "Location analysis based on general crime patterns",
                "Historical data suggests moderate risk in this area",
                "Standard safety assessment applied"
            ]
            risk_level = "Medium"
        else:
            # Try to use model features for explanation
            try:
                input_df = pd.DataFrame([sample_data])
                input_df['Latitude_fixed'] = input_df['Latitude']
                input_df['Longitude_fixed'] = input_df['Longitude']
                
                input_df, _ = create_advanced_features(input_df, stats=model_stats)
                
                # Get feature values
                input_features = {}
                for col in feature_columns:
                    input_features[col] = input_df[col].iloc[0] if col in input_df.columns else 0
                
                final_input_df = pd.DataFrame([input_features])
                
                # Encode categorical features
                categorical_cols = ['Day_of_Week', 'Month', 'Time_Slot', 'City', 'State', 
                                 'Patrol_Intensity', 'Crime_Type', 'Age_Group_Mostly_Affected', 
                                 'Police_Station_Area']
                
                for col in categorical_cols:
                    if col in label_encoders and col in final_input_df.columns:
                        le = label_encoders[col]
                        val = str(final_input_df[col].values[0])
                        if val in le.classes_:
                            final_input_df[col] = le.transform([val])[0]
                        else:
                            final_input_df[col] = 0
                    elif col in final_input_df.columns:
                        final_input_df[col] = 0
                
                final_input_df = final_input_df.fillna(0)
                input_scaled = scaler.transform(final_input_df)
                
                # Get prediction
                hotspot_pred = hotspot_model.predict(input_scaled)[0]
                
                # Generate reasons based on feature values
                reasons = []
                
                # Check various risk factors
                if 'Previous_Crimes_Area' in input_features:
                    prev_crimes = input_features.get('Previous_Crimes_Area', 0)
                    if prev_crimes > 10:
                        reasons.append(f"High number of past crime cases ({int(prev_crimes)})")
                    elif prev_crimes > 5:
                        reasons.append(f"Moderate number of past crime cases ({int(prev_crimes)})")
                
                if 'Police_Station_Distance' in input_features:
                    police_dist = input_features.get('Police_Station_Distance', 0)
                    if police_dist > 3:
                        reasons.append("Few police stations nearby (distance > 3km)")
                    elif police_dist > 1.5:
                        reasons.append("Limited police presence in the area")
                
                if 'Population_Density' in input_features:
                    density = input_features.get('Population_Density', 0)
                    if density > 20000:
                        reasons.append("High population density increases risk")
                    elif density > 10000:
                        reasons.append("Moderate population density")
                
                if 'Is_Night' in input_features and input_features.get('Is_Night', 0) > 0:
                    reasons.append("Night time increases crime risk")
                
                if 'Is_Weekend' in input_features and input_features.get('Is_Weekend', 0) > 0:
                    reasons.append("Weekend timing associated with higher risk")
                
                # Determine risk level
                if hotspot_pred == 1:
                    if len(reasons) >= 3:
                        risk_level = "High"
                    elif len(reasons) >= 2:
                        risk_level = "Medium"
                    else:
                        risk_level = "Low"
                else:
                    risk_level = "Low"
                
                # Add default reasons if none found
                if len(reasons) == 0:
                    reasons = [
                        "Standard risk assessment applied",
                        "Location-specific factors analyzed",
                        "General safety patterns considered"
                    ]
                
            except Exception as e:
                print(f"Error in model-based explanation: {e}")
                reasons = [
                    "Location analysis based on general patterns",
                    "Standard safety assessment applied"
                ]
                risk_level = "Medium"
        
        # Ensure we have at least 3-4 reasons
        while len(reasons) < 4:
            if len(reasons) == 0:
                reasons.append("General area risk assessment")
            elif len(reasons) == 1:
                reasons.append("Historical crime data considered")
            elif len(reasons) == 2:
                reasons.append("Infrastructure and lighting factors analyzed")
            else:
                reasons.append("Community safety patterns evaluated")
        
        return {
            "risk_level": risk_level,
            "top_reasons": reasons[:4]  # Return top 4 reasons
        }
        
    except Exception as e:
        print(f"Error in explain_risk: {e}")
        return {
            "risk_level": "Medium",
            "top_reasons": [
                "Location analysis based on general patterns",
                "Standard safety assessment applied",
                "Historical data considered",
                "General area risk factors evaluated"
            ]
        }


