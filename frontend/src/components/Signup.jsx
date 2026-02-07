import React, { useState } from 'react';

const Signup = ({ role, onSignupSuccess, onSwitchToSignin, onBack }) => {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
    });
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);

    const validateEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
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
            newErrors.email = 'Please enter a valid email address';
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
            // Mock signup - in production, this would call backend API
            // Simulating API call delay
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Store user data in localStorage (mock authentication)
            const userData = {
                email: formData.email,
                role: role,
                createdAt: new Date().toISOString(),
            };

            // Save to localStorage
            const users = JSON.parse(localStorage.getItem('users') || '[]');

            // Check if user already exists
            const existingUser = users.find(u => u.email === formData.email);
            if (existingUser) {
                setErrors({ email: 'User with this email already exists' });
                setLoading(false);
                return;
            }

            users.push({
                ...userData,
                password: formData.password, // In production, this would be hashed
            });
            localStorage.setItem('users', JSON.stringify(users));

            // Success - redirect to signin
            onSignupSuccess(userData);
        } catch (err) {
            setErrors({ general: 'Signup failed. Please try again.' });
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
