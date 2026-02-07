import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import RoleSelection from './components/RoleSelection';
import Signup from './components/Signup';
import Signin from './components/Signin';
import UniversityUpload from './components/UniversityUpload';
import UniversityReview from './components/UniversityReview';
import UniversitySuccess from './components/UniversitySuccess';
import VerifierUpload from './components/VerifierUpload';
import VerificationResult from './components/VerificationResult';

function App() {
    const [currentRole, setCurrentRole] = useState(null);
    const [authStep, setAuthStep] = useState(null); // 'signup' or 'signin'
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [userData, setUserData] = useState(null);
    const [universityStep, setUniversityStep] = useState('upload');
    const [extractedData, setExtractedData] = useState(null);
    const [confirmationData, setConfirmationData] = useState(null);
    const [verifierStep, setVerifierStep] = useState('upload');
    const [verificationData, setVerificationData] = useState(null);

    // Set document title
    useEffect(() => {
        document.title = 'Academic Records Validator';
    }, []);

    const handleRoleSelection = (role) => {
        setCurrentRole(role);
        setAuthStep('signup'); // Default to signup for new users
    };

    const handleSignupSuccess = (data) => {
        // After successful signup, redirect to signin
        setAuthStep('signin');
    };

    const handleSigninSuccess = (data) => {
        setUserData(data);
        setIsLoggedIn(true);
        setAuthStep(null);
    };

    const handleSwitchToSignin = () => {
        setAuthStep('signin');
    };

    const handleSwitchToSignup = () => {
        setAuthStep('signup');
    };

    const handleLogout = () => {
        setCurrentRole(null);
        setAuthStep(null);
        setIsLoggedIn(false);
        setUserData(null);
        setUniversityStep('upload');
        setExtractedData(null);
        setConfirmationData(null);
        setVerifierStep('upload');
        setVerificationData(null);
        localStorage.removeItem('currentUser');
    };

    const handleBackToRoleSelection = () => {
        setCurrentRole(null);
        setAuthStep(null);
    };

    const handleUploadSuccess = (data) => {
        setExtractedData(data);
        setUniversityStep('review');
    };

    const handleConfirmSuccess = (data) => {
        setConfirmationData(data);
        setUniversityStep('success');
    };

    const handleNewCertificate = () => {
        setUniversityStep('upload');
        setExtractedData(null);
        setConfirmationData(null);
    };

    const handleBackToUpload = () => {
        setUniversityStep('upload');
        setExtractedData(null);
    };

    const handleVerificationSuccess = (data) => {
        setVerificationData(data);
        setVerifierStep('result');
    };

    const handleNewVerification = () => {
        setVerifierStep('upload');
        setVerificationData(null);
    };

    const renderContent = () => {
        // Step 1: Role Selection
        if (!currentRole) {
            return <RoleSelection onSelectRole={handleRoleSelection} />;
        }

        // Step 2: Authentication (Signup or Signin)
        if (!isLoggedIn) {
            if (authStep === 'signup') {
                return (
                    <Signup
                        role={currentRole}
                        onSignupSuccess={handleSignupSuccess}
                        onSwitchToSignin={handleSwitchToSignin}
                        onBack={handleBackToRoleSelection}
                    />
                );
            }
            if (authStep === 'signin') {
                return (
                    <Signin
                        role={currentRole}
                        onSigninSuccess={handleSigninSuccess}
                        onSwitchToSignup={handleSwitchToSignup}
                        onBack={handleBackToRoleSelection}
                    />
                );
            }
        }

        // Step 3: Dashboard (University or Verifier)
        if (currentRole === 'university') {
            if (universityStep === 'upload') {
                return <UniversityUpload onUploadSuccess={handleUploadSuccess} />;
            }
            if (universityStep === 'review') {
                return (
                    <UniversityReview
                        extractedData={extractedData}
                        onConfirmSuccess={handleConfirmSuccess}
                        onBack={handleBackToUpload}
                    />
                );
            }
            if (universityStep === 'success') {
                return (
                    <UniversitySuccess
                        confirmationData={confirmationData}
                        onNewCertificate={handleNewCertificate}
                    />
                );
            }
        }

        if (currentRole === 'verifier') {
            if (verifierStep === 'upload') {
                return <VerifierUpload onVerificationSuccess={handleVerificationSuccess} />;
            }
            if (verifierStep === 'result') {
                return (
                    <VerificationResult
                        verificationData={verificationData}
                        onNewVerification={handleNewVerification}
                    />
                );
            }
        }

        return <RoleSelection onSelectRole={handleRoleSelection} />;
    };

    return (
        <div className="App">
            <Navbar role={currentRole} onLogout={isLoggedIn ? handleLogout : null} />
            <main className="main-content">{renderContent()}</main>
            <footer className="footer">
                <p>© 2026 Academic Records Validator | Powered by AI & Blockchain</p>
            </footer>
        </div>
    );
}

export default App;
