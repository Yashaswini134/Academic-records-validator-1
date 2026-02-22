# Blockchain Module - Academic Records Validator

## Overview
Ethereum blockchain integration for immutable certificate verification.

## Architecture

```
blockchain/
├── contracts/
│   └── CertificateRegistry.sol    # Smart contract
├── scripts/
│   └── deploy.js                  # Deployment script
├── blockchain_service.py          # Python backend integration
├── integration_example.py         # Integration examples
├── hardhat.config.js              # Hardhat configuration
├── package.json                   # Node dependencies
└── DEPLOYMENT_GUIDE.md            # Detailed setup guide
```

## Features

✅ **Privacy-Preserving**: Only stores certificate ID and SHA-256 hash  
✅ **Immutable**: Once registered, cannot be modified  
✅ **Decentralized**: Runs on local Ethereum node  
✅ **Graceful Degradation**: System works even if blockchain is unavailable  
✅ **Production-Ready**: Complete error handling and logging  

## Quick Start

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Compile contract**:
   ```bash
   npx hardhat compile
   ```

3. **Start local node** (Terminal 1):
   ```bash
   npx hardhat node
   ```

4. **Deploy contract** (Terminal 2):
   ```bash
   npx hardhat run scripts/deploy.js --network localhost
   ```

5. **Configure backend**:
   ```bash
   # Create backend/.env
   CONTRACT_ADDRESS=<address_from_deployment>
   BLOCKCHAIN_PROVIDER_URL=http://127.0.0.1:8545
   ```

6. **Test**:
   ```bash
   python blockchain_service.py
   ```

## Smart Contract Functions

### `registerCertificate(certificateId, hash)`
- Registers a new certificate on blockchain
- Reverts if certificate already exists
- Emits `CertificateRegistered` event

### `getCertificateHash(certificateId)`
- Returns stored hash for a certificate
- Reverts if certificate not found

### `getCertificateDetails(certificateId)`
- Returns hash, timestamp, and issuer address
- Reverts if certificate not found

### `certificateExists(certificateId)`
- Returns true if certificate is registered

## Backend Integration

### Register Certificate (University Upload)
```python
from blockchain.blockchain_service import get_blockchain_service

blockchain = get_blockchain_service()
result = blockchain.register_certificate(
    certificate_id="CERT-2024-001",
    certificate_hash="abc123..."
)
```

### Verify Certificate (Verifier Check)
```python
result = blockchain.get_certificate_hash("CERT-2024-001")
if result['success']:
    stored_hash = result['hash']
    # Compare with regenerated hash
```

## Security Considerations

⚠️ **What is stored on-chain**:
- Certificate ID
- SHA-256 hash
- Timestamp
- Issuer address

⚠️ **What is NOT stored**:
- Student name
- Grades/CGPA
- University name
- Certificate image
- Any personal data

This ensures GDPR compliance and privacy protection.

## Development vs Production

### Development (Current Setup)
- Local Hardhat node
- Data resets on restart
- Free transactions
- No gas costs

### Production (Future)
- Deploy to Ethereum mainnet or L2 (Polygon, Arbitrum)
- Persistent data
- Real gas costs
- Requires wallet management

## Troubleshooting

See `DEPLOYMENT_GUIDE.md` for detailed troubleshooting steps.

## Files Generated After Deployment

- `deployment.json` - Contract address and deployment info
- `contract_abi.json` - Contract ABI for backend
- `artifacts/` - Compiled contract artifacts
- `cache/` - Hardhat cache

## License

MIT
