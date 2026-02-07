import React, { useState } from 'react';
import { verifierAPI } from '../services/api';

const VerifierUpload = ({ onVerificationSuccess }) => {
    const [verificationMode, setVerificationMode] = useState('upload'); // 'upload' or 'id'
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [certificateId, setCertificateId] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

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

    const handleVerifyByUpload = async (e) => {
        e.preventDefault();
        setError('');

        if (!selectedFile) {
            setError('Please select a certificate file');
            return;
        }

        setLoading(true);

        try {
            const formData = new FormData();
            formData.append('certificate', selectedFile);

            const result = await verifierAPI.verifyCertificate(formData);

            if (result.success) {
                onVerificationSuccess(result.data);
            } else {
                setError(result.error);
            }
        } catch (err) {
            setError('Verification failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyById = async (e) => {
        e.preventDefault();
        setError('');

        if (!certificateId.trim()) {
            setError('Please enter a certificate ID');
            return;
        }

        setLoading(true);

        try {
            const result = await verifierAPI.verifyCertificateById(certificateId);

            if (result.success) {
                onVerificationSuccess(result.data);
            } else {
                setError(result.error);
            }
        } catch (err) {
            setError('Verification failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="verifier-container">
                <h2>🔍 Verify Certificate</h2>
                <p className="subtitle">Choose verification method</p>

                <div className="verification-mode-selector">
                    <button
                        className={`mode-btn ${verificationMode === 'upload' ? 'active' : ''}`}
                        onClick={() => setVerificationMode('upload')}
                        disabled={loading}
                    >
                        📤 Upload Certificate
                    </button>
                    <button
                        className={`mode-btn ${verificationMode === 'id' ? 'active' : ''}`}
                        onClick={() => setVerificationMode('id')}
                        disabled={loading}
                    >
                        🔑 Access Blockchain by ID
                    </button>
                </div>

                {verificationMode === 'upload' ? (
                    <form onSubmit={handleVerifyByUpload} className="verification-form">
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

                        {error && (
                            <div className="error-message">
                                ⚠️ {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            className="btn-primary btn-large"
                            disabled={loading || !selectedFile}
                        >
                            {loading ? 'Verifying...' : 'Verify Certificate'}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleVerifyById} className="verification-form">
                        <div className="form-group">
                            <label htmlFor="certificate-id">
                                Certificate ID <span className="required">*</span>
                            </label>
                            <input
                                type="text"
                                id="certificate-id"
                                value={certificateId}
                                onChange={(e) => setCertificateId(e.target.value)}
                                placeholder="Enter certificate ID (e.g., MT2023/CS/001)"
                                disabled={loading}
                            />
                        </div>

                        {error && (
                            <div className="error-message">
                                ⚠️ {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            className="btn-primary btn-large"
                            disabled={loading || !certificateId.trim()}
                        >
                            {loading ? 'Accessing Blockchain...' : 'Access Blockchain'}
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
};

export default VerifierUpload;
