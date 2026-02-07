import React from 'react';

const RoleSelection = ({ onSelectRole }) => {
    return (
        <div className="container">
            <div className="role-selection">
                <h1>Academic Records Validator</h1>
                <p className="subtitle">Select your role to continue</p>

                <div className="role-cards">
                    <div className="role-card" onClick={() => onSelectRole('university')}>
                        <div className="role-icon">🏛️</div>
                        <h3>University</h3>
                        <p>Upload and register certificates</p>
                        <button className="btn-primary">Continue as University</button>
                    </div>

                    <div className="role-card" onClick={() => onSelectRole('verifier')}>
                        <div className="role-icon">🔍</div>
                        <h3>Verifier</h3>
                        <p>Verify certificate authenticity</p>
                        <button className="btn-primary">Continue as Verifier</button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RoleSelection;
