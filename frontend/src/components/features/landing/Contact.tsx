import { useState } from 'react';
import { Mail, Send } from 'lucide-react';

export const Contact = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        message: ''
    });
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Frontend validation only for MVP
        if (formData.name && formData.email && formData.message) {
            setSubmitted(true);
            setTimeout(() => {
                setSubmitted(false);
                setFormData({ name: '', email: '', message: '' });
            }, 3000);
        }
    };

    return (
        <section id="contact" className="py-24 bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="max-w-3xl mx-auto">
                    <div className="text-center mb-12">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 text-purple-600 rounded-full mb-4">
                            <Mail className="w-8 h-8" />
                        </div>
                        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
                            Get In Touch
                        </h2>
                        <p className="text-xl text-gray-600">
                            Have questions? We'd love to hear from you.
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="bg-gradient-to-br from-gray-50 to-white p-8 rounded-2xl shadow-lg border border-gray-200">
                        <div className="mb-6">
                            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                                Name
                            </label>
                            <input
                                type="text"
                                id="name"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                placeholder="Your name"
                                required
                            />
                        </div>

                        <div className="mb-6">
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                                Email
                            </label>
                            <input
                                type="email"
                                id="email"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                placeholder="your@email.com"
                                required
                            />
                        </div>

                        <div className="mb-6">
                            <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                                Message
                            </label>
                            <textarea
                                id="message"
                                value={formData.message}
                                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                                rows={5}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none"
                                placeholder="Tell us what you're thinking..."
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-4 rounded-lg font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200 flex items-center justify-center"
                        >
                            {submitted ? (
                                <>
                                    <span className="mr-2">✓</span> Message Sent!
                                </>
                            ) : (
                                <>
                                    <Send className="w-5 h-5 mr-2" />
                                    Send Message
                                </>
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </section>
    );
};
