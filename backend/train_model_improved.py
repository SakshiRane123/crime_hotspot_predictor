import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("CRIME HOTSPOT PREDICTION - IMPROVED MODEL TRAINING")
print("=" * 70)

# Load dataset
print("\n[1/9] Loading dataset...")
df = pd.read_csv('../crime_hotspot_city_state_fixed.csv')
print(f"✓ Dataset loaded: {df.shape[0]} records, {df.shape[1]} features")

# Feature engineering
print("\n[2/9] Advanced feature engineering...")

# Create target variables
df['Hotspot_Label'] = df['Severity_Level'].apply(lambda x: 1 if x in ['Critical', 'High'] else 0)

# Enhanced features
df['Crime_Density_Ratio'] = df['Previous_Crimes_Area'] / (df['Population_Density'] + 1)
df['Police_Coverage'] = 1 / (df['Police_Station_Distance'] + 0.1)
df['Risk_Score'] = (df['Previous_Crimes_Area'] * df['Police_Station_Distance']) / (df['Population_Density'] + 1)

# Time-based features
df['Is_Weekend'] = df['Day_of_Week'].isin(['Saturday', 'Sunday']).astype(int)
df['Is_Night'] = df['Time_Slot'].isin(['Night', 'Evening']).astype(int)
df['Is_Peak_Crime_Month'] = df['Month'].isin([10, 11, 12, 1, 2]).astype(int)  # Winter months

# Patrol effectiveness
patrol_map = {'Low': 0, 'Medium': 1, 'High': 2}
df['Patrol_Numeric'] = df['Patrol_Intensity'].map(patrol_map)

# Geographic clustering (city crime reputation)
city_crime_rate = df.groupby('City')['Hotspot_Label'].mean()
df['City_Crime_Rate'] = df['City'].map(city_crime_rate)

# State crime rate
state_crime_rate = df.groupby('State')['Hotspot_Label'].mean()
df['State_Crime_Rate'] = df['State'].map(state_crime_rate)

print(f"✓ Created 9 new engineered features")

# Select features
base_features = [
    'Day_of_Week', 'Month', 'Time_Slot',
    'Latitude_fixed', 'Longitude_fixed', 'City', 'State',
    'Population_Density', 'Previous_Crimes_Area',
    'Police_Station_Distance', 'Patrol_Intensity'
]

engineered_features = [
    'Crime_Density_Ratio', 'Police_Coverage', 'Risk_Score',
    'Is_Weekend', 'Is_Night', 'Is_Peak_Crime_Month',
    'Patrol_Numeric', 'City_Crime_Rate', 'State_Crime_Rate'
]

feature_columns = base_features + engineered_features

# Prepare features
X = df[base_features + ['Crime_Density_Ratio', 'Police_Coverage', 'Risk_Score',
                         'Is_Weekend', 'Is_Night', 'Is_Peak_Crime_Month',
                         'Patrol_Numeric', 'City_Crime_Rate', 'State_Crime_Rate']].copy()
y_hotspot = df['Hotspot_Label']
y_severity = df['Severity_Level']

print(f"✓ Total features: {len(X.columns)}")

# Encode categorical variables
print("\n[3/9] Encoding categorical variables...")
label_encoders = {}
categorical_cols = ['Day_of_Week', 'Month', 'Time_Slot', 'City', 'State', 'Patrol_Intensity']

for col in categorical_cols:
    if col in X.columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le

# Encode severity levels
severity_encoder = LabelEncoder()
y_severity_encoded = severity_encoder.fit_transform(y_severity)

print(f"✓ Encoded {len(categorical_cols)} categorical columns")

# Handle any NaN values
X = X.fillna(X.mean())

# Scale features
print("\n[4/9] Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("✓ Features scaled")

# Split data with stratification
print("\n[5/9] Splitting data...")
X_train, X_test, y_hotspot_train, y_hotspot_test, y_severity_train, y_severity_test = train_test_split(
    X_scaled, y_hotspot, y_severity_encoded, test_size=0.2, random_state=42, stratify=y_hotspot
)
print(f"✓ Training set: {X_train.shape[0]} samples")
print(f"✓ Testing set: {X_test.shape[0]} samples")

# Train Enhanced Hotspot Detection Model
print("\n[6/9] Training Enhanced Hotspot Detection Model...")
print("Using XGBoost + Random Forest + Gradient Boosting Stacking")

# Base models with optimized hyperparameters
rf_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=20,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)

xgb_model = XGBClassifier(
    n_estimators=300,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    scale_pos_weight=1
)

gb_model = GradientBoostingClassifier(
    n_estimators=200,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.8,
    random_state=42
)

# Stacking ensemble
meta_model = LogisticRegression(max_iter=1000, random_state=42)

stacking_model = StackingClassifier(
    estimators=[
        ('rf', rf_model),
        ('xgb', xgb_model),
        ('gb', gb_model)
    ],
    final_estimator=meta_model,
    cv=5,
    n_jobs=-1
)

print("  → Training stacked ensemble model...")
stacking_model.fit(X_train, y_hotspot_train)
print("  ✓ Hotspot model trained")

# Cross-validation
print("  → Performing cross-validation...")
cv_scores = cross_val_score(stacking_model, X_train, y_hotspot_train, cv=5, scoring='accuracy')
print(f"  ✓ CV Accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std() * 2:.2%})")

# Train Enhanced Severity Model
print("\n[7/9] Training Enhanced Severity Classification Model...")

severity_rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=25,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)

severity_xgb = XGBClassifier(
    n_estimators=300,
    max_depth=10,
    learning_rate=0.05,
    random_state=42,
    n_jobs=-1
)

severity_meta = LogisticRegression(max_iter=1000, random_state=42, multi_class='multinomial')

severity_stacking = StackingClassifier(
    estimators=[
        ('rf', severity_rf),
        ('xgb', severity_xgb)
    ],
    final_estimator=severity_meta,
    cv=5,
    n_jobs=-1
)

print("  → Training severity stacking model...")
severity_stacking.fit(X_train, y_severity_train)
print("  ✓ Severity model trained")

# Evaluate models
print("\n[8/9] Evaluating models...")

# Hotspot prediction
y_hotspot_pred = stacking_model.predict(X_test)
hotspot_accuracy = accuracy_score(y_hotspot_test, y_hotspot_pred)
print(f"\n🎯 HOTSPOT DETECTION ACCURACY: {hotspot_accuracy:.2%}")
print("\nHotspot Classification Report:")
print(classification_report(y_hotspot_test, y_hotspot_pred, target_names=['Safe', 'Hotspot']))

# Severity prediction
y_severity_pred = severity_stacking.predict(X_test)
severity_accuracy = accuracy_score(y_severity_test, y_severity_pred)
print(f"\n🎯 SEVERITY CLASSIFICATION ACCURACY: {severity_accuracy:.2%}")
print("\nSeverity Classification Report:")
print(classification_report(y_severity_test, y_severity_pred, target_names=severity_encoder.classes_))

# Feature importance (from RF base estimator)
print("\n📊 Top 15 Most Important Features:")
rf_base = stacking_model.named_estimators_['rf']
feature_names = list(X.columns)
feature_importance = pd.DataFrame({
    'feature': feature_names,
    'importance': rf_base.feature_importances_
}).sort_values('importance', ascending=False).head(15)
print(feature_importance.to_string(index=False))

# Save models and encoders
print("\n[9/9] Saving enhanced models...")
joblib.dump(stacking_model, 'hotspot_model.pkl')
joblib.dump(severity_stacking, 'severity_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')
joblib.dump(severity_encoder, 'severity_encoder.pkl')
joblib.dump(list(X.columns), 'feature_columns.pkl')

print("✓ hotspot_model.pkl (Stacking Ensemble)")
print("✓ severity_model.pkl (Stacking Ensemble)")
print("✓ scaler.pkl")
print("✓ label_encoders.pkl")
print("✓ severity_encoder.pkl")
print("✓ feature_columns.pkl")

print("\n" + "=" * 70)
print("✅ ENHANCED MODEL TRAINING COMPLETE!")
print("=" * 70)
print(f"\nFinal Performance:")
print(f"  • Hotspot Detection: {hotspot_accuracy:.2%}")
print(f"  • Severity Classification: {severity_accuracy:.2%}")
print(f"  • Improvement Techniques:")
print(f"    - Feature Engineering (9 new features)")
print(f"    - XGBoost + RF + GB Stacking")
print(f"    - Optimized Hyperparameters")
print(f"    - Cross-Validation")
print(f"    - Class Balancing")
print(f"\nModels saved in backend/ directory")
print("Ready for high-accuracy predictions! 🚀")