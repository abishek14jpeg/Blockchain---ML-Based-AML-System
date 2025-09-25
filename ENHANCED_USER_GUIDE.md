# Enhanced Blockchain AML System - User Guide

## 🛡️ Enhanced Features Overview

The system now provides comprehensive blockchain transaction analysis with the following new capabilities:

### ✨ New Features Added:

1. **Comprehensive Transaction Details**
   - Sender and receiver address analysis
   - Gas fees displayed in both ETH and USD
   - Token type support (ETH and USDC)
   - Real blockchain network information

2. **Enhanced ML Analysis**
   - Multi-model ensemble prediction
   - Risk factor identification
   - Confidence scoring with detailed breakdown
   - Address risk assessment

3. **Advanced Gas Fee Analysis**
   - Accurate gas fee calculation in Wei, ETH, and USD
   - Support for different gas limits (21000 for ETH, 65000+ for USDC)
   - Gas price monitoring and alerts

4. **Smart Contract Detection**
   - Identifies contract interactions
   - Additional risk scoring for contract transactions
   - Enhanced monitoring for DeFi protocols

## 🚀 How to Use the Enhanced Dashboard

### 1. Access the System
- URL: http://127.0.0.1:5000
- Login with: `demo` / `demo123` (or other provided credentials)

### 2. Quick Start with Sample Data
The dashboard includes 6 sample transaction types:

**✅ Normal Transactions:**
- **Normal ETH Transaction**: Standard peer-to-peer ETH transfer
- **Normal USDC Transaction**: Regular USDC token transfer

**⚠️ Suspicious Patterns:**
- **Suspicious ETH (High Amount)**: Large ETH transfer with unusual timing
- **Suspicious USDC (High Frequency)**: High-frequency USDC transactions
- **Likely Illicit Pattern**: Multiple red flags indicating illicit activity
- **Mixer-like Pattern**: Pattern similar to cryptocurrency mixing services

### 3. Manual Transaction Analysis
Fill in the form with:

**Required Fields:**
- **Sender Address**: Ethereum address sending the transaction
- **Receiver Address**: Ethereum address receiving the transaction
- **Amount**: Transaction amount in specified token
- **Token Type**: Choose between ETH or USDC

**Optional Fields:**
- **Gas Limit**: Transaction gas limit (default: 21000 for ETH, adjust for USDC)
- **Gas Price (Gwei)**: Gas price for the transaction
- **24h Transaction Frequency**: Number of transactions in past 24 hours
- **Unique Counterparties**: Number of unique addresses interacted with
- **Hour of Day**: When the transaction occurred (0-23)
- **Account Age**: How old the sending account is (in days)
- **Account Balance**: Current balance of the sending account

### 4. Understanding the Results

**Transaction Details Panel:**
- Shows amount, gas fees in ETH and USD
- Displays sender/receiver addresses
- Network and block information

**Risk Assessment Panel:**
- Overall risk score and level (LOW/MEDIUM/HIGH)
- ML-based risk score
- Address-based risk factors
- Gas fee risk indicators

**Address Analysis Panel:**
- Determines if addresses are smart contracts
- Individual risk scores for sender and receiver
- Relationship analysis between addresses

**ML Prediction Panel:**
- Final prediction (NORMAL/ILLICIT)
- Confidence percentage
- Individual model results (Random Forest, Isolation Forest)
- Specific risk factors identified

**Recommendations Panel:**
- Actionable recommendations based on analysis
- Compliance guidance
- Monitoring suggestions

## 🧪 Sample Test Scenarios

### Example 1: Normal ETH Transaction
```
Sender: 0x1234567890123456789012345678901234567890
Receiver: 0x0987654321098765432109876543210987654321
Amount: 500 ETH
Gas Price: 20 Gwei
Result: Should show as NORMAL with low risk
```

### Example 2: Suspicious Large Transaction
```
Sender: 0x000000000000000000000000000000000000000a
Receiver: 0xffffffffffffffffffffffffffffffffffffffff  
Amount: 25000 ETH
Gas Price: 150 Gwei
Hour: 3 AM
Result: Should flag as HIGH RISK with multiple risk factors
```

### Example 3: USDC Token Transfer
```
Sender: 0xabcdef1234567890abcdef1234567890abcdef12
Receiver: 0x1234567890abcdef1234567890abcdef12345678
Amount: 1000 USDC
Gas Limit: 65000
Gas Price: 25 Gwei
Result: Shows USDC-specific analysis with contract interaction flags
```

## 🔧 Technical Details

**Gas Fee Calculation:**
- Gas Fee (Wei) = Gas Limit × Gas Price (in Wei)  
- Gas Fee (ETH) = Gas Fee (Wei) ÷ 10^18
- Gas Fee (USD) = Gas Fee (ETH) × ETH Price (~$2000)

**Risk Scoring:**
- ML Risk: Machine learning model probability
- Address Risk: Based on address patterns and history
- Gas Risk: Unusual gas price indicators
- Overall Risk: Weighted combination of all factors

**ML Models:**
- Random Forest: Trained on transaction patterns
- Isolation Forest: Anomaly detection for unusual behavior
- Ensemble: Combines both models for final prediction

## 🎯 Key Improvements Delivered

1. ✅ **Comprehensive blockchain transaction statistics**
2. ✅ **Gas fees displayed in ETH and USD**  
3. ✅ **Sender and receiver address analysis**
4. ✅ **Support for both ETH and USDC transactions**
5. ✅ **Enhanced ML-powered risk assessment**
6. ✅ **Real-time blockchain network integration**
7. ✅ **User-friendly sample data for quick testing**
8. ✅ **Detailed recommendations and compliance guidance**

The system is now fully functional and ready for comprehensive blockchain AML analysis!