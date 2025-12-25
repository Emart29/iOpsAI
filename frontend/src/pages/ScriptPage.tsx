import React from 'react';
import type { Dataset } from '../types';
import { ScriptSection } from '../components/features/dashboard/ScriptSection';

interface ScriptPageProps {
    dataset: Dataset;
}

export const ScriptPage: React.FC<ScriptPageProps> = ({ dataset }) => {
    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">Python Analysis Script</h2>
            <ScriptSection dataset={dataset} />
        </div>
    );
};
