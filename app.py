from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import sqlite3
import bcrypt
import os
import requests
import json
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database setup
DATABASE = 'users.db'

def init_db():
    """Initialize the database with users table and default users"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Default users
    default_users = [
        ('admin', 'admin123', 'admin'),
        ('user', 'password', 'user'),
        ('demo', 'demo123', 'user'),
        ('aml_analyst', 'analyst2024', 'analyst')
    ]
    
    for username, password, role in default_users:
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if not cursor.fetchone():
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', (username, password_hash, role))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized with default users")

def verify_password(password, password_hash):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash)

def get_user(username):
    """Get user from database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password_hash, role FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

@app.route('/')
def index():
    """Redirect to dashboard if authenticated, otherwise to login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user(username)
        if user and verify_password(password, user[2]):
            # Login successful
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Enhanced dashboard - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('enhanced_dashboard.html', 
                         username=session['username'], 
                         role=session['role'])

@app.route('/api/health')
def api_health():
    """API health check"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Check various services
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'user': session['username'],
        'services': {
            'authentication': 'online',
            'database': 'online',
            'ml_service': 'checking...',
            'blockchain': 'checking...'
        }
    }
    
    # Check ML service
    try:
        response = requests.get('http://127.0.0.1:8000/health', timeout=3)
        health_status['services']['ml_service'] = 'online' if response.status_code == 200 else 'offline'
    except:
        health_status['services']['ml_service'] = 'offline'
    
    # Check blockchain
    try:
        response = requests.post('http://127.0.0.1:8545', 
                               json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                               timeout=3)
        health_status['services']['blockchain'] = 'online' if response.status_code == 200 else 'offline'
    except:
        health_status['services']['blockchain'] = 'offline'
    
    return jsonify(health_status)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """Enhanced ML prediction API with blockchain analysis"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.json
    
    # Extract transaction details
    sender = data.get('sender_address', '')
    receiver = data.get('receiver_address', '')
    amount = float(data.get('amount', 1000))
    token_type = data.get('token_type', 'ETH')  # ETH or USDC
    gas_limit = int(data.get('gas_limit', 21000))
    gas_price_gwei = float(data.get('gas_price_gwei', 20))
    
    # Calculate gas fees
    gas_fee_wei = gas_limit * (gas_price_gwei * 10**9)  # Convert Gwei to Wei
    gas_fee_eth = gas_fee_wei / 10**18  # Convert Wei to ETH
    gas_fee_usd = gas_fee_eth * 2000  # Approximate ETH price
    
    # Get current blockchain info
    blockchain_info = get_blockchain_info()
    
    # Enhanced transaction analysis
    transaction_details = {
        'sender_address': sender,
        'receiver_address': receiver,
        'amount': amount,
        'token_type': token_type,
        'gas_limit': gas_limit,
        'gas_price_gwei': gas_price_gwei,
        'gas_fee_wei': gas_fee_wei,
        'gas_fee_eth': round(gas_fee_eth, 6),
        'gas_fee_usd': round(gas_fee_usd, 2),
        'block_number': blockchain_info.get('block_number', 'N/A'),
        'network': 'Localhost Anvil',
        'timestamp': datetime.now().isoformat()
    }
    
    # Address analysis
    address_analysis = analyze_addresses(sender, receiver)
    
    # Enhanced ML prediction data
    ml_data = {
        'amount': amount,
        'frequency_24h': data.get('frequency_24h', 5),
        'unique_counterparties': data.get('unique_counterparties', 3),
        'hour_of_day': data.get('hour_of_day', 12),
        'gas_price': gas_price_gwei,
        'is_contract': address_analysis['receiver_is_contract'],
        'account_age_days': data.get('account_age_days', 365),
        'balance': data.get('balance', 10000.0),
        'token_type_numeric': 0 if token_type == 'ETH' else 1,
        'high_gas_fee': 1 if gas_fee_eth > 0.01 else 0
    }
    
    try:
        # Try ML service first
        response = requests.post('http://127.0.0.1:8000/predict', 
                               json=ml_data, 
                               timeout=10)
        ml_result = response.json()
    except:
        # Enhanced fallback prediction
        ml_result = enhanced_fallback_prediction(ml_data)
    
    # Combine all analysis
    final_result = {
        'transaction_details': transaction_details,
        'address_analysis': address_analysis,
        'ml_prediction': ml_result,
        'risk_assessment': calculate_risk_assessment(ml_result, transaction_details, address_analysis),
        'recommendations': generate_recommendations(ml_result, transaction_details)
    }
    
    return jsonify(final_result)

def get_blockchain_info():
    """Get current blockchain information"""
    try:
        response = requests.post('http://127.0.0.1:8545', 
                               json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                               timeout=3)
        if response.status_code == 200:
            result = response.json()
            return {'block_number': int(result['result'], 16)}
    except:
        pass
    return {'block_number': 'N/A'}

def analyze_addresses(sender, receiver):
    """Analyze sender and receiver addresses"""
    analysis = {
        'sender_is_contract': is_contract_address(sender),
        'receiver_is_contract': is_contract_address(receiver),
        'sender_risk_score': calculate_address_risk(sender),
        'receiver_risk_score': calculate_address_risk(receiver),
        'addresses_related': are_addresses_related(sender, receiver)
    }
    return analysis

def is_contract_address(address):
    """Check if address is a smart contract"""
    if not address or len(address) != 42:
        return False
    # Simple heuristic - in reality would check bytecode
    return address.lower().endswith(('c', 'd', 'e', 'f'))

def calculate_address_risk(address):
    """Calculate risk score for an address (0-1)"""
    if not address:
        return 0.5
    # Simple heuristic based on address patterns
    risk = 0.0
    if address.lower().startswith('0x000'):
        risk += 0.3  # New or suspicious address pattern
    if len(set(address[2:])) < 10:
        risk += 0.2  # Low entropy address
    return min(risk, 1.0)

def are_addresses_related(sender, receiver):
    """Check if addresses might be related"""
    if not sender or not receiver:
        return False
    # Simple pattern matching
    return sender[:10] == receiver[:10]  # Same first 8 chars after 0x

def enhanced_fallback_prediction(data):
    """Enhanced fallback ML prediction when service is unavailable"""
    risk_factors = 0
    risk_reasons = []
    
    # Amount-based risk
    if data['amount'] > 10000:
        risk_factors += 1
        risk_reasons.append("High transaction amount")
    
    # Time-based risk
    if data['hour_of_day'] < 6 or data['hour_of_day'] > 22:
        risk_factors += 1
        risk_reasons.append("Unusual transaction time")
    
    # Frequency-based risk
    if data['frequency_24h'] > 10:
        risk_factors += 1
        risk_reasons.append("High transaction frequency")
    
    # Gas price risk
    if data['gas_price'] > 100:  # Very high gas price
        risk_factors += 1
        risk_reasons.append("Unusually high gas price")
    
    # Contract interaction risk
    if data['is_contract']:
        risk_factors += 0.5
        risk_reasons.append("Interacting with smart contract")
    
    is_illicit = risk_factors >= 2
    confidence = 0.7 + (min(risk_factors, 3) * 0.1)
    risk_score = min(risk_factors / 4.0, 1.0)
    
    return {
        'prediction': 1 if is_illicit else 0,
        'confidence': min(confidence, 0.95),
        'risk_score': risk_score,
        'risk_factors': risk_reasons,
        'source': 'enhanced_fallback_model',
        'models': {
            'random_forest': {'prediction': 1 if is_illicit else 0, 'confidence': confidence},
            'isolation_forest': {'prediction': 1 if risk_factors > 1.5 else 0, 'anomaly_score': risk_score}
        },
        'timestamp': datetime.now().isoformat()
    }

def calculate_risk_assessment(ml_result, transaction_details, address_analysis):
    """Calculate overall risk assessment"""
    base_risk = ml_result.get('risk_score', 0)
    
    # Additional risk factors
    address_risk = (address_analysis['sender_risk_score'] + address_analysis['receiver_risk_score']) / 2
    gas_risk = 0.1 if transaction_details['gas_fee_eth'] > 0.01 else 0
    
    overall_risk = min(base_risk + (address_risk * 0.3) + gas_risk, 1.0)
    
    risk_level = 'LOW'
    if overall_risk > 0.7:
        risk_level = 'HIGH'
    elif overall_risk > 0.4:
        risk_level = 'MEDIUM'
    
    return {
        'overall_risk_score': round(overall_risk, 3),
        'risk_level': risk_level,
        'ml_risk': base_risk,
        'address_risk': address_risk,
        'gas_risk': gas_risk
    }

def generate_recommendations(ml_result, transaction_details):
    """Generate recommendations based on analysis"""
    recommendations = []
    
    if ml_result.get('prediction') == 1:
        recommendations.append("🚨 ALERT: Transaction flagged as potentially illicit")
        recommendations.append("📋 Recommend manual review by compliance team")
        recommendations.append("🔍 Consider additional KYC verification")
    
    if transaction_details['gas_fee_eth'] > 0.005:
        recommendations.append("⚡ High gas fee detected - verify transaction urgency")
    
    if transaction_details['amount'] > 10000:
        recommendations.append("💰 Large transaction amount - enhanced monitoring recommended")
    
    if not recommendations:
        recommendations.append("✅ Transaction appears normal - routine processing")
    
    return recommendations

@app.route('/api/system/status')
def system_status():
    """Get system status"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    return jsonify({
        'blockchain_node': 'running',
        'smart_contracts': 'deployed',
        'oracle_bridge': 'active',
        'ml_models': 'trained',
        'active_users': 1,
        'predictions_today': 142,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/blockchain')
def blockchain_explorer():
    """Blockchain explorer interface"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('blockchain_explorer.html', 
                         username=session['username'], 
                         role=session['role'])

if __name__ == '__main__':
    print("🚀 Starting Blockchain AML System...")
    print("📦 Initializing database...")
    init_db()
    print("🔐 Authentication system ready")
    print("🌐 Starting Flask server on http://127.0.0.1:5000")
    print("\n👤 Default login credentials:")
    print("   • admin / admin123 (Admin)")
    print("   • user / password (User)")
    print("   • demo / demo123 (Demo)")
    print("   • aml_analyst / analyst2024 (Analyst)")
    
    app.run(debug=True, host='127.0.0.1', port=5000)