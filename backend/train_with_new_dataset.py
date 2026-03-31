import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

print("="*70)
print("CRIME HOTSPOT PREDICTION - TRAINING WITH NEW DATASET")
print("="*70)

# ============================================================================
# STEP 1: Load Dataset
# ============================================================================
print("\n[1/9] Loading dataset...")
df = pd.read_csv(r'D:\EDAI_NEW2\EDAI_NEW2\crime-hotspot-predictor\new_dataset_10000.csv')
print(f"✓ Dataset loaded: {len(df)} records")
print(f"  Severity distribution: {df['Severity_Level'].value_counts().to_dict()}")

# ============================================================================
# STEP 2: Create Hotspot Label from Severity
# ============================================================================
print("\n[2/9] Creating hotspot labels...")
# Critical, High, Medium = Hotspot (1), Low = Safe (0)
df['Hotspot_Label'] = df['Severity_Level'].apply(
    lambda x: 1 if x in ['Critical', 'High', 'Medium'] else 0
)
print(f"✓ Hotspot distribution: {df['Hotspot_Label'].value_counts().to_dict()}")

# ============================================================================
# STEP 3: Feature Engineering
# ============================================================================
print("\n[3/9] Feature engineering...")

# Select relevant features for training
feature_columns = [
    'Day_of_Week', 'Month', 'Time_Slot', 'City', 'State',
    'Latitude_fixed', 'Longitude_fixed', 'Population_Density',
    'Previous_Crimes_Area', 'Police_Station_Distance', 'Patrol_Intensity',
    'Crime_Type', 'Age_Group_Mostly_Affected', 'Police_Station_Area'
]

# Create additional engineered features
df['City_Crime_Rate'] = df.groupby('City')['Previous_Crimes_Area'].transform('mean') / 100
df['Patrol_Numeric'] = df['Patrol_Intensity'].map({'Low': 1, 'Medium': 2, 'High': 3})
df['Police_Coverage'] = 1 / (df['Police_Station_Distance'] + 0.1)  # Avoid division by zero
df['Crime_Density_Ratio'] = df['Previous_Crimes_Area'] / (df['Population_Density'] / 1000 + 1)
df['Risk_Score'] = (
    (df['Previous_Crimes_Area'] / 20) * 0.4 +
    (df['Population_Density'] / 30000) * 0.2 +
    (df['Police_Station_Distance'] / 20) * 0.2 +
    df['Patrol_Numeric'].map({1: 0.3, 2: 0.15, 3: 0}) * 0.2
)

# Add engineered features to feature list
feature_columns.extend(['City_Crime_Rate', 'Patrol_Numeric', 'Police_Coverage', 
                       'Crime_Density_Ratio', 'Risk_Score'])

X = df[feature_columns].copy()
y_hotspot = df['Hotspot_Label']
y_severity = df['Severity_Level']

print(f"✓ Using {len(feature_columns)} features")

# ============================================================================
# STEP 4: Encode Categorical Variables
# ============================================================================
print("\n[4/9] Encoding categorical variables...")
label_encoders = {}
categorical_cols = ['Day_of_Week', 'Month', 'Time_Slot', 'City', 'State', 
                   'Patrol_Intensity', 'Crime_Type', 'Age_Group_Mostly_Affected', 
                   'Police_Station_Area']

for col in categorical_cols:
    if col in X.columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le

severity_encoder = LabelEncoder()
y_severity_encoded = severity_encoder.fit_transform(y_severity)

print(f"✓ Encoded {len([c for c in categorical_cols if c in X.columns])} categorical columns")

# ============================================================================
# STEP 5: Handle Missing Values
# ============================================================================
print("\n[5/9] Handling missing values...")
X = X.fillna(X.median(numeric_only=True))
print("✓ Missing values handled")

# ============================================================================
# STEP 6: Scale Features
# ============================================================================
print("\n[6/9] Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("✓ Features scaled")

# ============================================================================
# STEP 7: Split Data
# ============================================================================
print("\n[7/9] Splitting data...")
X_train, X_test, y_hotspot_train, y_hotspot_test, y_severity_train, y_severity_test = train_test_split(
    X_scaled, y_hotspot, y_severity_encoded, test_size=0.2, random_state=42, stratify=y_hotspot
)
print(f"✓ Training: {len(X_train)} samples | Testing: {len(X_test)} samples")

# ============================================================================
# STEP 8: Train Models
# ============================================================================
print("\n[8/9] Training models...")

# Hotspot Detection Model
print("  → Training Hotspot Detection Model...")
hotspot_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)
hotspot_model.fit(X_train, y_hotspot_train)
print("  ✓ Hotspot model trained")

# Severity Classification Model
print("  → Training Severity Classification Model...")
severity_model = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=10,
    random_state=42,
    subsample=0.8
)
severity_model.fit(X_train, y_severity_train)
print("  ✓ Severity model trained")

# ============================================================================
# STEP 9: Evaluate Models
# ============================================================================
print("\n[9/9] Evaluating models...")

# Hotspot predictions
y_hotspot_pred = hotspot_model.predict(X_test)
hotspot_accuracy = accuracy_score(y_hotspot_test, y_hotspot_pred)

print(f"\n🎯 HOTSPOT DETECTION ACCURACY: {hotspot_accuracy*100:.2f}%")
print("\nHotspot Classification Report:")
print(classification_report(y_hotspot_test, y_hotspot_pred, 
                          target_names=['Safe', 'Hotspot'], zero_division=0))

# Severity predictions
y_severity_pred = severity_model.predict(X_test)
severity_accuracy = accuracy_score(y_severity_test, y_severity_pred)

print(f"\n🎯 SEVERITY CLASSIFICATION ACCURACY: {severity_accuracy*100:.2f}%")
print("\nSeverity Classification Report:")
print(classification_report(y_severity_test, y_severity_pred,
                          target_names=severity_encoder.classes_, zero_division=0))

# Feature importance
print("\n📊 Top 15 Most Important Features:")
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': hotspot_model.feature_importances_
}).sort_values('importance', ascending=False).head(15)
print(feature_importance.to_string(index=False))

# ============================================================================
# STEP 10: Save Models
# ============================================================================
print("\n[10/10] Saving models...")
joblib.dump(hotspot_model, 'hotspot_model.pkl')
joblib.dump(severity_model, 'severity_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')
joblib.dump(severity_encoder, 'severity_encoder.pkl')
joblib.dump(feature_columns, 'feature_columns.pkl')

print("✓ All models saved successfully")

print("\n" + "="*70)
print("✅ MODEL TRAINING COMPLETE!")
print("="*70)
print(f"\nFinal Performance:")
print(f"  • Hotspot Detection: {hotspot_accuracy*100:.2f}%")
print(f"  • Severity Classification: {severity_accuracy*100:.2f}%")
print(f"\nDataset Used:")
print(f"  • Total samples: {len(df)}")
print(f"  • Features: {len(feature_columns)}")
print(f"  • Cities covered: {df['City'].nunique()}")
print(f"  • Crime types: {df['Crime_Type'].nunique()}")
print(f"\nModels ready for predictions! 🚀")
