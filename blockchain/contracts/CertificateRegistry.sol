// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title CertificateRegistry
 * @dev Smart contract for storing and verifying academic certificate hashes
 * 
 * Privacy-Preserving Design:
 * - Only stores certificate ID and SHA-256 hash
 * - Does NOT store personal data (name, grades, etc.)
 * - Immutable once registered
 */
contract CertificateRegistry {
    
    // Certificate structure
    struct Certificate {
        string certificateId;
        string certificateHash;
        uint256 timestamp;
        address issuer;
        bool exists;
    }
    
    // Mapping: certificateId => Certificate
    mapping(string => Certificate) private certificates;
    
    // Event emitted when a certificate is registered
    event CertificateRegistered(
        string indexed certificateId,
        string certificateHash,
        address indexed issuer,
        uint256 timestamp
    );
    
    /**
     * @dev Register a new certificate on the blockchain
     * @param certificateId Unique identifier for the certificate
     * @param certificateHash SHA-256 hash of the certificate file
     */
    function registerCertificate(
        string memory certificateId,
        string memory certificateHash
    ) public {
        // Validate inputs
        require(bytes(certificateId).length > 0, "Certificate ID cannot be empty");
        require(bytes(certificateHash).length > 0, "Certificate hash cannot be empty");
        
        // Check if certificate already exists
        require(
            !certificates[certificateId].exists,
            "Certificate already registered"
        );
        
        // Store certificate data
        certificates[certificateId] = Certificate({
            certificateId: certificateId,
            certificateHash: certificateHash,
            timestamp: block.timestamp,
            issuer: msg.sender,
            exists: true
        });
        
        // Emit event
        emit CertificateRegistered(
            certificateId,
            certificateHash,
            msg.sender,
            block.timestamp
        );
    }
    
    /**
     * @dev Get the stored hash for a certificate
     * @param certificateId The certificate ID to look up
     * @return certificateHash The stored SHA-256 hash
     */
    function getCertificateHash(string memory certificateId)
        public
        view
        returns (string memory)
    {
        require(
            certificates[certificateId].exists,
            "Certificate not found"
        );
        
        return certificates[certificateId].certificateHash;
    }
    
    /**
     * @dev Get complete certificate details
     * @param certificateId The certificate ID to look up
     * @return certificateHash The stored hash
     * @return timestamp When the certificate was registered
     * @return issuer Address that registered the certificate
     */
    function getCertificateDetails(string memory certificateId)
        public
        view
        returns (
            string memory certificateHash,
            uint256 timestamp,
            address issuer
        )
    {
        require(
            certificates[certificateId].exists,
            "Certificate not found"
        );
        
        Certificate memory cert = certificates[certificateId];
        return (cert.certificateHash, cert.timestamp, cert.issuer);
    }
    
    /**
     * @dev Check if a certificate exists
     * @param certificateId The certificate ID to check
     * @return exists True if certificate is registered
     */
    function certificateExists(string memory certificateId)
        public
        view
        returns (bool)
    {
        return certificates[certificateId].exists;
    }
}
