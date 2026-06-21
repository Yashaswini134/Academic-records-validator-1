import React, { useState } from 'react';
import { universityAPI, verifierAPI } from '../services/api';

const Signup = ({ role, onSignupSuccess, onSwitchToSignin, onBack }) => {
    const [formData, setFormData] = useState({
        email: '',
        universityName: '',
        password: '',
        confirmPassword: '',
    });
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);

    const validateEmail = (email) => {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@gmail\.com$/;
        return emailRegex.test(email);
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
        // Clear error for this field when user starts typing
        setErrors({
            ...errors,
            [e.target.name]: '',
        });
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!validateEmail(formData.email)) {
            newErrors.email = 'Please enter a valid @gmail.com address';
        }

        if (!formData.password) {
            newErrors.password = 'Password is required';
        } else if (formData.password.length < 6) {
            newErrors.password = 'Password must be at least 6 characters';
        }

        if (!formData.confirmPassword) {
            newErrors.confirmPassword = 'Please confirm your password';
        } else if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setLoading(true);

        try {
            // Real signup - call backend API
            const signupApi = role === 'university' ? universityAPI.signup : verifierAPI.signup;
            const result = await signupApi({
                email: formData.email,
                university_name: formData.universityName,
                password: formData.password,
                role: role
            });

            if (result.success) {
                const userData = {
                    email: result.data.email,
                    role: result.data.role,
                    university_name: result.data.university_name,
                    token: result.data.token
                };

                // Success - save to localStorage for persistence
                localStorage.setItem('currentUser', JSON.stringify(userData));

                // Automatically log in
                onSignupSuccess(userData);
            } else {
                setErrors({ general: result.error || 'Signup failed. Please try again.' });
            }
        } catch (err) {
            setErrors({ general: 'Signup failed. Please check your connection.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="auth-container">
                <div className="auth-header">
                    <h2>
                        {role === 'university' ? '🏛️ University Sign Up' : '🔍 Verifier Sign Up'}
                    </h2>
                    <p>Create your account to continue</p>
                    <div className="role-badge">
                        Role: {role === 'university' ? 'University' : 'Verifier'}
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                    {role === 'university' && (
                        <div className="form-group">
                            <label htmlFor="universityName">
                                University Name <span className="required">*</span>
                            </label>
                            <input
                                type="text"
                                id="universityName"
                                name="universityName"
                                value={formData.universityName}
                                onChange={handleChange}
                                placeholder="Enter University Name (e.g. JNTUH)"
                                disabled={loading}
                            />
                        </div>
                    )}
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
                            className={errors.email ? 'error' : ''}
                        />
                        {errors.email && (
                            <span className="error-text">{errors.email}</span>
                        )}
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
                            placeholder="Enter your password (min 6 characters)"
                            disabled={loading}
                            className={errors.password ? 'error' : ''}
                        />
                        {errors.password && (
                            <span className="error-text">{errors.password}</span>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirmPassword">
                            Confirm Password <span className="required">*</span>
                        </label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            placeholder="Re-enter your password"
                            disabled={loading}
                            className={errors.confirmPassword ? 'error' : ''}
                        />
                        {errors.confirmPassword && (
                            <span className="error-text">{errors.confirmPassword}</span>
                        )}
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
                            {loading ? 'Creating Account...' : 'Sign Up'}
                        </button>
                    </div>
                </form>

                <div className="auth-footer">
                    <p>
                        Already have an account?{' '}
                        <button
                            className="link-button"
                            onClick={onSwitchToSignin}
                            disabled={loading}
                        >
                            Sign In
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Signup;
