import React from 'react';

const Navbar = ({ role, userData, onLogout }) => {
    return (
        <nav className="navbar">
            <div className="navbar-container">
                <div className="navbar-brand">
                    <h2>🎓 Academic Validator</h2>
                </div>
                <div className="navbar-menu">
                    {role && (
                        <>
                            {userData && (
                                <span className="navbar-user">
                                    👤 {userData.email}
                                </span>
                            )}
                            <span className="navbar-role">
                                {role === 'university' ? '🏛️ University' : '🔍 Verifier'}
                            </span>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
