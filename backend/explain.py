# explain.py
import numpy as np
import pandas as pd
import os

# Mapping of feature names to human-friendly labels and suggestions
FEATURE_REASON_MAP = {
    'Patrol_Intensity': ("Low patrol intensity", "Increase patrol frequency; add night patrols"),
    'Population_Density': ("High population density", "Deploy community policing; CCTV in public spaces"),
    'Previous_Crimes_Area': ("History of crimes", "Targeted patrols and community campaigns"),
    'Police_Station_Distance': ("Far from police station", "Consider temporary beat stations or mobile units"),
    'Latitude_fixed': ("Isolated location", "Improve street lighting; CCTV"),
    # add more mappings as needed
}

def explain_prediction(model, X_df):
    """
    Returns a list of (feature, contribution, reason, suggestion) sorted by abs(contribution)
    Try using SHAP if available; otherwise use model.feature_importances_
    """
    try:
        import shap
        explainer = shap.Explainer(model, X_df)
        shap_values = explainer(X_df)
        # For a single prediction take shap_values.values[0]
        contributions = list(zip(X_df.columns, shap_values.values[0]))
    except Exception as e:
        # fallback: use feature_importances_ if available
        try:
            import numpy as np
            fi = model.feature_importances_
            contributions = list(zip(X_df.columns, fi))
        except Exception:
            # last fallback: zero contributions
            contributions = [(c, 0.0) for c in X_df.columns]

    # sort by absolute magnitude
    contributions = sorted(contributions, key=lambda t: abs(t[1]), reverse=True)[:4]

    result = []
    for feat, contrib in contributions:
        pretty = FEATURE_REASON_MAP.get(feat, (feat.replace("_", " "), "No suggestion available"))
        result.append({
            'feature': feat,
            'contribution': float(contrib),
            'reason': pretty[0],
            'suggestion': pretty[1]
        })
    return result