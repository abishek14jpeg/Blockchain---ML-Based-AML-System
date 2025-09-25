#!/usr/bin/env python3
"""
ML Service API for Blockchain AML System
Provides /predict endpoint for real-time AML detection
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Blockchain AML Detection API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for models
models = {}
scaler = None
feature_names = []

def generate_synthetic_data(n_samples=10000):
    """Generate synthetic blockchain transaction data for AML detection"""
    logger.info(f"Generating {n_samples} synthetic transactions...")
    
    np.random.seed(42)
    
    # Normal transaction features
    normal_samples = int(n_samples * 0.85)  # 85% normal
    illicit_samples = n_samples - normal_samples  # 15% illicit
    
    # Enhanced features for blockchain transactions
    features = []
    labels = []
    
    # Generate normal transactions
    for _ in range(normal_samples):
        transaction = {
            'amount': np.random.lognormal(3, 1.5),  # Log-normal distribution for amounts
            'frequency_24h': np.random.poisson(3),  # Average 3 transactions per day
            'unique_counterparties': np.random.poisson(2),  # Average 2 unique counterparties
            'hour_of_day': np.random.normal(12, 4) % 24,  # Normal business hours bias
            'gas_price': np.random.gamma(2, 10),  # Gas price in Gwei
            'is_contract': np.random.choice([0, 1], p=[0.8, 0.2]),  # 20% contract interactions
            'account_age_days': np.random.exponential(365),  # Account age
            'balance': np.random.lognormal(4, 2),  # Account balance
            'token_type_numeric': np.random.choice([0, 1], p=[0.7, 0.3]),  # 70% ETH, 30% USDC
            'high_gas_fee': 0  # Will be calculated
        }
        
        # Calculate high gas fee flag
        transaction['high_gas_fee'] = 1 if transaction['gas_price'] > 50 else 0
        
        features.append(list(transaction.values()))
        labels.append(0)  # Normal
    
    # Generate illicit transactions with different patterns
    for _ in range(illicit_samples):
        transaction = {
            'amount': np.random.choice([
                np.random.lognormal(5, 2),  # Large amounts
                np.random.uniform(9999, 10001)  # Amounts just under reporting thresholds
            ]),
            'frequency_24h': np.random.choice([
                np.random.poisson(15),  # High frequency
                1  # Single large transaction
            ]),
            'unique_counterparties': np.random.choice([
                1,  # Single counterparty (possible tumbling)
                np.random.poisson(8)  # Many counterparties (possible structuring)
            ]),
            'hour_of_day': np.random.choice([
                np.random.uniform(0, 6),  # Late night/early morning
                np.random.uniform(22, 24),  # Late night
                np.random.normal(12, 2) % 24  # Some normal hours too
            ]),
            'gas_price': np.random.choice([
                np.random.gamma(5, 20),  # Very high gas price (urgency)
                np.random.gamma(1, 5)   # Very low gas price (patience)
            ]),
            'is_contract': np.random.choice([0, 1], p=[0.3, 0.7]),  # 70% contract interactions (mixers, etc.)
            'account_age_days': np.random.choice([
                np.random.exponential(30),  # New accounts
                np.random.exponential(1000)  # Old accounts
            ]),
            'balance': np.random.choice([
                np.random.lognormal(2, 1),  # Small balances
                np.random.lognormal(6, 2)   # Large balances
            ]),
            'token_type_numeric': np.random.choice([0, 1], p=[0.4, 0.6]),  # 60% USDC for illicit (privacy coins preference)
            'high_gas_fee': 0  # Will be calculated
        }
        
        # Calculate high gas fee flag
        transaction['high_gas_fee'] = 1 if transaction['gas_price'] > 50 else 0
        
        features.append(list(transaction.values()))
        labels.append(1)  # Illicit
    
    # Convert to DataFrame
    feature_names = ['amount', 'frequency_24h', 'unique_counterparties', 'hour_of_day', 
                    'gas_price', 'is_contract', 'account_age_days', 'balance',
                    'token_type_numeric', 'high_gas_fee']
    
    df = pd.DataFrame(features, columns=feature_names)
    df['label'] = labels
    
    # Add some noise to make it more realistic
    df['amount'] += np.random.normal(0, df['amount'] * 0.01)
    df['balance'] += np.random.normal(0, df['balance'] * 0.01)
    
    logger.info(f"Generated dataset: {len(df)} samples, {sum(labels)} illicit ({sum(labels)/len(labels)*100:.1f}%)")
    return df, feature_names

def train_models():
    """Train ML models for AML detection"""
    global models, scaler, feature_names
    
    logger.info("Starting model training...")
    
    # Generate synthetic data
    df, feature_names = generate_synthetic_data(10000)
    
    # Prepare features and target
    X = df[feature_names]
    y = df['label']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest
    logger.info("Training Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    rf_model.fit(X_train_scaled, y_train)
    
    # Train Isolation Forest for anomaly detection
    logger.info("Training Isolation Forest...")
    iso_model = IsolationForest(
        contamination=0.15,
        random_state=42
    )
    iso_model.fit(X_train_scaled[y_train == 0])  # Train only on normal data
    
    # Evaluate models
    rf_pred = rf_model.predict(X_test_scaled)
    iso_pred = iso_model.predict(X_test_scaled)
    iso_pred = np.where(iso_pred == -1, 1, 0)  # Convert to binary
    
    rf_accuracy = accuracy_score(y_test, rf_pred)
    iso_accuracy = accuracy_score(y_test, iso_pred)
    
    logger.info(f"Random Forest Accuracy: {rf_accuracy:.3f}")
    logger.info(f"Isolation Forest Accuracy: {iso_accuracy:.3f}")
    
    # Store models
    models['random_forest'] = rf_model
    models['isolation_forest'] = iso_model
    
    # Save training results
    training_results = {
        'timestamp': datetime.now().isoformat(),
        'rf_accuracy': rf_accuracy,
        'iso_accuracy': iso_accuracy,
        'feature_names': feature_names,
        'training_samples': len(X_train),
        'test_samples': len(X_test)
    }
    
    with open('/home/abishek14/blockchain-aml-system/ml/training_results.json', 'w') as f:
        json.dump(training_results, f, indent=2)
    
    # Save models
    os.makedirs('/home/abishek14/blockchain-aml-system/ml/models', exist_ok=True)
    with open('/home/abishek14/blockchain-aml-system/ml/models/random_forest.pkl', 'wb') as f:
        pickle.dump(rf_model, f)
    with open('/home/abishek14/blockchain-aml-system/ml/models/isolation_forest.pkl', 'wb') as f:
        pickle.dump(iso_model, f)
    with open('/home/abishek14/blockchain-aml-system/ml/models/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    logger.info("Model training completed!")
    return training_results

@app.on_event("startup")
async def startup_event():
    """Train models on startup"""
    try:
        train_models()
        logger.info("ML Service started successfully!")
    except Exception as e:
        logger.error(f"Failed to train models: {e}")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Blockchain AML Detection API",
        "status": "running",
        "models_loaded": len(models),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "models": list(models.keys()),
        "feature_count": len(feature_names),
        "scaler_fitted": scaler is not None
    }

@app.post("/predict")
async def predict(transaction_data: dict):
    """Predict if a transaction is illicit"""
    try:
        if not models:
            raise HTTPException(status_code=503, detail="Models not loaded")
        
        # Extract features matching the training data format
        features = [
            transaction_data.get('amount', 100.0),
            transaction_data.get('frequency_24h', 5),
            transaction_data.get('unique_counterparties', 3),
            transaction_data.get('hour_of_day', 12),
            transaction_data.get('gas_price', 20.0),
            transaction_data.get('is_contract', 0),
            transaction_data.get('account_age_days', 365),
            transaction_data.get('balance', 1000.0),
            transaction_data.get('token_type_numeric', 0),
            transaction_data.get('high_gas_fee', 0)
        ]
        
        # Ensure we have the right number of features
        if len(features) != len(feature_names):
            raise HTTPException(
                status_code=400, 
                detail=f"Expected {len(feature_names)} features, got {len(features)}"
            )
        
        # Scale features
        features_scaled = scaler.transform([features])
        
        # Get predictions
        rf_pred = models['random_forest'].predict(features_scaled)[0]
        rf_proba = models['random_forest'].predict_proba(features_scaled)[0]
        
        iso_pred = models['isolation_forest'].predict(features_scaled)[0]
        iso_pred_binary = 1 if iso_pred == -1 else 0
        
        # Ensemble prediction (majority vote)
        ensemble_pred = 1 if (rf_pred + iso_pred_binary) >= 1 else 0
        
        # Risk factors analysis
        risk_factors = []
        if transaction_data.get('amount', 0) > 10000:
            risk_factors.append("High transaction amount")
        if transaction_data.get('hour_of_day', 12) < 6 or transaction_data.get('hour_of_day', 12) > 22:
            risk_factors.append("Unusual transaction time")
        if transaction_data.get('frequency_24h', 0) > 10:
            risk_factors.append("High transaction frequency")
        if transaction_data.get('gas_price', 0) > 50:
            risk_factors.append("Unusually high gas price")
        if transaction_data.get('is_contract', 0):
            risk_factors.append("Smart contract interaction")
        
        result = {
            "prediction": int(ensemble_pred),
            "confidence": float(max(rf_proba)),
            "risk_score": float(rf_proba[1]),  # Probability of being illicit
            "risk_factors": risk_factors,
            "models": {
                "random_forest": {
                    "prediction": int(rf_pred),
                    "confidence": float(max(rf_proba)),
                    "probabilities": {
                        "normal": float(rf_proba[0]),
                        "illicit": float(rf_proba[1])
                    }
                },
                "isolation_forest": {
                    "prediction": int(iso_pred_binary),
                    "anomaly_score": float(abs(iso_pred))
                }
            },
            "timestamp": datetime.now().isoformat(),
            "source": "ml_service"
        }
        
        logger.info(f"Prediction made: {result['prediction']} (confidence: {result['confidence']:.3f})")
        return result
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/models/stats")
async def model_stats():
    """Get model statistics"""
    try:
        with open('/home/abishek14/blockchain-aml-system/ml/training_results.json', 'r') as f:
            results = json.load(f)
        return results
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Training results not found")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)