# Blockchain Integration - Deployment Guide

## Overview
This guide explains how to deploy and integrate the Ethereum blockchain module for the Academic Records Validator system.

## Prerequisites
- Node.js (v16 or higher)
- Python 3.8+
- npm

## Step-by-Step Deployment

### 1. Install Blockchain Dependencies

Navigate to the blockchain directory:
```bash
cd blockchain
npm install
```

This will install:
- Hardhat (Ethereum development environment)
- Hardhat Toolbox (testing and deployment tools)

### 2. Compile Smart Contract

```bash
npx hardhat compile
```

Expected output:
```
Compiled 1 Solidity file successfully
```

### 3. Start Local Ethereum Node

Open a **NEW TERMINAL** and run:
```bash
cd blockchain
npx hardhat node
```

**IMPORTANT**: Keep this terminal running! This is your local blockchain.

You should see:
```
Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/

Accounts
========
Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
...
```

### 4. Deploy Smart Contract

Open a **SECOND TERMINAL** and run:
```bash
cd blockchain
npx hardhat run scripts/deploy.js --network localhost
```

Expected output:
```
======================================================================
DEPLOYING CERTIFICATE REGISTRY CONTRACT
======================================================================

Deploying contract...
✓ Contract deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
✓ Deployed by: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
✓ Deployment info saved to: deployment.json
✓ Contract ABI saved to: contract_abi.json

======================================================================
DEPLOYMENT SUCCESSFUL
======================================================================
```

**COPY THE CONTRACT ADDRESS** - you'll need it for the next step!

### 5. Configure Backend

Create or update `backend/.env`:
```
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
BLOCKCHAIN_PROVIDER_URL=http://127.0.0.1:8545
```

Replace the contract address with the one from step 4.

### 6. Install Python Dependencies

```bash
cd ..
pip install web3
```

### 7. Test Blockchain Service

```bash
cd blockchain
python blockchain_service.py
```

Expected output:
```
======================================================================
TESTING BLOCKCHAIN SERVICE
======================================================================

✓ Blockchain service initialized
  Contract: 0x5FbDB2315678afecb367f032d93F642f64180aa3
  Network: http://127.0.0.1:8545

Blockchain available: True

[TEST] Registering certificate...
Registration result: {'success': True, 'tx_hash': '0x...', ...}

[TEST] Retrieving certificate...
Retrieval result: {'success': True, 'hash': 'abc123def456hash', ...}

[TEST] Verifying certificate...
Verification: True - Certificate hash matches blockchain record
======================================================================
```

### 8. Run the Application

Now you can start the backend server:
```bash
cd backend
python app.py
```

The backend will automatically connect to the blockchain!

## Verification

To verify everything is working:

1. **Check Hardhat node is running**: Terminal 1 should show transaction logs
2. **Check contract is deployed**: `blockchain/deployment.json` should exist
3. **Check ABI is saved**: `blockchain/contract_abi.json` should exist
4. **Check backend connection**: Backend logs should show "Blockchain service initialized"

## Troubleshooting

### "Blockchain service not available"
- Ensure Hardhat node is running (`npx hardhat node`)
- Check `CONTRACT_ADDRESS` in `backend/.env`
- Verify `contract_abi.json` exists in `blockchain/` folder

### "Connection refused"
- Hardhat node must be running on port 8545
- Check firewall settings

### "Certificate already registered"
- Each certificate ID can only be registered once
- This is expected behavior for duplicate registrations

## Important Notes

⚠️ **Local Development Only**
- This setup uses a local Hardhat node
- Data is NOT persistent (resets when node restarts)
- For production, deploy to a real Ethereum network

⚠️ **Privacy**
- Only certificate ID and hash are stored on-chain
- NO personal data (names, grades, etc.) is stored
- This ensures GDPR compliance

⚠️ **Security**
- Private keys are managed by Hardhat node
- For production, use proper key management
- Never commit private keys to version control

## Next Steps

Once deployed, the system will:
1. **University uploads certificate** → Hash stored on blockchain
2. **Verifier checks certificate** → Hash compared with blockchain
3. **Verification result** → Includes blockchain match status

The blockchain integration is now complete and ready to use!
