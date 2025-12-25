import React from 'react';
import type { Dataset } from '../types';
import { CleanSection } from '../components/features/dashboard/CleanSection';

interface CleanPageProps {
    dataset: Dataset;
}

export const CleanPage: React.FC<CleanPageProps> = ({ dataset }) => {
    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">Data Cleaning</h2>
            <CleanSection dataset={dataset} />
        </div>
    );
};
