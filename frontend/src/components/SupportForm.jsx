import React, { useState } from 'react';
import { submitSupportForm, getTicketStatus } from '../lib/apiClient';

const SupportForm = () => {
    const [activeTab, setActiveTab] = useState('submit'); // 'submit' or 'status'
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        subject: '',
        category: 'general',
        message: ''
    });
    const [statusInput, setStatusInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [feedback, setFeedback] = useState(null); // { type: 'success' | 'error', message: '', data: any }
    const [ticketStatus, setTicketStatus] = useState(null);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const validateForm = () => {
        if (formData.name.length < 2) return "Name must be at least 2 characters.";
        if (!formData.email.includes('@')) return "Please enter a valid email.";
        if (formData.subject.length < 5) return "Subject must be at least 5 characters.";
        if (formData.message.length < 10) return "Message must be at least 10 characters.";
        return null;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setFeedback(null);

        const error = validateForm();
        if (error) {
            setFeedback({ type: 'error', message: error });
            return;
        }

        setLoading(true);
        try {
            const response = await submitSupportForm(formData);
            setFeedback({
                type: 'success',
                message: `Ticket created successfully! Your Ticket ID is: ${response.ticket_id}`,
                data: response
            });
            setFormData({ name: '', email: '', subject: '', category: 'general', message: '' });
        } catch (err) {
            setFeedback({ type: 'error', message: err.message || "Failed to submit ticket." });
        } finally {
            setLoading(false);
        }
    };

    const handleCheckStatus = async (e) => {
        e.preventDefault();
        if (!statusInput) return;

        setLoading(true);
        setTicketStatus(null);
        setFeedback(null);

        try {
            const data = await getTicketStatus(statusInput);
            setTicketStatus(data);
        } catch (err) {
            setFeedback({ type: 'error', message: err.message || "Failed to retrieve ticket status." });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
            <div className="flex mb-6 border-b">
                <button
                    className={`flex-1 py-2 text-center ${activeTab === 'submit' ? 'border-b-2 border-blue-500 font-bold' : 'text-gray-500'}`}
                    onClick={() => { setActiveTab('submit'); setFeedback(null); }}
                >
                    Submit Ticket
                </button>
                <button
                    className={`flex-1 py-2 text-center ${activeTab === 'status' ? 'border-b-2 border-blue-500 font-bold' : 'text-gray-500'}`}
                    onClick={() => { setActiveTab('status'); setFeedback(null); }}
                >
                    Check Status
                </button>
            </div>

            {feedback && (
                <div className={`p-4 mb-4 rounded ${feedback.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {feedback.message}
                </div>
            )}

            {activeTab === 'submit' && (
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Name</label>
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleInputChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                            placeholder="John Doe"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Email</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleInputChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                            placeholder="john@example.com"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Category</label>
                        <select
                            name="category"
                            value={formData.category}
                            onChange={handleInputChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                        >
                            <option value="general">General Inquiry</option>
                            <option value="technical">Technical Support</option>
                            <option value="billing">Billing</option>
                            <option value="feedback">Feedback</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Subject</label>
                        <input
                            type="text"
                            name="subject"
                            value={formData.subject}
                            onChange={handleInputChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                            placeholder="Brief summary of issue"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Message</label>
                        <textarea
                            name="message"
                            value={formData.message}
                            onChange={handleInputChange}
                            rows="4"
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                            placeholder="Describe your issue..."
                            required
                        ></textarea>
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                        {loading ? 'Submitting...' : 'Submit Ticket'}
                    </button>
                </form>
            )}

            {activeTab === 'status' && (
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Ticket ID</label>
                        <div className="flex mt-1">
                            <input
                                type="text"
                                value={statusInput}
                                onChange={(e) => setStatusInput(e.target.value)}
                                className="flex-1 rounded-l-md border-gray-300 shadow-sm p-2 border"
                                placeholder="Enter Ticket UUID"
                            />
                            <button
                                onClick={handleCheckStatus}
                                disabled={loading}
                                className="py-2 px-4 border border-transparent rounded-r-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
                            >
                                {loading ? 'Check' : 'Check Status'}
                            </button>
                        </div>
                    </div>

                    {ticketStatus && (
                        <div className="mt-4 p-4 border rounded bg-gray-50">
                            <h3 className="font-bold text-lg">Ticket Status: <span className="uppercase text-blue-600">{ticketStatus.status}</span></h3>
                            <p className="text-gray-600">ID: {ticketStatus.ticket_id}</p>

                            <div className="mt-4">
                                <h4 className="font-semibold border-b pb-1 mb-2">Message History</h4>
                                {ticketStatus.messages && ticketStatus.messages.length > 0 ? (
                                    <div className="space-y-3">
                                        {ticketStatus.messages.map((msg, idx) => (
                                            <div key={idx} className={`p-3 rounded ${msg.role === 'customer' ? 'bg-blue-50 ml-8' : 'bg-white border mr-8'}`}>
                                                <p className="text-xs text-gray-500 mb-1 capitalize">{msg.role} - {new Date(msg.created_at).toLocaleString()}</p>
                                                <p>{msg.content}</p>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-gray-500 italic">No messages yet.</p>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default SupportForm;
