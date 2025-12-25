import React, { useState } from 'react';
import { FileDown, Loader2, FileText, CheckCircle } from 'lucide-react';
import type { Dataset } from '../../../types';
import { datasetService } from '../../../services/api';

interface ReportSectionProps {
    dataset: Dataset;
}

export const ReportSection: React.FC<ReportSectionProps> = ({ dataset }) => {
    const [loading, setLoading] = useState(false);
    const [downloadUrl, setDownloadUrl] = useState<string>('');
    const [error, setError] = useState<string>('');

    const handleGenerateReport = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await datasetService.generateReport(dataset.session_id);
            setDownloadUrl(response.download_url);
        } catch (e: any) {
            setError(e?.response?.data?.detail || 'Failed to generate report');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-xl shadow-lg p-8 text-center">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <FileText className="w-8 h-8 text-purple-600" />
                </div>

                <h3 className="text-2xl font-bold text-gray-900 mb-2">Generate EDA Report</h3>
                <p className="text-gray-600 mb-8">
                    Create a comprehensive PDF report containing data profile, insights, and visualizations for {dataset.filename}.
                </p>

                {error && (
                    <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 text-sm">
                        {error}
                    </div>
                )}

                {!downloadUrl ? (
                    <button
                        onClick={handleGenerateReport}
                        disabled={loading}
                        className="inline-flex items-center space-x-2 bg-purple-600 text-white px-8 py-3 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 font-semibold"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                <span>Generating Report...</span>
                            </>
                        ) : (
                            <>
                                <FileText className="w-5 h-5" />
                                <span>Generate PDF Report</span>
                            </>
                        )}
                    </button>
                ) : (
                    <div className="space-y-4">
                        <div className="flex items-center justify-center space-x-2 text-green-600 mb-4">
                            <CheckCircle className="w-6 h-6" />
                            <span className="font-medium">Report generated successfully!</span>
                        </div>
                        <a
                            href={`${import.meta.env.VITE_API_URL}${downloadUrl}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center space-x-2 bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 transition-colors font-semibold"
                        >
                            <FileDown className="w-5 h-5" />
                            <span>Download Report</span>
                        </a>
                        <button
                            onClick={() => setDownloadUrl('')}
                            className="block w-full text-sm text-gray-500 hover:text-gray-700 mt-4"
                        >
                            Generate another report
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};
