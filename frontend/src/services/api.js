import axios from 'axios';

// Base URL for backend API
const BASE_URL = 'http://localhost:5000';

// Create axios instance with default config
const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// University APIs
export const universityAPI = {
    // Login university
    login: async (credentials) => {
        try {
            const response = await api.post('/university/login', credentials);
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Login failed'
            };
        }
    },

    // Upload certificate for OCR extraction
    uploadCertificate: async (formData) => {
        try {
            const response = await api.post('/university/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Upload failed'
            };
        }
    },

    // Confirm certificate details and generate hash
    confirmCertificate: async (certificateData) => {
        try {
            const response = await api.post('/university/confirm', certificateData);
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Confirmation failed'
            };
        }
    },
};

// Verifier APIs
export const verifierAPI = {
    // Login verifier
    login: async (credentials) => {
        try {
            const response = await api.post('/verifier/login', credentials);
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Login failed'
            };
        }
    },

    // Verify certificate by upload
    verifyCertificate: async (formData) => {
        try {
            const response = await api.post('/verifier/verify', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Verification failed'
            };
        }
    },

    // Verify certificate by ID
    verifyCertificateById: async (certificateId) => {
        try {
            const response = await api.post('/verifier/verify-by-id', {
                certificate_id: certificateId
            });
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Verification failed'
            };
        }
    },
};

export default api;
