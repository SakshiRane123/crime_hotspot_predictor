import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

print("="*70)
print("CRIME HOTSPOT PREDICTION - HIGH ACCURACY TRAINING")
print("="*70)


df = pd.read_csv(r'D:\EDAI_NEW2\EDAI_NEW2\crime-hotspot-predictor\new_dataset_10000.csv')
print(f"✓ Dataset loaded: {len(df)} records")

# ============================================================================
# STEP 2: Create Hotspot Label from Severity
# ============================================================================
print("\n[2/10] Creating hotspot labels...")
df['Hotspot_Label'] = df['Severity_Level'].apply(
    lambda x: 1 if x in ['Critical', 'High', 'Medium'] else 0
)
print(f"✓ Hotspot distribution: {df['Hotspot_Label'].value_counts().to_dict()}")

# ============================================================================
# STEP 3: Advanced Feature Engineering
# ============================================================================
print("\n[3/10] Advanced feature engineering...")

# Time-based features
df['Is_Weekend'] = df['Day_of_Week'].isin(['Saturday', 'Sunday']).astype(int)
df['Is_Night'] = df['Time_Slot'].isin(['Night', 'Evening']).astype(int)
df['Month_Season'] = df['Month'].apply(lambda x: 
    0 if x in [12, 1, 2] else  # Winter
    1 if x in [3, 4, 5] else    # Spring
    2 if x in [6, 7, 8] else    # Summer
    3                            # Fall
)

# Crime severity mapping
severity_score_map = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
df['Severity_Score'] = df['Severity_Level'].map(severity_score_map)

# Police effectiveness metrics
df['Patrol_Numeric'] = df['Patrol_Intensity'].map({'Low': 1, 'Medium': 2, 'High': 3})
df['Police_Coverage'] = 1 / (df['Police_Station_Distance'] + 0.1)
df['Police_Effectiveness'] = df['Patrol_Numeric'] * df['Police_Coverage']

# Crime density and risk metrics
df['Crime_Density_Ratio'] = df['Previous_Crimes_Area'] / (df['Population_Density'] / 1000 + 1)
df['Crime_Per_1000_People'] = (df['Previous_Crimes_Area'] / df['Population_Density']) * 1000
df['High_Crime_Area'] = (df['Previous_Crimes_Area'] > df['Previous_Crimes_Area'].median()).astype(int)
df['High_Density_Area'] = (df['Population_Density'] > df['Population_Density'].median()).astype(int)

# City-level statistics
df['City_Crime_Rate'] = df.groupby('City')['Previous_Crimes_Area'].transform('mean')
df['City_Avg_Density'] = df.groupby('City')['Population_Density'].transform('mean')
df['City_Risk_Index'] = df['City_Crime_Rate'] / (df['City_Avg_Density'] / 1000 + 1)

# Composite risk score (weighted features)
df['Risk_Score'] = (
    (df['Previous_Crimes_Area'] / 100) * 0.30 +           # Historical crimes (30%)
    (df['Population_Density'] / 30000) * 0.15 +           # Population density (15%)
    (df['Police_Station_Distance'] / 20) * 0.20 +         # Police distance (20%)
    (4 - df['Patrol_Numeric']) / 3 * 0.15 +               # Patrol intensity (15%)
    df['Is_Night'] * 0.10 +                                # Night time (10%)
    df['Is_Weekend'] * 0.05 +                              # Weekend (5%)
    (df['Crime_Density_Ratio'] / 10) * 0.05                # Crime density (5%)
)

# Select features
feature_columns = [
    'Day_of_Week', 'Month', 'Time_Slot', 'City', 'State',
    'Latitude_fixed', 'Longitude_fixed', 'Population_Density',
    'Previous_Crimes_Area', 'Police_Station_Distance', 'Patrol_Intensity',
    'Crime_Type', 'Age_Group_Mostly_Affected', 'Police_Station_Area',
    'Is_Weekend', 'Is_Night', 'Month_Season', 'Severity_Score',
    'Patrol_Numeric', 'Police_Coverage', 'Police_Effectiveness',
    'Crime_Density_Ratio', 'Crime_Per_1000_People', 'High_Crime_Area',
    'High_Density_Area', 'City_Crime_Rate', 'City_Avg_Density',
    'City_Risk_Index', 'Risk_Score'
]

X = df[feature_columns].copy()
y_hotspot = df['Hotspot_Label']
y_severity = df['Severity_Level']

print(f"✓ Using {len(feature_columns)} features (including {len(feature_columns) - 14} engineered)")

# ============================================================================
# STEP 4: Encode Categorical Variables
# ============================================================================
print("\n[4/10] Encoding categorical variables...")
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
print("\n[5/10] Handling missing values...")
X = X.fillna(X.median(numeric_only=True))
print("✓ Missing values handled")

# ============================================================================
# STEP 6: Scale Features
# ============================================================================
print("\n[6/10] Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("✓ Features scaled")

# ============================================================================
# STEP 7: Split Data
# ============================================================================
print("\n[7/10] Splitting data...")
X_train, X_test, y_hotspot_train, y_hotspot_test, y_severity_train, y_severity_test = train_test_split(
    X_scaled, y_hotspot, y_severity_encoded, test_size=0.2, random_state=42, stratify=y_hotspot
)
print(f"✓ Training: {len(X_train)} samples | Testing: {len(X_test)} samples")

# ============================================================================
# STEP 8: Train Hotspot Model with Ensemble
# ============================================================================
print("\n[8/10] Training Hotspot Detection Model (Ensemble)...")

# Multiple models for voting
rf_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=25,
    min_samples_split=4,
    min_samples_leaf=2,
    max_features='sqrt',
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)

gb_model = GradientBoostingClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=12,
    min_samples_split=4,
    subsample=0.8,
    random_state=42
)

# Voting ensemble
hotspot_model = VotingClassifier(
    estimators=[('rf', rf_model), ('gb', gb_model)],
    voting='soft',
    n_jobs=-1
)

hotspot_model.fit(X_train, y_hotspot_train)
print("  ✓ Hotspot ensemble model trained")

# Cross-validation
cv_scores = cross_val_score(hotspot_model, X_train, y_hotspot_train, cv=5, n_jobs=-1)
print(f"  ✓ Cross-validation accuracy: {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*100:.2f}%)")

# ============================================================================
# STEP 9: Train Severity Model
# ============================================================================
print("\n[9/10] Training Severity Classification Model...")

severity_model = GradientBoostingClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=15,
    min_samples_split=4,
    subsample=0.8,
    random_state=42
)

severity_model.fit(X_train, y_severity_train)
print("  ✓ Severity model trained")

# ============================================================================
# STEP 10: Evaluate Models
# ============================================================================
print("\n[10/10] Evaluating models...")

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

# Feature importance (from Random Forest in ensemble)
print("\n📊 Top 20 Most Important Features:")
try:
    # Get the fitted RF model from the ensemble
    fitted_rf = hotspot_model.named_estimators_['rf']
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': fitted_rf.feature_importances_
    }).sort_values('importance', ascending=False).head(20)
    print(feature_importance.to_string(index=False))
except:
    print("  (Feature importance display skipped)")

# ============================================================================
# STEP 11: Save Models
# ============================================================================
print("\n[11/11] Saving models...")
joblib.dump(hotspot_model, 'hotspot_model.pkl')
joblib.dump(severity_model, 'severity_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')
joblib.dump(severity_encoder, 'severity_encoder.pkl')
joblib.dump(feature_columns, 'feature_columns.pkl')

print("✓ All models saved successfully")

print("\n" + "="*70)
print("✅ HIGH ACCURACY MODEL TRAINING COMPLETE!")
print("="*70)
print(f"\nFinal Performance:")
print(f"  • Hotspot Detection: {hotspot_accuracy*100:.2f}%")
print(f"  • Severity Classification: {severity_accuracy*100:.2f}%")
print(f"\nKey Improvements:")
print(f"  ✓ Ensemble voting (Random Forest + Gradient Boosting)")
print(f"  ✓ {len(feature_columns)} total features with advanced engineering")
print(f"  ✓ Optimized hyperparameters")
print(f"  ✓ Cross-validation: {cv_scores.mean()*100:.2f}% accuracy")
print(f"  ✓ Class balancing for imbalanced data")
print(f"\nModels ready for accurate predictions! 🚀")
