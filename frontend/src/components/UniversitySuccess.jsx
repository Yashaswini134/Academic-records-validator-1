import React from 'react';

const UniversitySuccess = ({ confirmationData, onNewCertificate, onViewIssued, onBack }) => {
    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        alert('Copied to clipboard!');
    };

    return (
        <div className="container">
            <div className="success-container">
                <button onClick={onBack} className="btn-secondary" style={{ marginBottom: '1rem' }}>
                    ← Back
                </button>
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
                            {confirmationData.blockchain_status === 'Success' ? (
                                <>
                                    <span className="status-badge status-success">
                                        ⛓️ Registered on Blockchain
                                    </span>
                                    <p className="status-message" style={{ wordBreak: 'break-all', fontSize: '0.8rem', marginTop: '0.5rem' }}>
                                        <strong>Transaction Hash:</strong><br />
                                        {confirmationData.tx_hash}
                                    </p>
                                </>
                            ) : confirmationData.blockchain_status === 'Already Registered' ? (
                                <>
                                    <span className="status-badge status-success" style={{ background: '#28a745' }}>
                                        ✅ Already on Blockchain
                                    </span>
                                    <p className="status-message">
                                        This certificate ID was already registered in a previous session.
                                    </p>
                                </>
                            ) : confirmationData.blockchain_status?.includes('Fallback') ? (
                                <>
                                    <span className="status-badge status-warning" style={{ background: '#ffc107', color: '#000' }}>
                                        ⚠️ Local Storage Only
                                    </span>
                                    <p className="status-message">
                                        Blockchain unavailable. Hash stored safely in university local database.
                                    </p>
                                </>
                            ) : (
                                <>
                                    <span className="status-badge status-pending">
                                        ⏳ {confirmationData.blockchain_status || 'Blockchain Registration Pending'}
                                    </span>
                                    <p className="status-message">
                                        {confirmationData.tx_hash ? `TX: ${confirmationData.tx_hash}` : 'The certificate registration is being processed.'}
                                    </p>
                                </>
                            )}
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

                <div className="success-actions" style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                    <button
                        className="btn-primary"
                        onClick={onNewCertificate}
                        style={{ padding: '1rem 2rem' }}
                    >
                        Register Another Certificate
                    </button>
                    <button
                        className="btn-secondary"
                        onClick={onViewIssued}
                        style={{ padding: '1rem 2rem' }}
                    >
                        View Issued Certificates
                    </button>
                </div>


            </div>
        </div>
    );
};

export default UniversitySuccess;
