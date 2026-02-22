import React from 'react';

const VerificationResult = ({ verificationData, onNewVerification, onBack }) => {
    const getDecisionBadge = (decision) => {
        const badges = {
            'VERIFIED': { class: 'status-verified', icon: '✅', text: 'VERIFIED' },
            'SUSPICIOUS': { class: 'status-suspicious', icon: '⚠️', text: 'SUSPICIOUS' },
            'FAKE': { class: 'status-fake', icon: '❌', text: 'FAKE' },
            'MANUAL REVIEW': { class: 'status-review', icon: '🔍', text: 'MANUAL REVIEW' },
        };
        return badges[decision] || badges['SUSPICIOUS'];
    };

    // Normalize decision and analysis fields from backend
    const finalDecision =
        verificationData.final_decision ||
        verificationData.final_status ||
        'SUSPICIOUS';

    const badge = getDecisionBadge(finalDecision);

    const hashMatch =
        typeof verificationData.hash_match === 'boolean'
            ? verificationData.hash_match
            : verificationData.hash_status === 'SUCCESS';

    const aiAnalysis = verificationData.ai_analysis || {
        ai_enabled: typeof verificationData.ai_score === 'number',
        ai_score: verificationData.ai_score ?? 0,
        ai_result: verificationData.ai_result || 'UNKNOWN',
    };

    return (
        <div className="container">
            <div className="result-container">
                <div className="result-header">
                    <button onClick={onBack} className="btn-secondary" style={{ float: 'left' }}>
                        ← Back
                    </button>
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
                                {verificationData.certificate_id ||
                                    verificationData.ocr_data?.certificate_id ||
                                    'N/A'}
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">Student Name:</span>
                            <span className="detail-value">
                                {verificationData.student_name ||
                                    verificationData.ocr_data?.student_name ||
                                    'N/A'}
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">Roll Number:</span>
                            <span className="detail-value">
                                {verificationData.roll_number ||
                                    verificationData.ocr_data?.roll_number ||
                                    'N/A'}
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">Course:</span>
                            <span className="detail-value">
                                {verificationData.course ||
                                    verificationData.ocr_data?.course ||
                                    'N/A'}
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">University:</span>
                            <span className="detail-value">
                                {verificationData.university ||
                                    verificationData.ocr_data?.university ||
                                    'N/A'}
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">Year:</span>
                            <span className="detail-value">
                                {verificationData.year ||
                                    verificationData.ocr_data?.year ||
                                    'N/A'}
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
                                {verificationData.blockchain_hash ||
                                    verificationData.hash ||
                                    'Not available'}
                            </code>
                        </div>
                        <div className="hash-item">
                            <span className="hash-label">📄 Current Hash (from uploaded file):</span>
                            <code className="hash-code">
                                {verificationData.current_hash ||
                                    verificationData.generated_hash ||
                                    verificationData.hash ||
                                    'Not available'}
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
                                {verificationData.hash_status ||
                                    (hashMatch ? 'SUCCESS' : 'MISMATCH')}
                            </span>
                        </div>
                        {verificationData.blockchain_info && (
                            <div className="blockchain-info">
                                <h4>⛓️ Blockchain Information</h4>
                                <div className="details-grid">
                                    <div className="detail-item">
                                        <span className="detail-label">Block Number:</span>
                                        <span className="detail-value">
                                            {verificationData.blockchain_info.blockNumber ||
                                                verificationData.blockchain_info.block_number ||
                                                'N/A'}
                                        </span>
                                    </div>
                                    <div className="detail-item">
                                        <span className="detail-label">Transaction Hash:</span>
                                        <span
                                            className="detail-value"
                                            style={{ fontSize: '0.8rem', wordBreak: 'break-all' }}
                                        >
                                            {verificationData.blockchain_info.transactionHash ||
                                                verificationData.blockchain_info.tx_hash ||
                                                'N/A'}
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
                                <div className="ai-score-label">AI Authentication Score</div>
                                <div className="ai-score-value" style={{
                                    color: aiAnalysis.ai_result === 'Genuine' ? '#28a745' : '#dc3545'
                                }}>
                                    {(aiAnalysis.ai_score * 100).toFixed(1)}%
                                </div>
                                <div className="ai-score-bar">
                                    <div
                                        className="ai-score-fill"
                                        style={{
                                            width: `${aiAnalysis.ai_score * 100}%`,
                                            backgroundColor:
                                                aiAnalysis.ai_result === 'Genuine'
                                                    ? '#28a745' // Success Green
                                                    : '#dc3545', // Danger Red
                                        }}
                                    ></div>
                                </div>
                            </div>
                            <div className="ai-result">
                                <span className="detail-label">AI Result:</span>
                                <span
                                    className={`status-badge ${aiAnalysis.ai_result === 'Genuine'
                                        ? 'status-success'
                                        : 'status-fake'
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
                            </div>
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


                <div className="result-actions">
                    <button
                        className="btn-primary btn-large"
                        onClick={onNewVerification}
                    >
                        Verify Another Certificate
                    </button>
                </div>

            </div>
        </div>
    );
};

export default VerificationResult;
