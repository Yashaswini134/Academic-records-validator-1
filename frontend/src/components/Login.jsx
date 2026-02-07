import React, { useState } from 'react';
import { universityAPI, verifierAPI } from '../services/api';

const Login = ({ role, onLoginSuccess, onBack }) => {
    const [credentials, setCredentials] = useState({
        userId: '',
        password: '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setCredentials({
            ...credentials,
            [e.target.name]: e.target.value,
        });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!credentials.userId || !credentials.password) {
            setError('Please enter both User ID and Password');
            return;
        }

        setLoading(true);

        try {
            const api = role === 'university' ? universityAPI : verifierAPI;
            const result = await api.login(credentials);

            if (result.success) {
                onLoginSuccess(result.data);
            } else {
                setError(result.error);
            }
        } catch (err) {
            setError('Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="login-container">
                <div className="login-header">
                    <h2>
                        {role === 'university' ? '🏛️ University Login' : '🔍 Verifier Login'}
                    </h2>
                    <p>Enter your credentials to continue</p>
                </div>

                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label htmlFor="userId">
                            {role === 'university' ? 'University ID' : 'Verifier ID'}
                        </label>
                        <input
                            type="text"
                            id="userId"
                            name="userId"
                            value={credentials.userId}
                            onChange={handleChange}
                            placeholder={`Enter your ${role === 'university' ? 'university' : 'verifier'} ID`}
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={credentials.password}
                            onChange={handleChange}
                            placeholder="Enter your password"
                            disabled={loading}
                        />
                    </div>

                    {error && (
                        <div className="error-message">
                            ⚠️ {error}
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
                            {loading ? 'Logging in...' : 'Login'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Login;
