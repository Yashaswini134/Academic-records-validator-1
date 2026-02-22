import React, { useState } from 'react';
import { universityAPI, verifierAPI } from '../services/api';

const Signin = ({ role, onSigninSuccess, onSwitchToSignup, onBack }) => {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
    });
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
        // Clear errors when user starts typing
        setErrors({});
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.email || !formData.password) {
            setErrors({ general: 'Please enter both email and password' });
            return;
        }

        setLoading(true);

        try {
            // Real signin - call backend API
            const apiCall = role === 'university' ? universityAPI.login : verifierAPI.login;
            const result = await apiCall({
                role: role,
                email: formData.email,
                password: formData.password
            });

            if (result.success) {
                // Store user data in localStorage (for persistent state between refreshes)
                const user = {
                    email: formData.email,
                    role: role,
                    university_name: result.data.university_name || formData.email
                };
                localStorage.setItem('currentUser', JSON.stringify(user));

                // Success - redirect to dashboard
                onSigninSuccess(user);
            } else {
                setErrors({ general: result.error || 'Invalid email or password' });
            }
        } catch (err) {
            setErrors({ general: 'Sign in failed. Please try again.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="auth-container">
                <div className="auth-header">
                    <h2>
                        {role === 'university' ? '🏛️ University Sign In' : '🔍 Verifier Sign In'}
                    </h2>
                    <p>Sign in to access your dashboard</p>
                    <div className="role-badge">
                        Role: {role === 'university' ? 'University' : 'Verifier'}
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label htmlFor="email">
                            Email Address <span className="required">*</span>
                        </label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="Enter your email"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">
                            Password <span className="required">*</span>
                        </label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="Enter your password"
                            disabled={loading}
                        />
                    </div>

                    {errors.general && (
                        <div className="error-message">
                            ⚠️ {errors.general}
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
                            type="submit"
                            className="btn-primary"
                            disabled={loading}
                        >
                            {loading ? 'Signing In...' : 'Sign In'}
                        </button>
                    </div>
                </form>

                <div className="auth-footer">
                    <p>
                        Don't have an account?{' '}
                        <button
                            className="link-button"
                            onClick={onSwitchToSignup}
                            disabled={loading}
                        >
                            Sign Up
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Signin;
