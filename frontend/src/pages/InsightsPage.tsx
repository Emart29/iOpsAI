import React from 'react';
import type { Dataset } from '../types';
import { InsightsSection } from '../components/features/dashboard/InsightsSection';

interface InsightsPageProps {
    dataset: Dataset;
}

export const InsightsPage: React.FC<InsightsPageProps> = ({ dataset }) => {
    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">AI Insights</h2>
            <InsightsSection dataset={dataset} />
        </div>
    );
};
