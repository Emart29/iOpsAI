import React from 'react';
import type { Dataset } from '../types';
import { MLSection } from '../components/features/dashboard/MLSection';

interface MLPageProps {
    dataset: Dataset;
}

export const MLPage: React.FC<MLPageProps> = ({ dataset }) => {
    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">AutoML Training</h2>
            <MLSection dataset={dataset} />
        </div>
    );
};
