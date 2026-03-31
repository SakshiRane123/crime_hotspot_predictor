import pandas as pd
import numpy as np

def create_advanced_features(df, stats=None):
    """
    Creates all advanced features for the crime hotspot model.
    Handles two modes:
    1. Training (stats=None): Calculates stats (quantiles, city averages)
       and returns them along with the feature-engineered dataframe.
    2. Prediction (stats provided): Uses the pre-calculated stats to
       engineer features for a single input row.
    """
    
    # --- Robust Stat Calculation ---
    if stats is None:
        # Training Mode: Calculate and store stats
        stats_to_save = {}
        
        # Calculate quantiles
        stats_to_save['quantiles'] = {
            'crime_q75': df['Previous_Crimes_Area'].quantile(0.75),
            'density_q75': df['Population_Density'].quantile(0.75)
        }
        
        # Calculate city-level aggregates
        stats_to_save['cities'] = df.groupby('City').agg(
            City_Crime_Rate=('Previous_Crimes_Area', 'mean'),
            City_Avg_Density=('Population_Density', 'mean'),
            City_Police_Distance=('Police_Station_Distance', 'mean')
        ).to_dict('index')
        
        # Store for use in this run
        calc_stats = stats_to_save
    else:
        # Prediction Mode: Load pre-calculated stats
        calc_stats = stats
        stats_to_save = None # We're not saving stats in prediction mode

    
    # --- Apply Features ---
    
    # Time-based features
    if 'Day_of_Week' in df.columns:
        df['Is_Weekend'] = df['Day_of_Week'].isin(['Saturday', 'Sunday']).astype(int)
        df['Is_Friday'] = (df['Day_of_Week'] == 'Friday').astype(int)
    
    if 'Time_Slot' in df.columns:
        df['Is_Night'] = (df['Time_Slot'] == 'Night').astype(int)
        df['Is_Evening'] = (df['Time_Slot'] == 'Evening').astype(int)
        df['Is_Late_Night'] = ((df['Time_Slot'] == 'Night') | (df['Time_Slot'] == 'Evening')).astype(int)

    if 'Month' in df.columns:
        df['Month'] = pd.to_numeric(df['Month'], errors='coerce').fillna(0)
        df['Month_Season'] = df['Month'].apply(lambda x: 
            0 if x in [12, 1, 2] else 1 if x in [3, 4, 5] else 2 if x in [6, 7, 8] else 3
        )
        df['Is_Summer'] = (df['Month_Season'] == 2).astype(int)
    
    # Crime type risk categories (if column exists)
    if 'Crime_Type' in df.columns:
        high_risk_crimes = ['Murder', 'Robbery', 'Assault', 'Burglary']
        medium_risk_crimes = ['Theft', 'Domestic Violence', 'Drug Offense']
        df['Crime_Risk_Category'] = df['Crime_Type'].apply(
            lambda x: 3 if x in high_risk_crimes else (2 if x in medium_risk_crimes else 1)
        )
    else:
        df['Crime_Risk_Category'] = 1 # Default to low risk if not provided

    # Police and patrol features
    if 'Patrol_Intensity' in df.columns:
        df['Patrol_Numeric'] = df['Patrol_Intensity'].map({'Low': 1, 'Medium': 2, 'High': 3})
    else:
        df['Patrol_Numeric'] = 2 # Default to Medium
        
    if 'Police_Station_Distance' in df.columns:
        df['Police_Coverage'] = 1 / (pd.to_numeric(df['Police_Station_Distance'], errors='coerce').fillna(5) + 0.1)
        df['Police_Effectiveness'] = df['Patrol_Numeric'] * df['Police_Coverage']
        df['Low_Police_Presence'] = ((df['Police_Station_Distance'] > 10) | (df['Patrol_Numeric'] == 1)).astype(int)
        df['High_Police_Presence'] = ((df['Police_Station_Distance'] < 2) & (df['Patrol_Numeric'] == 3)).astype(int)
        df['Distance_Squared'] = df['Police_Station_Distance'] ** 2

    # Crime density features
    if 'Previous_Crimes_Area' in df.columns and 'Population_Density' in df.columns:
        # Ensure numeric types
        prev_crimes = pd.to_numeric(df['Previous_Crimes_Area'], errors='coerce').fillna(0)
        pop_density = pd.to_numeric(df['Population_Density'], errors='coerce').fillna(0)

        df['Crime_Density_Ratio'] = prev_crimes / (pop_density / 1000 + 1)
        df['Crime_Per_1000_People'] = (prev_crimes / (pop_density + 1)) * 1000
        
        # Use saved quantiles
        crime_q75 = calc_stats['quantiles']['crime_q75']
        density_q75 = calc_stats['quantiles']['density_q75']
        
        df['High_Crime_Area'] = (prev_crimes > crime_q75).astype(int)
        df['High_Density_Area'] = (pop_density > density_q75).astype(int)
        df['Dense_High_Crime'] = (df['High_Crime_Area'] & df['High_Density_Area']).astype(int)

        # Interaction features
        df['Crime_Patrol_Interaction'] = prev_crimes * (4 - df['Patrol_Numeric'])
        df['Density_Distance_Interaction'] = pop_density * df['Police_Station_Distance']
        df['Night_Crime_Interaction'] = df['Is_Night'] * prev_crimes
        df['Weekend_Crime_Interaction'] = df['Is_Weekend'] * prev_crimes

        # Polynomial features
        df['Crimes_Squared'] = prev_crimes ** 2
        df['Density_Squared'] = pop_density ** 2
        
        # Bins need to be explicit for prediction
        df['Crime_Frequency_Category'] = pd.cut(prev_crimes, 
                                                bins=[-float('inf'), 25, 50, 75, float('inf')], 
                                                labels=[1, 2, 3, 4]).astype(float)

    # City-level aggregations
    if 'City' in df.columns:
        city_stats = calc_stats['cities']
        # Set default values (e.g., global mean) for unknown cities
        default_stats = {
            'City_Crime_Rate': np.mean([v['City_Crime_Rate'] for v in city_stats.values()]),
            'City_Avg_Density': np.mean([v['City_Avg_Density'] for v in city_stats.values()]),
            'City_Police_Distance': np.mean([v['City_Police_Distance'] for v in city_stats.values()]),
        }
        
        df['City_Crime_Rate'] = df['City'].apply(lambda x: city_stats.get(x, default_stats)['City_Crime_Rate'])
        df['City_Avg_Density'] = df['City'].apply(lambda x: city_stats.get(x, default_stats)['City_Avg_Density'])
        df['City_Police_Distance'] = df['City'].apply(lambda x: city_stats.get(x, default_stats)['City_Police_Distance'])
        
        df['City_Risk_Index'] = df['City_Crime_Rate'] / (df['City_Avg_Density'] / 1000 + 1)
        df['Above_City_Avg_Crime'] = (prev_crimes > df['City_Crime_Rate']).astype(int)

    # --- REMOVED TARGET LEAKAGE ---
    # We remove Severity_Score and Is_High_Severity as features.
    # We redefine Risk_Score without the leaky component.
    
    df['Risk_Score'] = (
        (prev_crimes / 100) * 0.25 +
        (pop_density / 30000) * 0.10 +
        (df['Police_Station_Distance'] / 20) * 0.15 +
        (4 - df['Patrol_Numeric']) / 3 * 0.10 +
        df['Is_Night'] * 0.08 +
        df['Is_Weekend'] * 0.05 +
        (df['Crime_Density_Ratio'] / 10) * 0.07 +
        (df['Crime_Risk_Category'] / 3) * 0.10
        # Removed: (df['Severity_Score'] / 4) * 0.10
    )
    
    df['Risk_Category'] = pd.cut(df['Risk_Score'], 
                                 bins=5, # Bins can be learned from data if needed
                                 labels=[1, 2, 3, 4, 5]).astype(float)

    return df, stats_to_save