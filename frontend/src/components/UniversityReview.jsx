import React, { useState } from 'react';
import { universityAPI } from '../services/api';

const UniversityReview = ({ extractedData, onConfirmSuccess, onBack }) => {
    const [formData, setFormData] = useState({
        certificate_id: extractedData.certificate_id || '',
        student_name: extractedData.student_name || '',
        roll_number: extractedData.roll_number || '',
        course: extractedData.course || '',
        university: extractedData.university || '',
        year: extractedData.year || '',
        cgpa: extractedData.cgpa || '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleConfirm = async () => {
        setError('');

        // Validate required fields
        if (!formData.certificate_id || !formData.student_name || !formData.university) {
            setError('Certificate ID, Student Name, and University are required fields');
            return;
        }

        setLoading(true);

        try {
            const result = await universityAPI.confirmCertificate(formData);

            if (result.success) {
                onConfirmSuccess(result.data);
            } else {
                setError(result.error);
            }
        } catch (err) {
            setError('Confirmation failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="review-container">
                <h2>📋 Review Extracted Details</h2>
                <p className="subtitle">
                    Review and edit the OCR-extracted information before confirmation
                </p>

                <div className="ocr-status">
                    {extractedData.status === 'Already Issued' ? (
                        <>
                            <span className="status-badge status-warning" style={{ background: '#ffc107', color: '#000' }}>
                                ⚠️ Already Issued
                            </span>
                            <p style={{ color: '#856404', fontWeight: 'bold', marginTop: '0.5rem' }}>
                                {extractedData.message}
                            </p>
                        </>
                    ) : (
                        <>
                            <span className="status-badge status-success">
                                ✓ OCR Extraction Complete
                            </span>
                            <p>Status: {extractedData.ocr_status || 'PASS'}</p>
                        </>
                    )}
                </div>

                <div className="review-form">
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="certificate_id">
                                Certificate ID <span className="required">*</span>
                            </label>
                            <input
                                type="text"
                                id="certificate_id"
                                name="certificate_id"
                                value={formData.certificate_id}
                                onChange={handleChange}
                                placeholder="Enter certificate ID"
                                disabled={loading}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="student_name">
                                Student Name <span className="required">*</span>
                            </label>
                            <input
                                type="text"
                                id="student_name"
                                name="student_name"
                                value={formData.student_name}
                                onChange={handleChange}
                                placeholder="Enter student name"
                                disabled={loading}
                            />
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="roll_number">Roll / Registration Number</label>
                            <input
                                type="text"
                                id="roll_number"
                                name="roll_number"
                                value={formData.roll_number}
                                onChange={handleChange}
                                placeholder="Enter roll number"
                                disabled={loading}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="year">Year of Passing</label>
                            <input
                                type="text"
                                id="year"
                                name="year"
                                value={formData.year}
                                onChange={handleChange}
                                placeholder="Enter year"
                                disabled={loading}
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="course">Course / Degree</label>
                        <input
                            type="text"
                            id="course"
                            name="course"
                            value={formData.course}
                            onChange={handleChange}
                            placeholder="Enter course name"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="university">
                            University Name <span className="required">*</span>
                        </label>
                        <input
                            type="text"
                            id="university"
                            name="university"
                            value={formData.university}
                            onChange={handleChange}
                            placeholder="Enter university name"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="cgpa">CGPA / Percentage</label>
                        <input
                            type="text"
                            id="cgpa"
                            name="cgpa"
                            value={formData.cgpa}
                            onChange={handleChange}
                            placeholder="Enter CGPA or percentage"
                            disabled={loading}
                        />
                    </div>

                    {error && (
                        <div className="error-message">
                            ⚠️ {error}
                        </div>
                    )}

                    <div className="form-actions">
                        <button
                            type="button"
                            className="btn-secondary"
                            onClick={onBack}
                            disabled={loading}
                        >
                            Back
                        </button>
                        <button
                            type="button"
                            className="btn-primary btn-large"
                            onClick={handleConfirm}
                            disabled={loading || extractedData.status === 'Already Issued'}
                        >
                            {loading ? 'Confirming...' : 'Confirm & Generate Hash'}
                        </button>
                    </div>
                </div>


            </div>
        </div>
    );
};

export default UniversityReview;
