#!/usr/bin/env python3
"""
Test script for the enhanced blockchain AML system
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def login():
    """Login and get session cookie"""
    session = requests.Session()
    
    # Login
    login_data = {
        'username': 'demo',
        'password': 'demo123'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Successfully logged in")
        return session
    else:
        print("❌ Login failed")
        return None

def test_prediction(session, test_case_name, data):
    """Test a prediction with given data"""
    print(f"\n🧪 Testing: {test_case_name}")
    print(f"📤 Request: {json.dumps(data, indent=2)}")
    
    response = session.post(f"{BASE_URL}/api/predict", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Prediction successful!")
        
        # Display key results
        td = result['transaction_details']
        ra = result['risk_assessment']
        ml = result['ml_prediction']
        
        print(f"💰 Transaction: {td['amount']} {td['token_type']}")
        print(f"📤 From: {td['sender_address'][:10]}...")
        print(f"📥 To: {td['receiver_address'][:10]}...")
        print(f"⛽ Gas Fee: {td['gas_fee_eth']} ETH (${td['gas_fee_usd']})")
        print(f"🎯 ML Prediction: {'🚨 ILLICIT' if ml['prediction'] == 1 else '✅ NORMAL'}")
        print(f"📊 Risk Level: {ra['risk_level']} ({ra['overall_risk_score']*100:.1f}%)")
        print(f"🔍 Confidence: {ml['confidence']*100:.1f}%")
        
        if ml.get('risk_factors'):
            print("⚠️  Risk Factors:")
            for factor in ml['risk_factors']:
                print(f"   • {factor}")
        
        print("💡 Recommendations:")
        for rec in result['recommendations'][:3]:  # Show first 3 recommendations
            print(f"   • {rec}")
            
    else:
        print(f"❌ Prediction failed: {response.status_code}")
        print(response.text)

def main():
    print("🛡️  Enhanced Blockchain AML System Test")
    print("=" * 50)
    
    # Login
    session = login()
    if not session:
        sys.exit(1)
    
    # Test cases
    test_cases = [
        {
            "name": "Normal ETH Transaction",
            "data": {
                "sender_address": "0x1234567890123456789012345678901234567890",
                "receiver_address": "0x0987654321098765432109876543210987654321",
                "amount": 500,
                "token_type": "ETH",
                "gas_limit": 21000,
                "gas_price_gwei": 20,
                "frequency_24h": 3,
                "unique_counterparties": 2,
                "hour_of_day": 14,
                "account_age_days": 365,
                "balance": 5000
            }
        },
        {
            "name": "Normal USDC Transaction",
            "data": {
                "sender_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                "receiver_address": "0x1234567890abcdef1234567890abcdef12345678",
                "amount": 1000,
                "token_type": "USDC",
                "gas_limit": 65000,
                "gas_price_gwei": 25,
                "frequency_24h": 5,
                "unique_counterparties": 3,
                "hour_of_day": 10,
                "account_age_days": 200,
                "balance": 10000
            }
        },
        {
            "name": "Suspicious High-Value ETH",
            "data": {
                "sender_address": "0x000000000000000000000000000000000000000a",
                "receiver_address": "0xffffffffffffffffffffffffffffffffffffffff",
                "amount": 25000,
                "token_type": "ETH",
                "gas_limit": 21000,
                "gas_price_gwei": 150,
                "frequency_24h": 1,
                "unique_counterparties": 1,
                "hour_of_day": 3,
                "account_age_days": 10,
                "balance": 30000
            }
        },
        {
            "name": "High-Frequency USDC Pattern",
            "data": {
                "sender_address": "0x1111111111111111111111111111111111111111",
                "receiver_address": "0x2222222222222222222222222222222222222222",
                "amount": 9999,
                "token_type": "USDC",
                "gas_limit": 65000,
                "gas_price_gwei": 200,
                "frequency_24h": 15,
                "unique_counterparties": 8,
                "hour_of_day": 2,
                "account_age_days": 5,
                "balance": 50000
            }
        },
        {
            "name": "Likely Illicit Pattern",
            "data": {
                "sender_address": "0x000000000000000000000000000000000000000b",
                "receiver_address": "0x1234567890123456789012345678901234567cde",
                "amount": 50000,
                "token_type": "USDC",
                "gas_limit": 150000,
                "gas_price_gwei": 300,
                "frequency_24h": 25,
                "unique_counterparties": 1,
                "hour_of_day": 4,
                "account_age_days": 1,
                "balance": 75000
            }
        }
    ]
    
    # Run test cases
    for test_case in test_cases:
        test_prediction(session, test_case["name"], test_case["data"])
    
    print("\n🎉 All tests completed!")
    print("\n🌐 You can now test the web interface at: http://127.0.0.1:5000")
    print("📝 Login credentials: demo / demo123")

if __name__ == "__main__":
    main()