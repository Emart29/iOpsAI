import React from 'react';
import { ExperimentsSection } from '../components/features/dashboard/ExperimentsSection';

export const ExperimentsPage: React.FC = () => {
    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">Experiment History</h2>
            <ExperimentsSection />
        </div>
    );
};
