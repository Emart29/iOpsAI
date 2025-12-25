import React from 'react';
import type { Dataset } from '../types';
import { ReportSection } from '../components/features/dashboard/ReportSection';

interface ReportPageProps {
    dataset: Dataset;
}

export const ReportPage: React.FC<ReportPageProps> = ({ dataset }) => {
    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">EDA Report</h2>
            <ReportSection dataset={dataset} />
        </div>
    );
};
