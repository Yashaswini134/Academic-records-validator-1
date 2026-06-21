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
        (verificationData.is_multi && verificationData.academic_results?.every(r => r.final_status === 'VERIFIED' || r.final_status === 'Genuine') ? 'VERIFIED' : 'SUSPICIOUS');

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

                    {verificationData.academic_data || verificationData.ocr_data?.academic_data ? (
                        <div className="sections-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                            {[
                                { id: '10th', title: '10th Certificate Details', key: 'tenth_certificate' },
                                { id: 'Inter', title: 'Intermediate Certificate Details', key: 'intermediate_certificate' },
                                { id: 'Degree', title: 'Degree Certificate Details', key: 'degree_certificate' }
                            ].map((section) => {
                                const sectionData = (verificationData.academic_data || verificationData.ocr_data?.academic_data)[section.key];
                                const resultInfo = verificationData.is_multi ? verificationData.academic_results.find(r => r.level === section.key) : null;

                                if (!sectionData && !resultInfo) return null;

                                return (
                                    <div key={section.id} className="academic-section-card" style={{ padding: '1.5rem', border: '2px solid #eef0f2', borderRadius: '12px', background: 'white' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.2rem' }}>
                                            <h4 className="section-title" style={{ margin: 0 }}>{section.title}</h4>
                                            {resultInfo && (
                                                <span className={`status-badge ${resultInfo.final_status === 'VERIFIED' || resultInfo.final_status === 'Genuine' ? 'status-success' : 'status-fake'}`} style={{ fontSize: '0.75rem' }}>
                                                    {resultInfo.final_status}
                                                </span>
                                            )}
                                        </div>

                                        <div className="details-grid" style={{ fontSize: '0.9rem' }}>
                                            <div className="detail-item">
                                                <span className="detail-label">Certificate ID:</span>
                                                <span className="detail-value">{sectionData?.certificate_number || sectionData?.certificate_id || 'N/A'}</span>
                                            </div>
                                            <div className="detail-item">
                                                <span className="detail-label">Roll Number:</span>
                                                <span className="detail-value">{sectionData?.roll_number || 'N/A'}</span>
                                            </div>
                                            <div className="detail-item">
                                                <span className="detail-label">University:</span>
                                                <span className="detail-value">{sectionData?.institution_name || sectionData?.university || 'N/A'}</span>
                                            </div>
                                            <div className="detail-item">
                                                <span className="detail-label">Year:</span>
                                                <span className="detail-value">{sectionData?.year_of_passing || sectionData?.year || 'N/A'}</span>
                                            </div>
                                        </div>

                                        {resultInfo && (
                                            <div className="blockchain-micro-info" style={{ marginTop: '1rem', padding: '0.8rem', background: '#f8f9fa', borderRadius: '8px', fontSize: '0.85rem' }}>
                                                <div style={{ display: 'flex', gap: '1rem' }}>
                                                    <div><strong>Hash Match:</strong> {resultInfo.hash_match ? '✅ Passed' : '❌ Failed'}</div>
                                                    <div><strong>BC Status:</strong> {resultInfo.blockchain_info?.status || 'Active'}</div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}

                        </div>
                    ) : (
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
                    )}
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
