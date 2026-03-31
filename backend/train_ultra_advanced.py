import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, ExtraTreesClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score
import joblib
import warnings
# Import the new feature engineering function
from feature_engineering import create_advanced_features

warnings.filterwarnings('ignore')

print("="*70)
print("CRIME HOTSPOT PREDICTION - ULTRA ADVANCED TRAINING (FIXED)")
print("="*70)

# ============================================================================
# STEP 1: Load Dataset
# ============================================================================
print("\n[1/12] Loading dataset...")
# Use raw string for file path
df = pd.read_csv(r'D:\EDAI_NEW2\EDAI_NEW2\crime-hotspot-predictor\new_dataset_10000.csv')
print(f"✓ Dataset loaded: {len(df)} records")

# ============================================================================
# STEP 2: Create Hotspot Label from Severity
# ============================================================================
print("\n[2/12] Creating hotspot labels...")
df['Hotspot_Label'] = df['Severity_Level'].apply(
    lambda x: 1 if x in ['Critical', 'High', 'Medium'] else 0
)
print(f"✓ Hotspot distribution: {df['Hotspot_Label'].value_counts().to_dict()}")

# ============================================================================
# STEP 3: Ultra-Advanced Feature Engineering (Using external function)
# ============================================================================
print("\n[3/12] Ultra-advanced feature engineering...")
# Call the centralized function
# It returns the dataframe and the stats (quantiles, city averages) to save
(df, model_stats) = create_advanced_features(df, stats=None)
print("✓ Feature engineering complete.")


# ============================================================================
# STEP 4: Define Feature Columns (Leaky features removed)
# ============================================================================
print("\n[4/12] Defining feature columns...")

# Select ALL non-leaky features
feature_columns = [
    'Day_of_Week', 'Month', 'Time_Slot', 'City', 'State',
    'Latitude_fixed', 'Longitude_fixed', 'Population_Density',
    'Previous_Crimes_Area', 'Police_Station_Distance', 'Patrol_Intensity',
    'Crime_Type', 'Age_Group_Mostly_Affected', 'Police_Station_Area',
    'Is_Weekend', 'Is_Friday', 'Is_Night', 'Is_Evening', 'Is_Late_Night',
    'Month_Season', 'Is_Summer',
    # --- REMOVED LEAKY FEATURES ---
    # 'Severity_Score', 'Is_High_Severity',
    # ------------------------------
    'Crime_Risk_Category', 'Patrol_Numeric', 'Police_Coverage', 
    'Police_Effectiveness', 'Low_Police_Presence', 'High_Police_Presence',
    'Crime_Density_Ratio', 'Crime_Per_1000_People', 'Crime_Frequency_Category',
    'High_Crime_Area', 'High_Density_Area', 'Dense_High_Crime',
    'City_Crime_Rate', 'City_Avg_Density', 'City_Risk_Index', 
    'City_Police_Distance', 'Above_City_Avg_Crime',
    'Crime_Patrol_Interaction', 'Density_Distance_Interaction',
    'Night_Crime_Interaction', 'Weekend_Crime_Interaction',
    'Crimes_Squared', 'Distance_Squared', 'Density_Squared',
    'Risk_Score', 'Risk_Category'
]

# Ensure all columns exist, fill missing ones if any (e.g., from feature_engineering)
for col in feature_columns:
    if col not in df.columns:
        print(f"Warning: Column '{col}' not found. Filling with 0.")
        df[col] = 0

X = df[feature_columns].copy()
y_hotspot = df['Hotspot_Label']
y_severity = df['Severity_Level']

print(f"✓ Using {len(feature_columns)} features (target-leakage removed)")

# ============================================================================
# STEP 5: Encode Categorical Variables
# ============================================================================
print("\n[5/12] Encoding categorical variables...")
label_encoders = {}
categorical_cols = ['Day_of_Week', 'Month', 'Time_Slot', 'City', 'State', 
                   'Patrol_Intensity', 'Crime_Type', 'Age_Group_Mostly_Affected', 
                   'Police_Station_Area']

for col in categorical_cols:
    if col in X.columns:
        # Convert to string and fillna to avoid errors
        X[col] = X[col].astype(str).fillna('Unknown')
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        label_encoders[col] = le

severity_encoder = LabelEncoder()
y_severity_encoded = severity_encoder.fit_transform(y_severity)

print(f"✓ Encoded {len([c for c in categorical_cols if c in X.columns])} categorical columns")

# ============================================================================
# STEP 6: Handle Missing Values
# ============================================================================
print("\n[6/12] Handling missing values...")
# Fill any remaining NaNs with the column median
X = X.fillna(X.median(numeric_only=True))
print("✓ Missing values handled")

# ============================================================================
# STEP 7: Advanced Scaling with RobustScaler
# ============================================================================
print("\n[7/12] Scaling features (RobustScaler for outlier resistance)...")
scaler = RobustScaler()
X_scaled = scaler.fit_transform(X)
print("✓ Features scaled")

# ============================================================================
# STEP 8: Split Data with Stratification
# ============================================================================
print("\n[8/12] Splitting data...")
X_train, X_test, y_hotspot_train, y_hotspot_test, y_severity_train, y_severity_test = train_test_split(
    X_scaled, y_hotspot, y_severity_encoded, test_size=0.15, random_state=42, stratify=y_hotspot
)
print(f"✓ Training: {len(X_train)} samples | Testing: {len(X_test)} samples")

# ============================================================================
# STEP 9: Train Ultra-Advanced Hotspot Model
# ============================================================================
print("\n[9/12] Training Ultra-Advanced Hotspot Detection Model...")

# Model 1: Random Forest
rf_model = RandomForestClassifier(
    n_estimators=500, max_depth=30, min_samples_split=2, min_samples_leaf=1,
    max_features='sqrt', bootstrap=True, random_state=42, class_weight='balanced', n_jobs=-1
)
# Model 2: Gradient Boosting
gb_model = GradientBoostingClassifier(
    n_estimators=500, learning_rate=0.03, max_depth=15, min_samples_split=2,
    subsample=0.8, random_state=42
)
# Model 3: Extra Trees
et_model = ExtraTreesClassifier(
    n_estimators=500, max_depth=30, min_samples_split=2, random_state=42,
    class_weight='balanced', n_jobs=-1
)
# Triple ensemble voting
hotspot_model = VotingClassifier(
    estimators=[('rf', rf_model), ('gb', gb_model), ('et', et_model)],
    voting='soft', n_jobs=-1
)
hotspot_model.fit(X_train, y_hotspot_train)
print("  ✓ Triple-ensemble hotspot model trained")

# Stratified K-Fold Cross-validation
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
cv_scores = cross_val_score(hotspot_model, X_train, y_hotspot_train, cv=skf, n_jobs=-1, scoring='accuracy')
print(f"  ✓ 10-Fold CV accuracy: {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*100:.2f}%)")

# ============================================================================
# STEP 10: Train Advanced Severity Model
# ============================================================================
print("\n[10/12] Training Advanced Severity Classification Model...")
severity_model = GradientBoostingClassifier(
    n_estimators=500, learning_rate=0.03, max_depth=20, min_samples_split=2,
    subsample=0.8, random_state=42
)
severity_model.fit(X_train, y_severity_train)
print("  ✓ Severity model trained")

# ============================================================================
# STEP 11: Evaluate Models
# ============================================================================
print("\n[11/12] Evaluating models...")

# Hotspot predictions
y_hotspot_pred = hotspot_model.predict(X_test)
hotspot_accuracy = accuracy_score(y_hotspot_test, y_hotspot_pred)
hotspot_f1 = f1_score(y_hotspot_test, y_hotspot_pred, average='weighted')
print(f"\n🎯 HOTSPOT DETECTION ACCURACY: {hotspot_accuracy*100:.2f}%")
print(f"📊 F1-Score: {hotspot_f1*100:.2f}%")
print("\nHotspot Classification Report:")
print(classification_report(y_hotspot_test, y_hotspot_pred, target_names=['Safe', 'Hotspot'], zero_division=0))

# Severity predictions
y_severity_pred = severity_model.predict(X_test)
severity_accuracy = accuracy_score(y_severity_test, y_severity_pred)
severity_f1 = f1_score(y_severity_test, y_severity_pred, average='weighted')
print(f"\n🎯 SEVERITY CLASSIFICATION ACCURACY: {severity_accuracy*100:.2f}%")
print(f"📊 F1-Score: {severity_f1*100:.2f}%")
print("\nSeverity Classification Report:")
print(classification_report(y_severity_test, y_severity_pred, target_names=severity_encoder.classes_, zero_division=0))

# Feature importance
print("\n📊 Top 25 Most Important Features:")
try:
    fitted_rf = hotspot_model.named_estimators_['rf']
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': fitted_rf.feature_importances_
    }).sort_values('importance', ascending=False).head(25)
    print(feature_importance.to_string(index=False))
except Exception as e:
    print(f"  (Feature importance display skipped: {e})")

# ============================================================================
# STEP 12: Save Models
# ============================================================================
print("\n[12/12] Saving ultra-advanced models...")
joblib.dump(hotspot_model, 'hotspot_model.pkl')
joblib.dump(severity_model, 'severity_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')
joblib.dump(severity_encoder, 'severity_encoder.pkl')
joblib.dump(feature_columns, 'feature_columns.pkl')
# --- SAVE THE NEW STATS FILE ---
joblib.dump(model_stats, 'model_stats.pkl')
print("✓ All models and stats saved successfully")

