
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
                <h2>Registered Certificates</h2>
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
                                <th>Student Name</th>
                                <th>Primary Certificate ID</th>
                                <th>Highest Qualification</th>
                                <th>Year</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(() => {
                                // Group certificates by their combined hash
                                const groups = certificates.reduce((acc, cert) => {
                                    const key = cert.hash || cert.student_name;
                                    if (!acc[key]) {
                                        acc[key] = { ...cert, all_certs: [cert] };
                                    } else {
                                        acc[key].all_certs.push(cert);
                                        // Prioritize Degree over others for display
                                        if (cert.course && (cert.course.toUpperCase().includes('BACHELOR') || cert.course.toUpperCase().includes('DEGREE'))) {
                                            acc[key].course = cert.course;
                                            acc[key].year = cert.year;
                                            acc[key].certificate_id = cert.certificate_id;
                                        }
                                    }
                                    return acc;
                                }, {});

                                const displayCerts = Object.values(groups);

                                if (displayCerts.length > 0) {
                                    return displayCerts.map((cert) => (
                                        <tr key={cert.hash || cert.certificate_id}>
                                            <td><strong>{cert.student_name}</strong></td>
                                            <td><code>{cert.certificate_id}</code></td>
                                            <td>{cert.course}</td>
                                            <td>{cert.year}</td>
                                            <td>
                                                <div className="status-badge status-verified" style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                                                    <span>Issued</span>
                                                    <span style={{ fontSize: '0.8rem' }}>✅</span>
                                                </div>
                                            </td>
                                        </tr>
                                    ));
                                } else {
                                    return (
                                        <tr>
                                            <td colSpan="5" className="empty-state">
                                                No certificates issued yet.
                                            </td>
                                        </tr>
                                    );
                                }
                            })()}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default IssuedCertificates;
