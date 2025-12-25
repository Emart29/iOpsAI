import React, { useEffect, useState } from 'react';
import type { Insight, Dataset } from '../../../types';
import { datasetService } from '../../../services/api';

interface InsightsSectionProps {
    dataset: Dataset;
}

export const InsightsSection: React.FC<InsightsSectionProps> = ({ dataset }) => {
    const [insights, setInsights] = useState<Insight[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string>('');

    useEffect(() => {
        const fetchInsights = async () => {
            setLoading(true);
            try {
                const data = await datasetService.getInsights(dataset.session_id);
                setInsights(data);
            } catch (e: any) {
                setError(e?.response?.data?.detail || 'Failed to load insights');
            } finally {
                setLoading(false);
            }
        };
        fetchInsights();
    }, [dataset.session_id]);

    if (loading) return <p className="text-gray-600">Loading insights...</p>;
    if (error) return <p className="text-red-600">{error}</p>;

    return (
        <div className="space-y-4">
            {insights.map((insight, idx) => (
                <div key={idx} className="p-4 bg-white rounded-lg shadow">
                    <h3 className="text-lg font-semibold text-purple-600 mb-2">{insight.title}</h3>
                    <p className="text-gray-700">{insight.description}</p>
                </div>
            ))}
        </div>
    );
};
