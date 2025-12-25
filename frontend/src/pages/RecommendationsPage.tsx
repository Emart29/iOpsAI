import React from 'react';
import type { Dataset } from '../types';
import { RecommendationsSection } from '../components/features/dashboard/RecommendationsSection';

interface RecommendationsPageProps {
    dataset: Dataset;
}

export const RecommendationsPage: React.FC<RecommendationsPageProps> = ({ dataset }) => {
    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">Smart Recommendations</h2>
            <RecommendationsSection dataset={dataset} />
        </div>
    );
};
