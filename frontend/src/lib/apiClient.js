import axios from 'axios';

const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000, // 10 seconds
});

// Request interceptor
apiClient.interceptors.request.use(
    (config) => {
        // You can add auth tokens here if needed in the future
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // Standardize error format
        const errorResponse = {
            message: 'An unexpected error occurred',
            code: 'UNKNOWN_ERROR',
            status: error.response ? error.response.status : 500,
        };

        if (error.response && error.response.data) {
            errorResponse.message = error.response.data.message || errorResponse.message;
            errorResponse.code = error.response.data.code || errorResponse.code;
        } else if (error.request) {
            errorResponse.message = 'No response received from server. Please check your internet connection.';
            errorResponse.code = 'NETWORK_ERROR';
        } else {
            errorResponse.message = error.message;
        }

        return Promise.reject(errorResponse);
    }
);

export const submitSupportForm = async (formData) => {
    try {
        const response = await apiClient.post('/support/submit', formData);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getTicketStatus = async (ticketId) => {
    try {
        const response = await apiClient.get(`/support/ticket/${ticketId}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export default apiClient;
