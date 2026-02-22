import axios from 'axios';

// Base URL for backend API
const BASE_URL = 'http://localhost:5000';

// Create axios instance with default config
const api = axios.create({
    baseURL: BASE_URL,
    withCredentials: true, // Enable sending cookies (sessions)
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

    // Get list of issued certificates
    getIssuedCertificates: async () => {
        try {
            const response = await api.get('/university/issued');
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Failed to fetch issued certificates'
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

    // Step 1: Upload certificate for verifier (OCR + basic data)
    uploadCertificate: async (formData) => {
        try {
            const response = await api.post('/verifier/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Upload failed',
                data: error.response?.data
            };
        }
    },

    // Step 2: AI-based forgery detection (CNN) on uploaded file
    runAiDetection: async (filename) => {
        try {
            const response = await api.post('/verifier/ai-detect', { filename });
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'AI detection failed'
            };
        }
    },

    // Step 3: Generate SHA-256 hash for uploaded file
    generateHash: async (filename) => {
        try {
            const response = await api.post('/verifier/generate-hash', { filename });
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Hash generation failed'
            };
        }
    },

    // Step 4: Verify generated hash against blockchain
    blockchainVerify: async (certificateId, generatedHash) => {
        try {
            const response = await api.post('/verifier/blockchain-verify', {
                certificate_id: certificateId,
                generated_hash: generatedHash,
            });
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Blockchain verification failed'
            };
        }
    },
};

export default api;
