import React from 'react';
import type { Dataset } from '../types';
import { ChartsSection } from '../components/features/dashboard/ChartsSection';

interface ChartsPageProps {
    dataset: Dataset;
}

export const ChartsPage: React.FC<ChartsPageProps> = ({ dataset }) => {
    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">Data Visualizations</h2>
            <ChartsSection dataset={dataset} />
        </div>
    );
};
