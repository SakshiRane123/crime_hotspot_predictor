import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("CRIME HOTSPOT PREDICTION - HYBRID MODEL TRAINING")
print("=" * 60)

# Load dataset
print("\n[1/7] Loading dataset...")
df = pd.read_csv('../crime_hotspot_city_state_fixed.csv')
print(f"✓ Dataset loaded: {df.shape[0]} records, {df.shape[1]} features")
print(f"Dataset file: crime_hotspot_city_state_fixed.csv")

# Display dataset info
print(f"\nDataset columns: {list(df.columns)}")
print(f"\nSeverity levels: {df['Severity_Level'].unique()}")
print(f"Severity distribution:\n{df['Severity_Level'].value_counts()}")

# Feature engineering
print("\n[2/7] Engineering features...")

# Select relevant features for prediction
feature_columns = [
    'Day_of_Week', 'Month', 'Time_Slot',
    'Latitude_fixed', 'Longitude_fixed', 'City', 'State',
    'Population_Density', 'Previous_Crimes_Area',
    'Police_Station_Distance', 'Patrol_Intensity'
]

# Create target variables
# Hotspot_Label: 1 if Critical or High, else 0
df['Hotspot_Label'] = df['Severity_Level'].apply(lambda x: 1 if x in ['Critical', 'High'] else 0)

# Prepare features
X = df[feature_columns].copy()
y_hotspot = df['Hotspot_Label']
y_severity = df['Severity_Level']

print(f"✓ Features selected: {len(feature_columns)} columns")
print(f"✓ Hotspot distribution: {y_hotspot.value_counts().to_dict()}")

# Encode categorical variables
print("\n[3/7] Encoding categorical variables...")
label_encoders = {}
categorical_cols = ['Day_of_Week', 'Month', 'Time_Slot', 'City', 'State', 'Patrol_Intensity']

for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))
    label_encoders[col] = le

# Encode severity levels
severity_encoder = LabelEncoder()
y_severity_encoded = severity_encoder.fit_transform(y_severity)

print(f"✓ Encoded {len(categorical_cols)} categorical columns")

# Scale numerical features
print("\n[4/7] Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("✓ Features scaled")

# Split data
print("\n[5/7] Splitting data...")
X_train, X_test, y_hotspot_train, y_hotspot_test, y_severity_train, y_severity_test = train_test_split(
    X_scaled, y_hotspot, y_severity_encoded, test_size=0.2, random_state=42, stratify=y_hotspot
)
print(f"✓ Training set: {X_train.shape[0]} samples")
print(f"✓ Testing set: {X_test.shape[0]} samples")

# Train Hybrid Model for Hotspot Detection
print("\n[6/7] Training Hybrid Ensemble Model...")
print("Model architecture: Random Forest + Extra Trees + Gradient Boosting")

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier

# Create individual models
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)

et_model = ExtraTreesClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)

gb_model = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=8,
    learning_rate=0.1,
    random_state=42
)

# Create hybrid voting classifier
hybrid_model = VotingClassifier(
    estimators=[
        ('rf', rf_model),
        ('et', et_model),
        ('gb', gb_model)
    ],
    voting='soft',
    n_jobs=-1
)

print("  → Training hotspot detection model...")
hybrid_model.fit(X_train, y_hotspot_train)
print("  ✓ Hotspot model trained")

# Train severity model
print("  → Training severity classification model...")
severity_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)
severity_model.fit(X_train, y_severity_train)
print("  ✓ Severity model trained")

# Evaluate models
print("\n[7/7] Evaluating models...")

# Hotspot prediction
y_hotspot_pred = hybrid_model.predict(X_test)
hotspot_accuracy = accuracy_score(y_hotspot_test, y_hotspot_pred)
print(f"\n🎯 HOTSPOT DETECTION ACCURACY: {hotspot_accuracy:.2%}")
print("\nHotspot Classification Report:")
print(classification_report(y_hotspot_test, y_hotspot_pred, target_names=['Safe', 'Hotspot']))

# Severity prediction
y_severity_pred = severity_model.predict(X_test)
severity_accuracy = accuracy_score(y_severity_test, y_severity_pred)
print(f"\n🎯 SEVERITY CLASSIFICATION ACCURACY: {severity_accuracy:.2%}")
print("\nSeverity Classification Report:")
print(classification_report(y_severity_test, y_severity_pred, 
                           target_names=severity_encoder.classes_))

# Feature importance
print("\n📊 Top 10 Most Important Features:")
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': hybrid_model.estimators_[0].feature_importances_  # From Random Forest
}).sort_values('importance', ascending=False).head(10)
print(feature_importance.to_string(index=False))

# Save models and encoders
print("\n[8/8] Saving models and encoders...")
joblib.dump(hybrid_model, 'hotspot_model.pkl')
joblib.dump(severity_model, 'severity_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')
joblib.dump(severity_encoder, 'severity_encoder.pkl')
joblib.dump(feature_columns, 'feature_columns.pkl')

print("✓ hotspot_model.pkl")
print("✓ severity_model.pkl")
print("✓ scaler.pkl")
print("✓ label_encoders.pkl")
print("✓ severity_encoder.pkl")
print("✓ feature_columns.pkl")

print("\n" + "=" * 60)
print("✅ MODEL TRAINING COMPLETE!")
print("=" * 60)
print(f"\nFinal Performance:")
print(f"  • Hotspot Detection: {hotspot_accuracy:.2%}")
print(f"  • Severity Classification: {severity_accuracy:.2%}")
print(f"\nModels saved in backend/ directory")
print("Ready to use for predictions! 🚀")
