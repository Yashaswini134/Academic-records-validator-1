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
                    {confirmationData.all_certificates ? (
                        <div className="multi-success-list" style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                            {/* Combined Hash Section */}
                            <div className="detail-card" style={{ background: '#f0f7ff', border: '1px solid #cce5ff' }}>
                                <h3>🔐 Combined Record Hash</h3>
                                <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.8rem' }}>
                                    This single SHA-256 hash covers all certificates in this record.
                                </p>
                                <div className="hash-display" style={{ background: '#fff' }}>
                                    <code className="hash-value">{confirmationData.hash}</code>
                                    <button className="btn-copy" onClick={() => copyToClipboard(confirmationData.hash)}>📋</button>
                                </div>
                                <div className="detail-row" style={{ marginTop: '0.8rem' }}>
                                    <span className="detail-label">Blockchain Status:</span>
                                    <span className={`status-badge ${confirmationData.blockchain_status === 'Success' ? 'status-success' : 'status-warning'}`}>
                                        {confirmationData.blockchain_status}
                                    </span>
                                </div>
                                {confirmationData.tx_hash && (
                                    <div className="detail-row" style={{ fontSize: '0.8rem', color: '#666' }}>
                                        <span className="detail-label">TX Hash:</span>
                                        <span style={{ wordBreak: 'break-all' }}>{confirmationData.tx_hash}</span>
                                    </div>
                                )}
                            </div>

                            <h3 style={{ borderBottom: '2px solid #eee', paddingBottom: '0.5rem', marginTop: '1rem' }}>📜 Included Certificates</h3>
                            {confirmationData.all_certificates.map((cert, idx) => (
                                <div key={idx} className="detail-card academic-section-card" style={{ border: '1px solid #e7f3ff', background: '#fcfdff' }}>
                                    <h4>{cert.cert_type} - {cert.student_name}</h4>
                                    <div className="detail-row">
                                        <span className="detail-label">Certificate ID:</span>
                                        <span className="detail-value"><strong>{cert.certificate_id}</strong></span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <>
                            <div className="detail-card">
                                <h3>📋 Certificate Information</h3>
                                <div className="detail-row">
                                    <span className="detail-label">Certificate ID:</span>
                                    <span className="detail-value">{confirmationData.certificate_id}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="detail-label">Student Name:</span>
                                    <span className="detail-value">{confirmationData.student_name}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="detail-label">University:</span>
                                    <span className="detail-value">{confirmationData.university}</span>
                                </div>
                            </div>

                            <div className="detail-card">
                                <h3>🔐 Security Hash</h3>
                                <div className="hash-display">
                                    <code className="hash-value">{confirmationData.hash || 'Hash generation pending...'}</code>
                                    {confirmationData.hash && (
                                        <button className="btn-copy" onClick={() => copyToClipboard(confirmationData.hash)} title="Copy hash">📋</button>
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
                                            <span className="status-badge status-success">⛓️ Registered on Blockchain</span>
                                            <p className="status-message" style={{ wordBreak: 'break-all', fontSize: '0.8rem', marginTop: '0.5rem' }}>
                                                <strong>Transaction Hash:</strong><br />{confirmationData.tx_hash}
                                            </p>
                                        </>
                                    ) : (
                                        <span className="status-badge status-pending">{confirmationData.blockchain_status || 'Pending'}</span>
                                    )}
                                </div>
                            </div>
                        </>
                    )}

                    <div className="detail-card" style={{ marginTop: '1rem' }}>
                        <h3>📊 Processing Metadata</h3>
                        <div className="detail-row">
                            <span className="detail-label">Timestamp:</span>
                            <span className="detail-value">{confirmationData.timestamp || new Date().toLocaleString()}</span>
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
                        View Registered Certificates
                    </button>
                </div>


            </div>
        </div>
    );
};

export default UniversitySuccess;
