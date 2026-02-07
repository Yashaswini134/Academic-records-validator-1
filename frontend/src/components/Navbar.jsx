import React from 'react';

const Navbar = ({ role, onLogout }) => {
    return (
        <nav className="navbar">
            <div className="navbar-container">
                <div className="navbar-brand">
                    <h2>🎓 BlockCert</h2>
                </div>
                <div className="navbar-menu">
                    {role && (
                        <>
                            <span className="navbar-role">
                                {role === 'university' ? '🏛️ University' : '🔍 Verifier'}
                            </span>
                            <button className="btn-logout" onClick={onLogout}>
                                Logout
                            </button>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
