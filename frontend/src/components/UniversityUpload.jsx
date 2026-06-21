import React, { useState } from 'react';
import { universityAPI } from '../services/api';

const UniversityUpload = ({ onUploadSuccess, onBack }) => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        setError('');

        if (file) {
            // Validate file type
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
            if (!validTypes.includes(file.type)) {
                setError('Please select a valid file (JPG, PNG, or PDF)');
                setSelectedFile(null);
                setPreview(null);
                return;
            }

            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                setError('File size must be less than 5MB');
                setSelectedFile(null);
                setPreview(null);
                return;
            }

            setSelectedFile(file);

            // Create preview for images
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

    const handleSubmit = async (e) => {
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

            const result = await universityAPI.uploadCertificate(formData);

            if (result.success) {
                onUploadSuccess(result.data);
            } else {
                setError(result.error);
            }
        } catch (err) {
            setError('Upload failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="upload-container">
                <div className="flex-row-between">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <button onClick={onBack} className="btn-secondary" style={{ padding: '0.4rem 0.8rem' }}>
                            ← Back
                        </button>
                        <h2 style={{ margin: 0 }}>📤 Upload Certificate</h2>
                    </div>
                    <button
                        onClick={() => onUploadSuccess('dashboard_shortcut')}
                        className="btn-secondary"
                        style={{ padding: '0.5rem 1rem' }}
                    >
                        View Registered Certificates
                    </button>
                </div>
                <p className="subtitle">Upload a certificate for OCR extraction and registration</p>

                <form onSubmit={handleSubmit} className="upload-form">
                    <div className="file-upload-area">
                        <input
                            type="file"
                            id="certificate-file"
                            accept=".jpg,.jpeg,.png,.pdf"
                            onChange={handleFileSelect}
                            disabled={loading}
                            style={{ display: 'none' }}
                        />
                        <label htmlFor="certificate-file" className="file-upload-label">
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

                    <div className="form-actions">
                        <button
                            type="submit"
                            className="btn-primary btn-large"
                            disabled={loading || !selectedFile}
                        >
                            {loading ? 'Processing...' : 'Upload & Extract Data'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default UniversityUpload;
