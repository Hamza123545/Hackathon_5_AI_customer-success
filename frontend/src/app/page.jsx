'use client';

import SupportForm from '../components/SupportForm';

export default function Home() {
    return (
        <main className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
            <div className="w-full max-w-4xl text-center mb-10">
                <h1 className="text-4xl font-extrabold text-blue-700 tracking-tight sm:text-5xl mb-4">
                    Customer Success AI Support
                </h1>
                <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
                    Experience 24/7 instant support powered by our advanced AI Digital Employee.
                    Submit a ticket or check your status below.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left mb-12 max-w-3xl mx-auto">
                    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
                        <h3 className="font-bold text-blue-600 mb-2">⚡ Instant Answers</h3>
                        <p className="text-sm text-gray-500">Our AI agent searches our knowledge base to solve your problems in seconds.</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
                        <h3 className="font-bold text-blue-600 mb-2">🔄 Multi-Channel</h3>
                        <p className="text-sm text-gray-500">Start on Web, continue on WhatsApp or Email. We remember context everywhere.</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
                        <h3 className="font-bold text-blue-600 mb-2">🛡️ Reliable</h3>
                        <p className="text-sm text-gray-500">Built on resilient infrastructure to ensure we are always online for you.</p>
                    </div>
                </div>
            </div>

            <div className="w-full max-w-2xl bg-white rounded-xl shadow-xl overflow-hidden border border-gray-200">
                <SupportForm />
            </div>

            <footer className="mt-12 text-center text-gray-400 text-sm">
                <p>&copy; {new Date().getFullYear()} Customer Success FTE. Powered by OpenAI Agents SDK & Gemini.</p>
            </footer>
        </main>
    );
}
