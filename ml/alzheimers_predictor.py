import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import warnings
warnings.filterwarnings('ignore')

class AlzheimersPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None

    def load_and_preprocess_data(self, file_path):
        """Load and preprocess the Alzheimer's disease dataset"""
        print("Loading data...")
        df = pd.read_csv(file_path)

        # Remove PatientID and DoctorInCharge columns as they're not predictive features
        df = df.drop(['PatientID', 'DoctorInCharge'], axis=1)

        # Separate features and target
        X = df.drop('Diagnosis', axis=1)
        y = df['Diagnosis']

        print(f"Dataset shape: {df.shape}")
        print(f"Features: {X.shape[1]}")
        print(f"Diagnosis distribution:")
        print(y.value_counts())

        self.feature_names = X.columns.tolist()
        return X, y

    def train_model(self, X, y, test_size=0.2, random_state=42):
        """Train the Random Forest model"""
        print("\nSplitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Scale the features
        print("Scaling features...")
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train Random Forest model
        print("Training Random Forest model...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            class_weight='balanced'
        )

        self.model.fit(X_train_scaled, y_train)

        # Make predictions
        y_pred = self.model.predict(X_test_scaled)

        # Evaluate model
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\nModel Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))

        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        print("\nTop 10 Most Important Features:")
        print(feature_importance.head(10))

        return accuracy, feature_importance

    def predict_diagnosis(self, patient_data):
        """Predict diagnosis for a new patient"""
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained yet. Please train the model first.")

        # Convert to DataFrame if it's a dictionary
        if isinstance(patient_data, dict):
            patient_df = pd.DataFrame([patient_data])
        else:
            patient_df = patient_data

        # Ensure all required features are present
        missing_features = set(self.feature_names) - set(patient_df.columns)
        if missing_features:
            raise ValueError(f"Missing features: {missing_features}")

        # Reorder columns to match training data
        patient_df = patient_df[self.feature_names]

        # Scale the features
        patient_scaled = self.scaler.transform(patient_df)

        # Make prediction
        prediction = self.model.predict(patient_scaled)
        probability = self.model.predict_proba(patient_scaled)

        return {
            'diagnosis': int(prediction[0]),
            'diagnosis_label': 'Alzheimer\'s Disease' if prediction[0] == 1 else 'No Alzheimer\'s Disease',
            'probability_no_alzheimers': float(probability[0][0]),
            'probability_alzheimers': float(probability[0][1])
        }

    def save_model(self, model_path='alzheimers_model.joblib', scaler_path='alzheimers_scaler.joblib'):
        """Save the trained model and scaler"""
        if self.model is not None and self.scaler is not None:
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            joblib.dump(self.feature_names, 'feature_names.joblib')
            print(f"Model saved to {model_path}")
            print(f"Scaler saved to {scaler_path}")

    def load_model(self, model_path='alzheimers_model.joblib', scaler_path='alzheimers_scaler.joblib', feature_names_path='feature_names.joblib'):
        """Load a pre-trained model and scaler"""
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.feature_names = joblib.load(feature_names_path)
        print("Model and scaler loaded successfully")

def main():
    # Initialize predictor
    predictor = AlzheimersPredictor()

    # Load and preprocess data
    X, y = predictor.load_and_preprocess_data('alzheimers_disease_data.csv')

    # Train model
    accuracy, feature_importance = predictor.train_model(X, y)

    # Save the model
    predictor.save_model()

    # Example prediction for a new patient
    print("\n" + "="*50)
    print("EXAMPLE PREDICTION FOR NEW PATIENT")
    print("="*50)

    # Create sample patient data based on the features
    sample_patient = {
        'Age': 75,
        'Gender': 1,  # 1 for female, 0 for male
        'Ethnicity': 0,
        'EducationLevel': 2,
        'BMI': 24.5,
        'Smoking': 0,
        'AlcoholConsumption': 5.0,
        'PhysicalActivity': 3.0,
        'DietQuality': 6.0,
        'SleepQuality': 7.0,
        'FamilyHistoryAlzheimers': 1,
        'CardiovascularDisease': 0,
        'Diabetes': 0,
        'Depression': 1,
        'HeadInjury': 0,
        'Hypertension': 1,
        'SystolicBP': 140,
        'DiastolicBP': 85,
        'CholesterolTotal': 220,
        'CholesterolLDL': 130,
        'CholesterolHDL': 45,
        'CholesterolTriglycerides': 180,
        'MMSE': 22,
        'FunctionalAssessment': 6.5,
        'MemoryComplaints': 1,
        'BehavioralProblems': 0,
        'ADL': 3.5,
        'Confusion': 1,
        'Disorientation': 0,
        'PersonalityChanges': 1,
        'DifficultyCompletingTasks': 1,
        'Forgetfulness': 1
    }

    try:
        result = predictor.predict_diagnosis(sample_patient)
        print(f"Diagnosis: {result['diagnosis_label']}")
        print(f"Probability of No Alzheimer's: {result['probability_no_alzheimers']:.4f}")
        print(f"Probability of Alzheimer's: {result['probability_alzheimers']:.4f}")
    except Exception as e:
        print(f"Error making prediction: {e}")

if __name__ == "__main__":
    main()