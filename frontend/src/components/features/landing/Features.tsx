import { Brain, MessageSquare, FileText, Sparkles, Code, BarChart3 } from 'lucide-react';

const features = [
    {
        icon: Brain,
        title: 'AI-Powered Insights',
        description: 'Automatic data analysis and intelligent recommendations powered by advanced AI models.',
        color: 'purple'
    },
    {
        icon: MessageSquare,
        title: 'Sight Chatbot',
        description: 'Conversational AI assistant that answers questions about your data in natural language.',
        color: 'blue'
    },
    {
        icon: FileText,
        title: 'Instant EDA Reports',
        description: 'Professional PDF reports with comprehensive exploratory data analysis in seconds.',
        color: 'pink'
    },
    {
        icon: Sparkles,
        title: 'Smart Data Cleaning',
        description: 'AI-suggested cleaning strategies to prepare your data for analysis automatically.',
        color: 'indigo'
    },
    {
        icon: Code,
        title: 'Python Scripts',
        description: 'Generate reproducible Python code for all your data transformations and analyses.',
        color: 'violet'
    },
    {
        icon: BarChart3,
        title: 'Interactive Charts',
        description: 'Dynamic visualizations that update in real-time as you explore your data.',
        color: 'fuchsia'
    }
];

export const Features = () => {
    return (
        <section id="features" className="py-24 bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
                        Powerful Features for Data Scientists
                    </h2>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                        Everything you need to explore, analyze, and understand your data—all in one intelligent platform.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {features.map((feature, index) => {
                        const Icon = feature.icon;
                        return (
                            <div
                                key={index}
                                className="group relative bg-gradient-to-br from-gray-50 to-white p-8 rounded-2xl border border-gray-200 hover:border-purple-300 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2"
                            >
                                <div className={`inline-flex p-3 bg-${feature.color}-100 text-${feature.color}-600 rounded-xl mb-4 group-hover:scale-110 transition-transform duration-300`}>
                                    <Icon className="w-6 h-6" />
                                </div>
                                <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                            </div>
                        );
                    })}
                </div>
            </div>
        </section>
    );
};
