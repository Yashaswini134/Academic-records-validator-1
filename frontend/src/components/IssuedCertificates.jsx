
import React, { useState, useEffect } from 'react';
import { universityAPI } from '../services/api';

const IssuedCertificates = ({ onBack }) => {
    const [certificates, setCertificates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchCertificates();
    }, []);

    const fetchCertificates = async () => {
        setLoading(true);
        const result = await universityAPI.getIssuedCertificates();
        if (result.success) {
            setCertificates(result.data.certificates || []);
        } else {
            setError(result.error);
        }
        setLoading(false);
    };

    return (
        <div className="container">
            <div className="dashboard-header">
                <h2>📜 Issued Certificates</h2>
                <button onClick={onBack} className="btn-secondary">
                    ← Back to Upload
                </button>
            </div>

            {loading ? (
                <div className="loading-state">
                    <p>Loading issued certificates...</p>
                </div>
            ) : error ? (
                <div className="error-message">
                    ⚠️ {error}
                </div>
            ) : (
                <div className="table-responsive">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Certificate ID</th>
                                <th>Student Name</th>
                                <th>Course</th>
                                <th>Year</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {certificates.length > 0 ? (
                                certificates.map((cert) => (
                                    <tr key={cert.certificate_id}>
                                        <td><strong>{cert.certificate_id}</strong></td>
                                        <td>{cert.student_name}</td>
                                        <td>{cert.course}</td>
                                        <td>{cert.year}</td>
                                        <td>
                                            <span className="status-badge status-verified">
                                                Issued ✅
                                            </span>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="empty-state">
                                        No certificates issued yet.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default IssuedCertificates;
