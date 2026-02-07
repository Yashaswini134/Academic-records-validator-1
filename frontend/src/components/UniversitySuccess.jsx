import React from 'react';

const UniversitySuccess = ({ confirmationData, onNewCertificate }) => {
    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        alert('Copied to clipboard!');
    };

    return (
        <div className="container">
            <div className="success-container">
                <div className="success-header">
                    <div className="success-icon">✅</div>
                    <h2>Certificate Registered Successfully!</h2>
                    <p>The certificate has been processed and hash generated</p>
                </div>

                <div className="success-details">
                    <div className="detail-card">
                        <h3>📋 Certificate Information</h3>
                        <div className="detail-row">
                            <span className="detail-label">Certificate ID:</span>
                            <span className="detail-value">
                                {confirmationData.certificate_id}
                            </span>
                        </div>
                        <div className="detail-row">
                            <span className="detail-label">Student Name:</span>
                            <span className="detail-value">
                                {confirmationData.student_name}
                            </span>
                        </div>
                        <div className="detail-row">
                            <span className="detail-label">University:</span>
                            <span className="detail-value">
                                {confirmationData.university}
                            </span>
                        </div>
                    </div>

                    <div className="detail-card">
                        <h3>🔐 Security Hash</h3>
                        <div className="hash-display">
                            <code className="hash-value">
                                {confirmationData.hash || 'Hash generation pending...'}
                            </code>
                            {confirmationData.hash && (
                                <button
                                    className="btn-copy"
                                    onClick={() => copyToClipboard(confirmationData.hash)}
                                    title="Copy hash"
                                >
                                    📋
                                </button>
                            )}
                        </div>
                        <p className="hash-info">
                            <strong>Algorithm:</strong> {confirmationData.hash_algorithm || 'SHA-256'}
                        </p>
                    </div>

                    <div className="detail-card">
                        <h3>⛓️ Blockchain Status</h3>
                        <div className="blockchain-status">
                            <span className="status-badge status-pending">
                                ⏳ Blockchain Registration Pending
                            </span>
                            <p className="status-message">
                                The certificate will be registered on the blockchain shortly.
                                This feature will be available in the next update.
                            </p>
                        </div>
                    </div>

                    <div className="detail-card">
                        <h3>📊 Processing Details</h3>
                        <div className="detail-row">
                            <span className="detail-label">OCR Status:</span>
                            <span className="detail-value">
                                <span className="status-badge status-success">
                                    {confirmationData.ocr_status || 'PASS'}
                                </span>
                            </span>
                        </div>
                        <div className="detail-row">
                            <span className="detail-label">Hash Status:</span>
                            <span className="detail-value">
                                <span className="status-badge status-success">
                                    {confirmationData.hash_status || 'SUCCESS'}
                                </span>
                            </span>
                        </div>
                        <div className="detail-row">
                            <span className="detail-label">Timestamp:</span>
                            <span className="detail-value">
                                {confirmationData.timestamp || new Date().toLocaleString()}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="success-actions">
                    <button
                        className="btn-primary btn-large"
                        onClick={onNewCertificate}
                    >
                        Register Another Certificate
                    </button>
                </div>

                <div className="info-box">
                    <h4>ℹ️ Important Information</h4>
                    <ul>
                        <li>Save the certificate ID and hash for future reference</li>
                        <li>The hash is unique to this certificate and cannot be changed</li>
                        <li>Verifiers can use the certificate ID or upload the certificate to verify authenticity</li>
                        <li>Blockchain registration will provide immutable proof of issuance</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default UniversitySuccess;
