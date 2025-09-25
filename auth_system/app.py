#!/usr/bin/env python3
"""
Blockchain AML Dashboard with Authentication
A secure Flask application with login/logout functionality and SQLite database
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import bcrypt
import os
import secrets
from datetime import datetime, timedelta
import requests
import json

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Secure secret key
CORS(app)

# Database setup
DATABASE = '/home/abishek14/blockchain-aml-system/auth_system/users.db'

def init_db():
    """Initialize SQLite database with users table"""
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create default users
    default_users = [
        ('admin', 'admin123', 'admin@blockchain-aml.com', 'admin'),
        ('user', 'password', 'user@blockchain-aml.com', 'user'),
        ('demo', 'demo123', 'demo@blockchain-aml.com', 'user'),
        ('aml_analyst', 'analyst2024', 'analyst@blockchain-aml.com', 'analyst')
    ]
    
    for username, password, email, role in default_users:
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if not cursor.fetchone():
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, role)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, email, role))
    
    conn.commit()
    conn.close()
    print("Database initialized with default users:")
    print("- admin / admin123 (Admin)")
    print("- user / password (User)")  
    print("- demo / demo123 (User)")
    print("- aml_analyst / analyst2024 (Analyst)")

def verify_password(password, password_hash):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash)

def get_user(username):
    """Get user from database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password_hash, email, role FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_last_login(user_id):
    """Update user's last login timestamp"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def is_authenticated():
    """Check if user is authenticated"""
    return 'user_id' in session and 'username' in session

@app.route('/')
def index():
    """Redirect to dashboard if authenticated, otherwise to login"""
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user(username)
        if user and verify_password(password, user[2]):  # user[2] is password_hash
            # Login successful
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]
            session['login_time'] = datetime.now().isoformat()
            
            update_last_login(user[0])
            
            # Redirect to dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard - requires authentication"""
    if not is_authenticated():
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', 
                         username=session['username'], 
                         role=session['role'])

@app.route('/api/health')
def api_health():
    """API health check - requires authentication"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Check ML service
        ml_response = requests.get('http://127.0.0.1:8000/health', timeout=5)
        ml_status = ml_response.json() if ml_response.status_code == 200 else {'status': 'offline'}
        
        # Check blockchain
        blockchain_response = requests.post('http://127.0.0.1:8545', 
                                          json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                                          timeout=5)
        blockchain_status = 'online' if blockchain_response.status_code == 200 else 'offline'
        
        return jsonify({
            'ml_service': ml_status,
            'blockchain': blockchain_status,
            'user': session['username'],
            'role': session['role'],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """ML prediction API - requires authentication"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Forward request to ML service
        ml_response = requests.post('http://127.0.0.1:8000/predict', 
                                   json=request.json, 
                                   timeout=10)
        return jsonify(ml_response.json()), ml_response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('/home/abishek14/blockchain-aml-system/auth_system/static', filename)

# Initialize database on startup
init_db()

if __name__ == '__main__':
    print("🔐 Starting Blockchain AML Authentication Server...")
    print("🌐 Dashboard will be available at: http://127.0.0.1:5000")
    print("👤 Default login credentials:")
    print("   • admin / admin123")
    print("   • user / password") 
    print("   • demo / demo123")
    print("   • aml_analyst / analyst2024")
    app.run(host='127.0.0.1', port=5000, debug=True)