import React, { useState } from 'react';
import { universityAPI } from '../services/api';

const UniversityReview = ({ extractedData, onConfirmSuccess, onBack }) => {
    // Initialize state with multi-certificate structure from backend's academic_data
    const [academicData, setAcademicData] = useState({
        tenth_certificate: extractedData.academic_data?.tenth_certificate || {
            name: extractedData.student_name || '',
            certificate_number: extractedData.certificate_id || '',
            roll_number: extractedData.roll_number || '',
            institution_name: extractedData.university || '',
            year_of_passing: extractedData.year || '',
            course_or_stream: 'SSC',
            cgpa_or_marks: extractedData.cgpa || ''
        },
        intermediate_certificate: extractedData.academic_data?.intermediate_certificate || {
            name: '', certificate_number: '', roll_number: '', institution_name: '', year_of_passing: '', course_or_stream: '', cgpa_or_marks: ''
        },
        degree_certificate: extractedData.academic_data?.degree_certificate || {
            name: '', certificate_number: '', roll_number: '', institution_name: '', year_of_passing: '', course_or_stream: '', cgpa_or_marks: ''
        }
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleFieldChange = (certType, field, value) => {
        setAcademicData({
            ...academicData,
            [certType]: {
                ...academicData[certType],
                [field]: value
            }
        });
    };

    const handleConfirm = async () => {
        setError('');

        // Basic validation for at least one certificate ID
        if (!academicData.tenth_certificate.certificate_number &&
            !academicData.intermediate_certificate.certificate_number &&
            !academicData.degree_certificate.certificate_number) {
            setError('Please provide at least one Certificate ID for any level.');
            return;
        }

        setLoading(true);

        try {
            // Sends the structured multi-certificate data to the backend
            // In a real scenario, this would register all three in a batch or the primary one
            const result = await universityAPI.confirmCertificate({
                ...academicData.degree_certificate, // Fallback to degree for main storage
                academic_data: academicData // Include full payload
            });

            if (result.success) {
                onConfirmSuccess(result.data);
            } else {
                setError(result.error || 'Confirmation failed');
            }
        } catch (err) {
            setError('System error during confirmation.');
        } finally {
            setLoading(false);
        }
    };

    const renderCertificateSection = (title, type, data) => (
        <div className="academic-section-card" key={type}>
            <h3 className="section-title">{title}</h3>
            <div className="review-form">
                <div className="form-row">
                    <div className="form-group">
                        <label>Student Name</label>
                        <input
                            type="text"
                            value={data.name || ''}
                            onChange={(e) => handleFieldChange(type, 'name', e.target.value)}
                            placeholder="Full Name"
                            disabled={loading}
                        />
                    </div>
                    <div className="form-group">
                        <label>Certificate ID</label>
                        <input
                            type="text"
                            value={data.certificate_number || ''}
                            onChange={(e) => handleFieldChange(type, 'certificate_number', e.target.value)}
                            placeholder="Certificate No."
                            disabled={loading}
                        />
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label>Roll / Reg Number</label>
                        <input
                            type="text"
                            value={data.roll_number || ''}
                            onChange={(e) => handleFieldChange(type, 'roll_number', e.target.value)}
                            placeholder="Roll No."
                            disabled={loading}
                        />
                    </div>
                    <div className="form-group">
                        <label>Year of Passing</label>
                        <input
                            type="text"
                            value={data.year_of_passing || ''}
                            onChange={(e) => handleFieldChange(type, 'year_of_passing', e.target.value)}
                            placeholder="YYYY"
                            disabled={loading}
                        />
                    </div>
                </div>

                <div className="form-group">
                    <label>Course / Stream / Degree</label>
                    <input
                        type="text"
                        value={data.course_or_stream || ''}
                        onChange={(e) => handleFieldChange(type, 'course_or_stream', e.target.value)}
                        placeholder="e.g. B.Tech CSE / MPC / SSC"
                        disabled={loading}
                    />
                </div>

                <div className="form-group">
                    <label>Board / University Name</label>
                    <input
                        type="text"
                        value={data.institution_name || ''}
                        onChange={(e) => handleFieldChange(type, 'institution_name', e.target.value)}
                        placeholder="Institution Name"
                        disabled={loading}
                    />
                </div>

                <div className="form-group">
                    <label>CGPA / Percentage / Marks</label>
                    <input
                        type="text"
                        value={data.cgpa_or_marks || ''}
                        onChange={(e) => handleFieldChange(type, 'cgpa_or_marks', e.target.value)}
                        placeholder="Results"
                        disabled={loading}
                    />
                </div>
            </div>
        </div>
    );

    return (
        <div className="container" style={{ maxWidth: '1000px' }}>
            <div className="multi-review-wrapper">
                <div className="review-header">
                    <div className="header-top">
                        <button onClick={onBack} className="btn-secondary" style={{ padding: '0.5rem 1rem' }}>
                            ← Back
                        </button>
                    </div>
                </div>


                <div className="sections-container" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', marginTop: '1rem' }}>
                    {renderCertificateSection("10th Certificate Details", "tenth_certificate", academicData.tenth_certificate)}
                    {renderCertificateSection("Intermediate Certificate Details", "intermediate_certificate", academicData.intermediate_certificate)}
                    {renderCertificateSection("Degree Certificate Details", "degree_certificate", academicData.degree_certificate)}
                </div>

                {error && <div className="error-message" style={{ marginTop: '1.5rem' }}>⚠️ {error}</div>}

                <div className="final-actions" style={{ marginTop: '2.5rem', display: 'flex', justifyContent: 'center' }}>
                    <button
                        className="btn-primary btn-large"
                        style={{ maxWidth: '400px', padding: '1.2rem', fontSize: '1.2rem', fontWeight: 'bold' }}
                        onClick={handleConfirm}
                        disabled={loading}
                    >
                        {loading ? 'Generating Hash...' : 'Generate Hash'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default UniversityReview;
