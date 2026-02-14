'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Search, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { submitSupportForm, getTicketStatus } from '../lib/apiClient';
import { cn } from './ui-helpers';

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
    const [feedback, setFeedback] = useState(null);
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
                message: `Ticket created successfully!`,
                ticketId: response.ticket_id
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
        <div className="w-full max-w-2xl mx-auto">
            {/* Tabs */}
            <div className="flex bg-white/5 rounded-2xl p-1 mb-8 backdrop-blur-md border border-white/10">
                {['submit', 'status'].map((tab) => (
                    <button
                        key={tab}
                        onClick={() => { setActiveTab(tab); setFeedback(null); }}
                        className={cn(
                            "flex-1 py-3 px-6 rounded-xl text-sm font-medium transition-all duration-300 relative",
                            activeTab === tab ? "text-white" : "text-gray-400 hover:text-white"
                        )}
                    >
                        {activeTab === tab && (
                            <motion.div
                                layoutId="activeTab"
                                className="absolute inset-0 bg-white/10 rounded-xl shadow-inner"
                                transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                            />
                        )}
                        <span className="relative z-10 flex items-center justify-center gap-2">
                            {tab === 'submit' ? <Send size={16} /> : <Search size={16} />}
                            {tab === 'submit' ? 'New Request' : 'Track Status'}
                        </span>
                    </button>
                ))}
            </div>

            <AnimatePresence mode="wait">
                <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.3 }}
                >
                    {/* Feedback Alert */}
                    <AnimatePresence>
                        {feedback && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className={cn(
                                    "mb-6 p-4 rounded-xl border flex items-start gap-3",
                                    feedback.type === 'success'
                                        ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-200"
                                        : "bg-red-500/10 border-red-500/20 text-red-200"
                                )}
                            >
                                {feedback.type === 'success' ? <CheckCircle2 className="mt-0.5" /> : <AlertCircle className="mt-0.5" />}
                                <div>
                                    <p className="font-medium">{feedback.message}</p>
                                    {feedback.ticketId && (
                                        <p className="text-sm mt-1 opacity-80 font-mono bg-black/20 px-2 py-1 rounded inline-block">
                                            ID: {feedback.ticketId}
                                        </p>
                                    )}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {activeTab === 'submit' ? (
                        <form onSubmit={handleSubmit} className="space-y-5">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-gray-300 ml-1">Name</label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleInputChange}
                                        className="glass-input w-full"
                                        placeholder="John Doe"
                                        required
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-gray-300 ml-1">Email</label>
                                    <input
                                        type="email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleInputChange}
                                        className="glass-input w-full"
                                        placeholder="john@company.com"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-300 ml-1">Category</label>
                                <div className="relative">
                                    <select
                                        name="category"
                                        value={formData.category}
                                        onChange={handleInputChange}
                                        className="glass-input w-full appearance-none pr-10 cursor-pointer"
                                    >
                                        <option value="general" className="text-black">General Inquiry</option>
                                        <option value="technical" className="text-black">Technical Support</option>
                                        <option value="billing" className="text-black">Billing</option>
                                        <option value="feedback" className="text-black">Feedback</option>
                                    </select>
                                    <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                                        <svg width="12" height="8" viewBox="0 0 12 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-300 ml-1">Subject</label>
                                <input
                                    type="text"
                                    name="subject"
                                    value={formData.subject}
                                    onChange={handleInputChange}
                                    className="glass-input w-full"
                                    placeholder="Brief summary of your issue"
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-300 ml-1">Message</label>
                                <textarea
                                    name="message"
                                    value={formData.message}
                                    onChange={handleInputChange}
                                    rows="5"
                                    className="glass-input w-full resize-none"
                                    placeholder="How can we help you today?"
                                    required
                                ></textarea>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="glass-button glass-button-primary w-full flex items-center justify-center gap-2 group"
                            >
                                {loading ? (
                                    <Loader2 className="animate-spin" />
                                ) : (
                                    <>
                                        Submit Request
                                        <Send size={18} className="group-hover:translate-x-1 transition-transform" />
                                    </>
                                )}
                            </button>
                        </form>
                    ) : (
                        <div className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-300 ml-1">Ticket ID</label>
                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        value={statusInput}
                                        onChange={(e) => setStatusInput(e.target.value)}
                                        className="glass-input flex-1"
                                        placeholder="Enter Ticket UUID"
                                    />
                                    <button
                                        onClick={handleCheckStatus}
                                        disabled={loading}
                                        className="glass-button glass-button-primary px-6"
                                    >
                                        {loading ? <Loader2 className="animate-spin" /> : <Search size={20} />}
                                    </button>
                                </div>
                            </div>

                            <AnimatePresence>
                                {ticketStatus && (
                                    <motion.div
                                        initial={{ opacity: 0, scale: 0.95 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4"
                                    >
                                        <div className="flex items-center justify-between border-b border-white/10 pb-4">
                                            <div>
                                                <p className="text-sm text-gray-400">Status</p>
                                                <div className={cn(
                                                    "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider mt-1",
                                                    ticketStatus.status === 'resolved' ? "bg-emerald-500/20 text-emerald-300" :
                                                        ticketStatus.status === 'open' ? "bg-blue-500/20 text-blue-300" :
                                                            "bg-orange-500/20 text-orange-300"
                                                )}>
                                                    <span className="w-1.5 h-1.5 rounded-full bg-current" />
                                                    {ticketStatus.status}
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-sm text-gray-400">Ticket ID</p>
                                                <p className="font-mono text-sm text-white/80">{ticketStatus.ticket_id.slice(0, 8)}...</p>
                                            </div>
                                        </div>

                                        <div className="space-y-3 max-h-80 overflow-y-auto pr-2 custom-scrollbar">
                                            {ticketStatus.messages && ticketStatus.messages.length > 0 ? (
                                                ticketStatus.messages.map((msg, idx) => (
                                                    <motion.div
                                                        key={idx}
                                                        initial={{ opacity: 0, x: msg.role === 'customer' ? 20 : -20 }}
                                                        animate={{ opacity: 1, x: 0 }}
                                                        transition={{ delay: idx * 0.1 }}
                                                        className={cn(
                                                            "p-4 rounded-2xl max-w-[90%] text-sm leading-relaxed",
                                                            msg.role === 'customer'
                                                                ? "bg-blue-600/20 ml-auto rounded-tr-sm border border-blue-500/20"
                                                                : "bg-white/5 mr-auto rounded-tl-sm border border-white/10"
                                                        )}
                                                    >
                                                        <div className="flex items-center gap-2 mb-2 opacity-60 text-xs">
                                                            <span className="capitalize font-semibold">{msg.role}</span>
                                                            <span>•</span>
                                                            <span>{new Date(msg.created_at).toLocaleString()}</span>
                                                        </div>
                                                        <p className="text-white/90 whitespace-pre-wrap">{msg.content}</p>
                                                    </motion.div>
                                                ))
                                            ) : (
                                                <div className="text-center py-8 text-gray-500">
                                                    No messages yet.
                                                </div>
                                            )}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    )}
                </motion.div>
            </AnimatePresence>
        </div>
    );
};

export default SupportForm;
