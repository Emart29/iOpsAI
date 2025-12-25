import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import type { ChartData, Dataset } from '../../../types';
import { datasetService } from '../../../services/api';

interface ChartsSectionProps {
    dataset: Dataset;
}

export const ChartsSection: React.FC<ChartsSectionProps> = ({ dataset }) => {
    const [chartData, setChartData] = useState<ChartData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string>('');

    useEffect(() => {
        const fetchCharts = async () => {
            setLoading(true);
            try {
                const data = await datasetService.getCharts(dataset.session_id);
                setChartData(data);
            } catch (e: any) {
                setError(e?.response?.data?.detail || 'Failed to load charts');
            } finally {
                setLoading(false);
            }
        };
        fetchCharts();
    }, [dataset.session_id]);

    if (loading) return <div className="text-center py-10">Loading interactive charts...</div>;
    if (error) return <div className="text-red-600 py-10">{error}</div>;
    if (!chartData) return null;

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.entries(chartData).map(([key, chart]) => (
                <div key={key} className="bg-white p-4 rounded-xl shadow-lg overflow-hidden">
                    <Plot
                        data={chart.data}
                        layout={{
                            ...chart.layout,
                            width: undefined, // Let it be responsive
                            height: 400,
                            autosize: true,
                            margin: { l: 50, r: 20, t: 50, b: 50 }
                        }}
                        useResizeHandler={true}
                        style={{ width: '100%', height: '100%' }}
                        config={{ responsive: true, displayModeBar: true }}
                    />
                </div>
            ))}
        </div>
    );
};
