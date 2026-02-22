import React, { useState } from 'react';
import { verifierAPI } from '../services/api';

const VerifierUpload = ({ onVerificationSuccess, onBack }) => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [uploadedFilename, setUploadedFilename] = useState(null);
    const [ocrData, setOcrData] = useState(null);
    const [aiData, setAiData] = useState(null);
    const [generatedHash, setGeneratedHash] = useState(null);
    const [claimantId, setClaimantId] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [aiMessage, setAiMessage] = useState('');
    const [aiStatus, setAiStatus] = useState(null); // 'pass' or 'fail'

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        setError('');

        if (file) {
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
            if (!validTypes.includes(file.type)) {
                setError('Please select a valid file (JPG, PNG, or PDF)');
                setSelectedFile(null);
                setPreview(null);
                return;
            }

            if (file.size > 5 * 1024 * 1024) {
                setError('File size must be less than 5MB');
                setSelectedFile(null);
                setPreview(null);
                return;
            }

            setSelectedFile(file);
            setOcrData(null);
            setAiData(null);
            setGeneratedHash(null);
            setAiMessage('');
            setAiStatus(null);
            setPreview(null);

            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onloadend = () => {
                    setPreview(reader.result);
                };
                reader.readAsDataURL(file);
            } else {
                setPreview(null);
            }
        }
    };

    const handleUploadAndExtract = async (e) => {
        e.preventDefault();
        setError('');

        if (!claimantId.trim()) {
            setError('Please enter the Roll Number or Certificate ID provided by the claimant.');
            return;
        }

        if (!selectedFile) {
            setError('Please select a certificate file');
            return;
        }

        setLoading(true);
        setUploadedFilename(null);
        setOcrData(null);
        setAiData(null);
        setGeneratedHash(null);
        setAiMessage('');
        setAiStatus(null);

        try {
            const formData = new FormData();
            formData.append('certificate', selectedFile);
            formData.append('claimant_id', claimantId);

            // Step 1: Upload + OCR extraction + Ownership Check
            const result = await verifierAPI.uploadCertificate(formData);

            if (result.success) {
                const data = result.data;
                setUploadedFilename(data.filename);
                setOcrData(data.ocr_data || null);
            } else {
                // Check if it's an ownership rejection
                if (result.data && result.data.status === 'Rejected') {
                    setError(`Rejected: ${result.data.message}`);
                } else {
                    setError(result.error);
                }
            }
        } catch (err) {
            setError('Upload or OCR extraction failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleRunAiDetection = async () => {
        setError('');

        if (!uploadedFilename) {
            setError('Please upload a certificate first.');
            return;
        }

        setLoading(true);

        try {
            // Step 2: AI-based forgery detection only
            const result = await verifierAPI.runAiDetection(uploadedFilename);

            if (result.success) {
                const data = result.data;
                setAiData(data);

                if (data.ai_enabled) {
                    if (data.ai_result === 'Genuine') {
                        setAiMessage(`ai passed (${Math.round(data.confidence * 100)}% Match)`);
                        setAiStatus('pass');
                    } else {
                        setAiMessage(`forgery detected (${Math.round(data.confidence * 100)}% Match)`);
                        setAiStatus('fail');
                    }
                } else {
                    setAiMessage('AI Error: ' + (data.error || 'System not ready'));
                    setAiStatus('fail');
                }
            } else {
                setError(result.error);
                setAiMessage('ai detection failed');
                setAiStatus('fail');
            }
        } catch (err) {
            setError('AI detection failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateHash = async () => {
        setError('');

        if (!uploadedFilename) {
            setError('Please upload a certificate first.');
            return;
        }

        setLoading(true);

        try {
            // Step 3: Generate SHA-256 hash
            console.log("Requesting hash generation...");
            const result = await verifierAPI.generateHash(uploadedFilename);
            console.log("Hash generation result:", result);

            if (result.success) {
                // Determine where the hash is in the response structure
                const hash = result.data.generated_hash || (result.data.data && result.data.data.generated_hash);
                if (hash) {
                    setGeneratedHash(hash);
                    console.log("Hash set to:", hash);
                } else {
                    console.error("Hash missing in response:", result.data);
                    setError("Hash generated but not returned by server.");
                }
            } else {
                console.error("Hash generation failed:", result.error);
                setError(result.error);
            }
        } catch (err) {
            setError('Hash generation failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleBlockchainVerify = async () => {
        setError('');

        if (!ocrData || !ocrData.certificate_id) {
            setError('Certificate ID missing from OCR data. Please re-upload or correct OCR.');
            return;
        }

        if (!generatedHash) {
            setError('Please generate the SHA-256 hash first.');
            return;
        }

        setLoading(true);

        try {
            // Step 4: Verify against blockchain using certificate ID + generated hash
            const result = await verifierAPI.blockchainVerify(
                ocrData.certificate_id,
                generatedHash
            );

            if (result.success) {
                // Combine all step results into a single verification payload
                const finalPayload = {
                    // OCR data
                    ocr_data: ocrData,
                    certificate_id: ocrData.certificate_id,
                    student_name: ocrData.student_name,
                    roll_number: ocrData.roll_number,
                    course: ocrData.course,
                    university: ocrData.university,
                    year: ocrData.year,
                    // AI analysis
                    ai_score: aiData?.ai_score ?? null,
                    ai_result: aiData?.ai_result ?? 'UNKNOWN',
                    // Hashes
                    generated_hash: generatedHash,
                    blockchain_hash: result.data.blockchain_hash,
                    hash_match: result.data.hash_match,
                    // Final status & metadata
                    final_status: result.data.final_status,
                    remarks: result.data.remarks,
                    blockchain_info: result.data.blockchain_info,
                    timestamp: result.data.timestamp,
                };

                onVerificationSuccess(finalPayload);
            } else {
                setError(result.error);
            }
        } catch (err) {
            setError('Blockchain verification failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="verifier-container">
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                    <button onClick={onBack} className="btn-secondary" style={{ padding: '0.4rem 0.8rem' }}>
                        ← Back
                    </button>
                    <h2 style={{ margin: 0 }}>🔍 Verify Certificate</h2>
                </div>
                <p className="subtitle">Upload certificate for verification</p>

                <form onSubmit={handleUploadAndExtract} className="verification-form">
                    <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                        <label htmlFor="claimant-id" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                            Roll Number <span className="required" style={{ color: 'red' }}>*</span>
                        </label>
                        <input
                            type="text"
                            id="claimant-id"
                            value={claimantId}
                            onChange={(e) => setClaimantId(e.target.value)}
                            placeholder="Enter Roll Number (provided by claimant)"
                            disabled={loading || ocrData}
                            className="form-input"
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                borderRadius: '8px',
                                border: '1px solid #ccc',
                                fontSize: '1rem'
                            }}
                        />
                    </div>

                    <div className="file-upload-area">
                        <input
                            type="file"
                            id="verify-file"
                            accept=".jpg,.jpeg,.png,.pdf"
                            onChange={handleFileSelect}
                            disabled={loading}
                            style={{ display: 'none' }}
                        />
                        <label htmlFor="verify-file" className="file-upload-label">
                            {selectedFile ? (
                                <div className="file-selected">
                                    <span className="file-icon">📄</span>
                                    <span className="file-name">{selectedFile.name}</span>
                                    <span className="file-size">
                                        ({(selectedFile.size / 1024).toFixed(2)} KB)
                                    </span>
                                </div>
                            ) : (
                                <div className="file-placeholder">
                                    <span className="upload-icon">📁</span>
                                    <p>Click to select certificate</p>
                                    <p className="file-hint">Supported: JPG, PNG, PDF (Max 5MB)</p>
                                </div>
                            )}
                        </label>
                    </div>

                    {preview && (
                        <div className="image-preview">
                            <img src={preview} alt="Certificate preview" />
                        </div>
                    )}

                    {ocrData && (
                        <div className="ocr-preview">
                            <h3>📋 OCR-Extracted Details</h3>
                            <div className="details-grid">
                                <div className="detail-item">
                                    <span className="detail-label">Certificate ID:</span>
                                    <span className="detail-value">
                                        {ocrData.certificate_id || 'N/A'}
                                    </span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">Student Name:</span>
                                    <span className="detail-value">
                                        {ocrData.student_name || 'N/A'}
                                    </span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">Roll Number:</span>
                                    <span className="detail-value">
                                        {ocrData.roll_number || 'N/A'}
                                    </span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">Course:</span>
                                    <span className="detail-value">
                                        {ocrData.course || 'N/A'}
                                    </span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">University:</span>
                                    <span className="detail-value">
                                        {ocrData.university || 'N/A'}
                                    </span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">Year:</span>
                                    <span className="detail-value">
                                        {ocrData.year || 'N/A'}
                                    </span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-label">CGPA/Marks:</span>
                                    <span className="detail-value">
                                        {ocrData.cgpa || 'N/A'}
                                    </span>
                                </div>
                            </div>
                            <p className="subtitle">
                                Step 1 complete. Now run AI detection, generate hash, then verify on blockchain.
                            </p>
                        </div>
                    )}

                    {error && (
                        <div className="error-message">
                            ⚠️ {error}
                        </div>
                    )}

                    <div className="form-actions">
                        <button
                            type="submit"
                            className="btn-secondary"
                            disabled={loading || !selectedFile}
                        >
                            {loading ? 'Processing...' : '1️⃣ Upload & Extract OCR'}
                        </button>

                        <div className="action-step">
                            <button
                                type="button"
                                className="btn-primary"
                                onClick={handleRunAiDetection}
                                disabled={loading || !uploadedFilename}
                            >
                                {loading ? 'Running AI...' : '2️⃣ Run AI Forgery Detection'}
                            </button>
                            {aiStatus && (
                                <div className={`step-result ${aiStatus}`}>
                                    {aiStatus === 'pass' ? '✅' : '❌'} {aiMessage}
                                </div>
                            )}
                        </div>

                        <div className="action-step">
                            <button
                                type="button"
                                className="btn-primary"
                                onClick={handleGenerateHash}
                                disabled={loading || !uploadedFilename}
                            >
                                {loading ? 'Generating hash...' : '3️⃣ Generate SHA-256 Hash'}
                            </button>
                            {generatedHash && (
                                <div className="step-result pass" style={{ wordBreak: 'break-all', maxWidth: '300px' }}>
                                    ✅ Hash Generated: <br />
                                    <small>{generatedHash}</small>
                                </div>
                            )}
                        </div>
                        <button
                            type="button"
                            className="btn-primary btn-large"
                            onClick={handleBlockchainVerify}
                            disabled={loading || !uploadedFilename || !ocrData || !generatedHash}
                        >
                            {loading ? 'Verifying...' : '4️⃣ Blockchain Verify'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default VerifierUpload;
