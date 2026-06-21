import React, { useState } from 'react';
import { verifierAPI } from '../services/api';

const VerifierUpload = ({ onVerificationSuccess, onBack }) => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [uploadedFilename, setUploadedFilename] = useState(null);
    const [ocrData, setOcrData] = useState(null);
    const [aiData, setAiData] = useState(null);
    const [generatedHash, setGeneratedHash] = useState(null);
    const [academicHashes, setAcademicHashes] = useState({});
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

            // Step 1: Upload + OCR extraction + Ownership Check
            console.log("DEBUG: Sending file to verifier/upload...");
            const result = await verifierAPI.uploadCertificate(formData);
            console.log("DEBUG: uploadCertificate result:", result);

            if (result.success) {
                const data = result.data;
                setUploadedFilename(data.filename);
                setOcrData(data.ocr_data || null);
            } else {
                console.warn("DEBUG: Upload/OCR rejected:", result);
                // Check if it's an registration/validity rejection
                if (result.data && (result.data.status === 'Rejected' || result.data.message)) {
                    setError(result.data.message || result.error);
                } else {
                    setError(result.error || "The certificate could not be verified at this stage.");
                }
            }
        } catch (err) {
            setError('Upload or extraction failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleCompleteVerification = async () => {
        setError('');

        if (!uploadedFilename) {
            setError('Please upload a certificate first.');
            return;
        }

        setLoading(true);

        try {
            console.log("Requesting complete verification for:", uploadedFilename);
            const result = await verifierAPI.verifyCertificate(uploadedFilename);

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
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                    <button onClick={onBack} className="btn-secondary" style={{ padding: '0.4rem 0.8rem' }}>
                        ← Back
                    </button>
                    <h2 style={{ margin: 0 }}>🔍 Verify Certificate</h2>
                </div>
                <p className="subtitle">Upload certificate for verification</p>

                <form onSubmit={handleUploadAndExtract} className="verification-form">

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
                            <h2 style={{ color: '#667eea', marginBottom: '1.5rem', textAlign: 'center' }}>📋 OCR-Extracted Academic Records</h2>

                            {ocrData.academic_data ? (
                                <div className="sections-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                                    {[
                                        { id: '10th', title: '10th Certificate Details', data: ocrData.academic_data.tenth_certificate },
                                        { id: 'Inter', title: 'Intermediate Certificate Details', data: ocrData.academic_data.intermediate_certificate },
                                        { id: 'Degree', title: 'Degree Certificate Details', data: ocrData.academic_data.degree_certificate }
                                    ].map((section) => (
                                        <div key={section.id} className="academic-section-card" style={{ padding: '1.2rem', border: '1px solid #ddd', borderRadius: '8px' }}>
                                            <h4 className="section-title" style={{ marginTop: 0, marginBottom: '1rem' }}>{section.title}</h4>
                                            <div className="details-grid" style={{ fontSize: '0.9rem' }}>
                                                <div className="detail-item">
                                                    <span className="detail-label">Student Name:</span>
                                                    <span className="detail-value">{section.data?.name || 'NOT FOUND'}</span>
                                                </div>
                                                <div className="detail-item">
                                                    <span className="detail-label">Certificate ID:</span>
                                                    <span className="detail-value">{section.data?.certificate_number || 'NOT FOUND'}</span>
                                                </div>
                                                <div className="detail-item">
                                                    <span className="detail-label">Roll Number:</span>
                                                    <span className="detail-value">{section.data?.roll_number || 'NOT FOUND'}</span>
                                                </div>
                                                <div className="detail-item">
                                                    <span className="detail-label">Course:</span>
                                                    <span className="detail-value">{section.data?.course_or_stream || 'NOT FOUND'}</span>
                                                </div>
                                                <div className="detail-item">
                                                    <span className="detail-label">University:</span>
                                                    <span className="detail-value">{section.data?.institution_name || 'NOT FOUND'}</span>
                                                </div>
                                                <div className="detail-item">
                                                    <span className="detail-label">Year:</span>
                                                    <span className="detail-value">{section.data?.year_of_passing || 'NOT FOUND'}</span>
                                                </div>
                                                <div className="detail-item">
                                                    <span className="detail-label">CGPA/Marks:</span>
                                                    <span className="detail-value">{section.data?.cgpa_or_marks || 'NOT FOUND'}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="details-grid">
                                    <div className="detail-item">
                                        <span className="detail-label">Certificate ID:</span>
                                        <span className="detail-value">{ocrData.certificate_id || 'N/A'}</span>
                                    </div>
                                    <div className="detail-item">
                                        <span className="detail-label">Student Name:</span>
                                        <span className="detail-value">{ocrData.student_name || 'N/A'}</span>
                                    </div>
                                    <div className="detail-item">
                                        <span className="detail-label">Roll Number:</span>
                                        <span className="detail-value">{ocrData.roll_number || 'N/A'}</span>
                                    </div>
                                    <div className="detail-item">
                                        <span className="detail-label">Course:</span>
                                        <span className="detail-value">{ocrData.course || 'N/A'}</span>
                                    </div>
                                    <div className="detail-item">
                                        <span className="detail-label">University:</span>
                                        <span className="detail-value">{ocrData.university || 'N/A'}</span>
                                    </div>
                                    <div className="detail-item">
                                        <span className="detail-label">Year:</span>
                                        <span className="detail-value">{ocrData.year || 'N/A'}</span>
                                    </div>
                                    <div className="detail-item">
                                        <span className="detail-label">CGPA/Marks:</span>
                                        <span className="detail-value">{ocrData.cgpa || 'N/A'}</span>
                                    </div>
                                </div>
                            )}

                        </div>
                    )}


                    {error && (
                        <div className="error-message" style={{
                            color: '#e53e3e',
                            backgroundColor: '#fff5f5',
                            border: '2px solid #feb2b2',
                            padding: '1rem',
                            borderRadius: '8px',
                            fontWeight: 'bold',
                            marginTop: '1rem',
                            textAlign: 'center'
                        }}>
                            🚫 {error}
                        </div>
                    )}

                    <div className="form-actions">
                        <button
                            type="submit"
                            className="btn-secondary"
                            disabled={loading || !selectedFile}
                        >
                            {loading && !uploadedFilename ? 'Extracting...' : '1️⃣ Upload & Extract OCR'}
                        </button>

                        <button
                            type="button"
                            className="btn-primary btn-large"
                            onClick={handleCompleteVerification}
                            disabled={loading || !uploadedFilename || !ocrData}
                        >
                            {loading && uploadedFilename ? 'Verifying...' : 'Complete Verification'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default VerifierUpload;
