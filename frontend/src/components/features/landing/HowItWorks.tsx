import { Upload, Brain, MessageSquare, Download } from 'lucide-react';

const steps = [
    {
        icon: Upload,
        title: 'Upload CSV',
        description: 'Drag and drop your dataset or browse to upload. We support files up to 50MB.',
        step: '01'
    },
    {
        icon: Brain,
        title: 'AI Analyzes',
        description: 'Our AI automatically profiles your data, detects patterns, and identifies insights.',
        step: '02'
    },
    {
        icon: MessageSquare,
        title: 'Chat with Sight',
        description: 'Ask questions about your data in natural language and get instant answers.',
        step: '03'
    },
    {
        icon: Download,
        title: 'Download Insights',
        description: 'Export comprehensive reports, cleaned data, and Python scripts.',
        step: '04'
    }
];

export const HowItWorks = () => {
    return (
        <section id="how-it-works" className="py-24 bg-gradient-to-br from-purple-50 to-blue-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
                        How It Works
                    </h2>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                        Get from raw data to actionable insights in four simple steps
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {steps.map((step, index) => {
                        const Icon = step.icon;
                        return (
                            <div key={index} className="relative">
                                {/* Connector line */}
                                {index < steps.length - 1 && (
                                    <div className="hidden lg:block absolute top-16 left-full w-full h-0.5 bg-gradient-to-r from-purple-300 to-blue-300 -z-10" />
                                )}

                                <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow duration-300">
                                    <div className="relative mb-6">
                                        <div className="absolute -top-4 -right-4 text-6xl font-bold text-purple-100">
                                            {step.step}
                                        </div>
                                        <div className="relative inline-flex p-4 bg-gradient-to-br from-purple-500 to-blue-500 text-white rounded-xl">
                                            <Icon className="w-8 h-8" />
                                        </div>
                                    </div>
                                    <h3 className="text-xl font-bold text-gray-900 mb-3">{step.title}</h3>
                                    <p className="text-gray-600 leading-relaxed">{step.description}</p>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </section>
    );
};
