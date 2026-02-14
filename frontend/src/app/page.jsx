"use client";

import SupportForm from '../components/SupportForm';

export default function Home() {
    return (
        <main className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto text-center mb-10">
                <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
                    Customer Support
                </h1>
                <p className="mt-4 text-lg text-gray-600">
                    How can we help you today? Submit a ticket or check your status below.
                </p>
            </div>
            <SupportForm />
        </main>
    );
}
