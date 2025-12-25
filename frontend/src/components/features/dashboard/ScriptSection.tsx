import React, { useEffect, useState } from 'react';
import { Code, Copy, Download, Check, Loader2, AlertCircle } from 'lucide-react';
import type { Dataset } from '../../../types';
import { datasetService } from '../../../services/api';

interface ScriptSectionProps {
    dataset: Dataset;
}

export const ScriptSection: React.FC<ScriptSectionProps> = ({ dataset }) => {
    const [script, setScript] = useState<string>('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string>('');
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        const fetchScript = async () => {
            try {
                const data = await datasetService.generateScript(dataset.session_id);
                setScript(data);
            } catch (e: any) {
                setError(e?.response?.data?.detail || 'Failed to generate script');
            } finally {
                setLoading(false);
            }
        };
        fetchScript();
    }, [dataset.session_id]);

    const handleCopy = () => {
        navigator.clipboard.writeText(script);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleDownload = () => {
        const blob = new Blob([script], { type: 'text/x-python' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analysis_${dataset.filename.split('.')[0]}.py`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="w-10 h-10 text-purple-600 animate-spin mb-4" />
                <p className="text-gray-600">Generating Python analysis script...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 text-red-600 p-6 rounded-xl flex items-center space-x-3">
                <AlertCircle className="w-6 h-6" />
                <span>{error}</span>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                <div className="bg-gray-900 px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <Code className="w-5 h-5 text-purple-400" />
                        <span className="text-gray-200 font-mono text-sm">analysis.py</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={handleCopy}
                            className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-gray-800"
                            title="Copy to clipboard"
                        >
                            {copied ? <Check className="w-5 h-5 text-green-400" /> : <Copy className="w-5 h-5" />}
                        </button>
                        <button
                            onClick={handleDownload}
                            className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-gray-800"
                            title="Download file"
                        >
                            <Download className="w-5 h-5" />
                        </button>
                    </div>
                </div>
                <div className="p-0 overflow-x-auto">
                    <pre className="text-sm font-mono text-gray-300 bg-gray-900 p-6 m-0 leading-relaxed">
                        <code>{script}</code>
                    </pre>
                </div>
            </div>

            <div className="bg-purple-50 p-6 rounded-xl border border-purple-100">
                <h4 className="font-semibold text-purple-900 mb-2">How to run this script</h4>
                <ol className="list-decimal list-inside text-purple-800 space-y-1 text-sm">
                    <li>Download the script or copy the code</li>
                    <li>Ensure you have Python installed</li>
                    <li>Install required libraries: <code className="bg-purple-100 px-2 py-0.5 rounded text-purple-700">pip install pandas numpy matplotlib seaborn</code></li>
                    <li>Run the script: <code className="bg-purple-100 px-2 py-0.5 rounded text-purple-700">python analysis.py</code></li>
                </ol>
            </div>
        </div>
    );
};
