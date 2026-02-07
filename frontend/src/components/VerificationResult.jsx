import React from 'react';

const VerificationResult = ({ verificationData, onNewVerification }) => {
    const getDecisionBadge = (decision) => {
        const badges = {
            'VERIFIED': { class: 'status-verified', icon: '✅', text: 'VERIFIED' },
            'SUSPICIOUS': { class: 'status-suspicious', icon: '⚠️', text: 'SUSPICIOUS' },
            'FAKE': { class: 'status-fake', icon: '❌', text: 'FAKE' },
            'MANUAL REVIEW': { class: 'status-review', icon: '🔍', text: 'MANUAL REVIEW' },
        };
        return badges[decision] || badges['SUSPICIOUS'];
    };

    const badge = getDecisionBadge(verificationData.final_decision);
    const hashMatch = verificationData.hash_status === 'SUCCESS';
    const aiAnalysis = verificationData.ai_analysis || {};

    return (
        <div className="container">
            <div className="result-container">
                <div className="result-header">
                    <div className={`result-icon ${badge.class}`}>
                        {badge.icon}
                    </div>
                    <h2>Verification Result</h2>
                    <div className={`decision-badge ${badge.class}`}>
                        {badge.text}
                    </div>
                </div>

                {/* Certificate Details */}
                <div className="result-section">
                    <h3>📋 Certificate Details</h3>
                    <div className="details-grid">
                        <div className="detail-item">
                            <span className="detail-label">Certificate ID:</span>
                            <span className="detail-value">
                                {verificationData.certificate_id || 'N/A'}
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">Student Name:</span>
                            <span className="detail-value">
                                {verificationData.student_name || 'N/A'}
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">Roll Number:</span>
                            <span className="detail-value">
                                {verificationData.roll_number || 'N/A'}
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">Course:</span>
                            <span className="detail-value">
                                {verificationData.course || 'N/A'}
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">University:</span>
                            <span className="detail-value">
                                {verificationData.university || 'N/A'}
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">Year:</span>
                            <span className="detail-value">
                                {verificationData.year || 'N/A'}
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">CGPA:</span>
                            <span className="detail-value">
                                {verificationData.cgpa || 'N/A'}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Hash Comparison */}
                <div className="result-section">
                    <h3>🔐 Hash Comparison & Blockchain Verification</h3>
                    <div className="hash-comparison">
                        <div className="hash-item">
                            <span className="hash-label">📜 Original Hash (from Blockchain):</span>
                            <code className="hash-code">
                                {verificationData.blockchain_hash || verificationData.hash || 'Not available'}
                            </code>
                        </div>
                        <div className="hash-item">
                            <span className="hash-label">📄 Current Hash (from uploaded file):</span>
                            <code className="hash-code">
                                {verificationData.current_hash || verificationData.hash || 'Not available'}
                            </code>
                        </div>
                        <div className="hash-match-indicator">
                            {hashMatch ? (
                                <span className="match-badge match-success">
                                    ✓ Hash Match - Certificate Not Tampered
                                </span>
                            ) : (
                                <span className="match-badge match-fail">
                                    ✗ Hash Mismatch - Certificate May Be Tampered
                                </span>
                            )}
                        </div>
                        <div className="hash-status">
                            <span className="detail-label">Hash Verification:</span>
                            <span className={`status-badge ${hashMatch ? 'status-success' : 'status-error'}`}>
                                {verificationData.hash_status || 'UNKNOWN'}
                            </span>
                        </div>
                        {verificationData.blockchain_info && (
                            <div className="blockchain-info">
                                <h4>⛓️ Blockchain Information</h4>
                                <div className="details-grid">
                                    <div className="detail-item">
                                        <span className="detail-label">Block Number:</span>
                                        <span className="detail-value">
                                            {verificationData.blockchain_info.blockNumber || 'N/A'}
                                        </span>
                                    </div>
                                    <div className="detail-item">
                                        <span className="detail-label">Transaction Hash:</span>
                                        <span className="detail-value" style={{ fontSize: '0.8rem', wordBreak: 'break-all' }}>
                                            {verificationData.blockchain_info.transactionHash || 'N/A'}
                                        </span>
                                    </div>
                                    <div className="detail-item">
                                        <span className="detail-label">Blockchain Status:</span>
                                        <span className="status-badge status-success">
                                            {verificationData.blockchain_info.status || 'CONFIRMED'}
                                        </span>
                                    </div>
                                    <div className="detail-item">
                                        <span className="detail-label">Registered On:</span>
                                        <span className="detail-value">
                                            {verificationData.blockchain_info.timestamp
                                                ? new Date(verificationData.blockchain_info.timestamp).toLocaleString()
                                                : 'N/A'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* AI Forgery Detection */}
                <div className="result-section">
                    <h3>🤖 AI Forgery Detection</h3>
                    {aiAnalysis.ai_enabled ? (
                        <div className="ai-analysis">
                            <div className="ai-score-display">
                                <div className="ai-score-label">AI Suspicion Score</div>
                                <div className="ai-score-value">
                                    {(aiAnalysis.ai_score * 100).toFixed(1)}%
                                </div>
                                <div className="ai-score-bar">
                                    <div
                                        className="ai-score-fill"
                                        style={{
                                            width: `${aiAnalysis.ai_score * 100}%`,
                                            backgroundColor:
                                                aiAnalysis.ai_score < 0.3
                                                    ? '#4caf50'
                                                    : aiAnalysis.ai_score < 0.7
                                                        ? '#ff9800'
                                                        : '#f44336',
                                        }}
                                    ></div>
                                </div>
                            </div>
                            <div className="ai-result">
                                <span className="detail-label">AI Result:</span>
                                <span
                                    className={`status-badge ${aiAnalysis.ai_result === 'Genuine'
                                        ? 'status-success'
                                        : 'status-warning'
                                        }`}
                                >
                                    {aiAnalysis.ai_result}
                                </span>
                            </div>
                            <div className="ai-explanation">
                                <p>
                                    {aiAnalysis.ai_result === 'Genuine'
                                        ? '✓ The AI model has analyzed the certificate and found no suspicious patterns.'
                                        : '⚠️ The AI model has detected potential forgery patterns. Manual review recommended.'}
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="ai-unavailable">
                            <p>⚠️ AI analysis not available for this verification</p>
                        </div>
                    )}
                </div>

                {/* Final Decision */}
                <div className="result-section">
                    <h3>⚖️ Final Decision</h3>
                    <div className="final-decision">
                        <div className={`decision-card ${badge.class}`}>
                            <div className="decision-icon">{badge.icon}</div>
                            <div className="decision-text">
                                <h4>{badge.text}</h4>
                                <p className="decision-confidence">
                                    Confidence: {verificationData.decision_confidence || 'N/A'}
                                </p>
                            </div>
                        </div>
                        <div className="decision-remarks">
                            <h4>Explanation:</h4>
                            <p>{verificationData.remarks || 'No additional remarks'}</p>
                        </div>
                        {verificationData.flags && verificationData.flags.length > 0 && (
                            <div className="decision-flags">
                                <h4>Flags:</h4>
                                <ul>
                                    {verificationData.flags.map((flag, index) => (
                                        <li key={index}>
                                            <span className="flag-badge">{flag}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </div>

                {/* Processing Info */}
                <div className="result-section">
                    <h3>📊 Processing Information</h3>
                    <div className="processing-info">
                        <div className="info-item">
                            <span className="info-label">OCR Status:</span>
                            <span className={`status-badge ${verificationData.ocr_status === 'PASS' ? 'status-success' : 'status-warning'
                                }`}>
                                {verificationData.ocr_status || 'N/A'}
                            </span>
                        </div>
                        <div className="info-item">
                            <span className="info-label">Processing Time:</span>
                            <span className="info-value">
                                {verificationData.processing_time || 'N/A'}
                            </span>
                        </div>
                        <div className="info-item">
                            <span className="info-label">Timestamp:</span>
                            <span className="info-value">
                                {verificationData.timestamp || new Date().toLocaleString()}
                            </span>
                        </div>
                        <div className="info-item">
                            <span className="info-label">Verification Version:</span>
                            <span className="info-value">
                                {verificationData.verification_version || '2.0'}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="result-actions">
                    <button
                        className="btn-primary btn-large"
                        onClick={onNewVerification}
                    >
                        Verify Another Certificate
                    </button>
                </div>

                <div className="info-box">
                    <h4>ℹ️ Understanding the Results</h4>
                    <ul>
                        <li>
                            <strong>VERIFIED:</strong> Certificate is authentic. All checks passed.
                        </li>
                        <li>
                            <strong>SUSPICIOUS:</strong> Certificate has issues. OCR or data validation failed.
                        </li>
                        <li>
                            <strong>FAKE:</strong> Certificate is tampered. Hash verification failed.
                        </li>
                        <li>
                            <strong>MANUAL REVIEW:</strong> AI detected suspicious patterns. Human review needed.
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default VerificationResult;
