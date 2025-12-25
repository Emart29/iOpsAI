import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';
import { useTheme } from '../../contexts/ThemeContext';
import { ChartSkeleton } from '../ui/Skeleton';

interface PlotlyChartProps {
    data: any[];
    layout?: any;
    config?: any;
    isLoading?: boolean;
    title?: string;
    height?: number | string;
}

export const PlotlyChart: React.FC<PlotlyChartProps> = ({
    data,
    layout = {},
    config = {},
    isLoading = false,
    title,
    height = 450
}) => {
    const { theme } = useTheme();

    const chartTheme = useMemo(() => {
        const isDark = theme === 'dark';

        return {
            paper_bgcolor: isDark ? '#1f2937' : '#ffffff',
            plot_bgcolor: isDark ? '#1f2937' : '#ffffff',
            font: {
                color: isDark ? '#e5e7eb' : '#374151',
                family: 'Inter, sans-serif'
            },
            xaxis: {
                gridcolor: isDark ? '#374151' : '#e5e7eb',
                zerolinecolor: isDark ? '#374151' : '#e5e7eb',
            },
            yaxis: {
                gridcolor: isDark ? '#374151' : '#e5e7eb',
                zerolinecolor: isDark ? '#374151' : '#e5e7eb',
            },
            margin: { t: 40, r: 20, l: 50, b: 40 },
        };
    }, [theme]);

    if (isLoading) {
        return <ChartSkeleton />;
    }

    return (
        <div className="w-full bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 transition-colors duration-200">
            {title && (
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    {title}
                </h3>
            )}
            <Plot
                data={data}
                layout={{
                    ...chartTheme,
                    ...layout,
                    autosize: true,
                    height: typeof height === 'number' ? height : undefined,
                }}
                config={{
                    responsive: true,
                    displayModeBar: true,
                    displaylogo: false,
                    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
                    ...config
                }}
                style={{ width: '100%', height: height }}
                useResizeHandler={true}
                className="w-full"
            />
        </div>
    );
};
