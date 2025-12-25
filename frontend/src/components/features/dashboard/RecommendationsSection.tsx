import React, { useEffect, useState } from 'react';
import { Lightbulb, Loader2, AlertCircle, ArrowRight } from 'lucide-react';
import type { Dataset, Insight } from '../../../types';
import { datasetService } from '../../../services/api';

interface RecommendationsSectionProps {
    dataset: Dataset;
}

export const RecommendationsSection: React.FC<RecommendationsSectionProps> = ({ dataset }) => {
    const [recommendations, setRecommendations] = useState<Insight[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string>('');

    useEffect(() => {
        const fetchRecommendations = async () => {
            try {
                const data = await datasetService.getRecommendations(dataset.session_id);
                setRecommendations(data);
            } catch (e: any) {
                setError(e?.response?.data?.detail || 'Failed to load recommendations');
            } finally {
                setLoading(false);
            }
        };
        fetchRecommendations();
    }, [dataset.session_id]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="w-10 h-10 text-yellow-500 animate-spin mb-4" />
                <p className="text-gray-600">Generating AI recommendations...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 text-red-600 p-6 rounded-xl flex items-center space-x-3">
                <AlertCircle className="w-6 h-6" />
                <span>{error}</span>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-gradient-to-r from-yellow-500 to-orange-500 p-8 rounded-2xl text-white shadow-lg mb-8">
                <div className="flex items-center space-x-4 mb-4">
                    <div className="bg-white/20 p-3 rounded-xl">
                        <Lightbulb className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold">AI Recommendations</h3>
                </div>
                <p className="text-yellow-50 text-lg">
                    Based on your data profile, here are some actionable steps and insights to improve your analysis.
                </p>
            </div>

            <div className="grid gap-6">
                {recommendations.map((rec, idx) => (
                    <div key={idx} className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow border-l-4 border-yellow-500">
                        <div className="flex items-start justify-between">
                            <div>
                                <div className="flex items-center space-x-2 mb-2">
                                    <span className="text-xs font-bold uppercase tracking-wider text-yellow-600 bg-yellow-50 px-2 py-1 rounded">
                                        {rec.category}
                                    </span>
                                </div>
                                <h4 className="text-xl font-bold text-gray-900 mb-2">{rec.title}</h4>
                                <p className="text-gray-600 leading-relaxed">{rec.description}</p>
                            </div>
                            <ArrowRight className="w-5 h-5 text-gray-400 mt-1" />
                        </div>
                    </div>
                ))}

                {recommendations.length === 0 && (
                    <div className="text-center py-10 text-gray-500">
                        No specific recommendations found for this dataset.
                    </div>
                )}
            </div>
        </div>
    );
};
