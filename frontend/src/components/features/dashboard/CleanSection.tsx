import React, { useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import {
    Droplet, CheckCircle, Download, Loader2, AlertCircle, Table,
    Undo, Redo, Save, Settings, Package, Play
} from 'lucide-react';
import type { Dataset, CleaningOperation } from '../../../types';
import { datasetService } from '../../../services/api';

interface CleanSectionProps {
    dataset: Dataset;
}

const AVAILABLE_OPERATIONS: CleaningOperation[] = [
    {
        id: 'fill_numeric_mean',
        label: 'Fill Missing Numeric Values',
        description: 'Replace missing values in numeric columns with the mean value.'
    },
    {
        id: 'remove_duplicates',
        label: 'Remove Duplicates',
        description: 'Remove duplicate rows from the dataset.'
    },
    {
        id: 'drop_high_missing',
        label: 'Drop High Missing Columns',
        description: 'Remove columns with more than 50% missing values.'
    }
];

const TRANSFORMATIONS = [
    { id: 'convert_type', label: 'Convert Data Type', icon: '🔄' },
    { id: 'normalize_text', label: 'Normalize Text', icon: '📝' },
    { id: 'remove_outliers', label: 'Remove Outliers', icon: '📊' },
    { id: 'fill_custom', label: 'Fill Custom Value', icon: '✏️' },
    { id: 'create_bins', label: 'Create Bins', icon: '📦' },
];

export const CleanSection: React.FC<CleanSectionProps> = ({ dataset }) => {
    const [selectedOps, setSelectedOps] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<{ download_url: string; summary: string } | null>(null);
    const [error, setError] = useState<string>('');
    const [showGrid, setShowGrid] = useState(false);
    const [showTransforms, setShowTransforms] = useState(false);
    const [showPipelines, setShowPipelines] = useState(false);
    const [gridData, setGridData] = useState<any[]>([]);
    const [columnDefs, setColumnDefs] = useState<any[]>([]);
    const [history, setHistory] = useState<any[][]>([]);
    const [historyIndex, setHistoryIndex] = useState(-1);
    const [pipelines, setPipelines] = useState<any[]>([]);
    const [pipelineName, setPipelineName] = useState('');

    useEffect(() => {
        if (showGrid) {
            fetchGridData();
        }
    }, [showGrid, dataset.session_id]);

    useEffect(() => {
        if (showPipelines) {
            fetchPipelines();
        }
    }, [showPipelines, dataset.session_id]);

    const fetchGridData = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/data-preview/${dataset.session_id}`);
            const data = await response.json();

            if (data.rows && data.rows.length > 0) {
                const cols = Object.keys(data.rows[0]).map(key => ({
                    field: key,
                    editable: true,
                    sortable: true,
                    filter: true,
                    resizable: true,
                }));
                setColumnDefs(cols);
                setGridData(data.rows);
                setHistory([data.rows]);
                setHistoryIndex(0);
            }
        } catch (e) {
            console.error('Failed to fetch grid data:', e);
        }
    };

    const fetchPipelines = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/pipeline/list/${dataset.session_id}`);
            const data = await response.json();
            setPipelines(data.pipelines || []);
        } catch (e) {
            console.error('Failed to fetch pipelines:', e);
        }
    };

    const toggleOperation = (id: string) => {
        setSelectedOps(prev =>
            prev.includes(id) ? prev.filter(op => op !== id) : [...prev, id]
        );
    };

    const handleClean = async () => {
        if (selectedOps.length === 0) return;
        setLoading(true);
        setError('');
        setResult(null);

        try {
            const data = await datasetService.cleanData(dataset.session_id, selectedOps);
            setResult(data);
            if (showGrid) {
                fetchGridData();
            }
        } catch (e: any) {
            setError(e?.response?.data?.detail || 'Failed to clean data');
        } finally {
            setLoading(false);
        }
    };

    const handleCellValueChanged = () => {
        const newData = [...gridData];
        const newHistory = history.slice(0, historyIndex + 1);
        newHistory.push(newData);
        setHistory(newHistory);
        setHistoryIndex(newHistory.length - 1);
    };

    const handleUndo = () => {
        if (historyIndex > 0) {
            setHistoryIndex(historyIndex - 1);
            setGridData(history[historyIndex - 1]);
        }
    };

    const handleRedo = () => {
        if (historyIndex < history.length - 1) {
            setHistoryIndex(historyIndex + 1);
            setGridData(history[historyIndex + 1]);
        }
    };

    const handleSaveChanges = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/data-update/${dataset.session_id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rows: gridData })
            });
            const data = await response.json();
            setResult({
                download_url: data.download_url,
                summary: `Manual edits saved! ${data.rows_updated} rows updated.`
            });
        } catch (e) {
            setError('Failed to save changes');
        }
    };

    const handleSavePipeline = async () => {
        if (!pipelineName.trim()) {
            alert('Please enter a pipeline name');
            return;
        }

        try {
            const steps = selectedOps.map(op => ({ type: op }));
            await fetch(`${import.meta.env.VITE_API_URL}/api/pipeline/save/${dataset.session_id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: pipelineName, steps })
            });
            alert('Pipeline saved successfully!');
            setPipelineName('');
            fetchPipelines();
        } catch (e) {
            alert('Failed to save pipeline');
        }
    };

    const handleApplyPipeline = async (pipelineFile: string) => {
        try {
            setLoading(true);
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/pipeline/apply/${dataset.session_id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pipeline_file: pipelineFile })
            });
            const data = await response.json();
            setResult({
                download_url: data.download_url,
                summary: data.message
            });
        } catch (e) {
            setError('Failed to apply pipeline');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-8">
            {/* Control Panel */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                        <div className="bg-blue-100 p-2 rounded-lg">
                            <Droplet className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-gray-900">Data Cleaning & Transformation</h3>
                            <p className="text-gray-600 text-sm">Automated pipelines, manual editing, and advanced transformations</p>
                        </div>
                    </div>
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={() => setShowGrid(!showGrid)}
                            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${showGrid ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                        >
                            <Table className="w-4 h-4" />
                            <span>Grid</span>
                        </button>
                        <button
                            onClick={() => setShowTransforms(!showTransforms)}
                            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${showTransforms ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                        >
                            <Settings className="w-4 h-4" />
                            <span>Transforms</span>
                        </button>
                        <button
                            onClick={() => setShowPipelines(!showPipelines)}
                            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${showPipelines ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                        >
                            <Package className="w-4 h-4" />
                            <span>Pipelines</span>
                        </button>
                    </div>
                </div>

                {/* Automated Operations */}
                <div className="space-y-4 mb-8">
                    <h4 className="font-semibold text-gray-900">Quick Cleaning Operations</h4>
                    {AVAILABLE_OPERATIONS.map((op) => (
                        <div
                            key={op.id}
                            onClick={() => toggleOperation(op.id)}
                            className={`flex items-start space-x-4 p-4 rounded-lg border-2 cursor-pointer transition-all ${selectedOps.includes(op.id)
                                ? 'border-blue-500 bg-blue-50'
                                : 'border-gray-200 hover:border-blue-200'
                                }`}
                        >
                            <div className={`w-5 h-5 rounded border flex items-center justify-center mt-1 ${selectedOps.includes(op.id)
                                ? 'bg-blue-500 border-blue-500'
                                : 'border-gray-300 bg-white'
                                }`}>
                                {selectedOps.includes(op.id) && <CheckCircle className="w-3 h-3 text-white" />}
                            </div>
                            <div>
                                <h4 className="font-semibold text-gray-900">{op.label}</h4>
                                <p className="text-sm text-gray-600">{op.description}</p>
                            </div>
                        </div>
                    ))}
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 flex items-center space-x-2">
                        <AlertCircle className="w-5 h-5" />
                        <span>{error}</span>
                    </div>
                )}

                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <input
                            type="text"
                            placeholder="Pipeline name..."
                            value={pipelineName}
                            onChange={(e) => setPipelineName(e.target.value)}
                            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                        <button
                            onClick={handleSavePipeline}
                            disabled={selectedOps.length === 0 || !pipelineName.trim()}
                            className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
                        >
                            <Save className="w-4 h-4" />
                            <span>Save Pipeline</span>
                        </button>
                    </div>
                    <button
                        onClick={handleClean}
                        disabled={loading || selectedOps.length === 0}
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 font-medium"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span>Processing...</span>
                            </>
                        ) : (
                            <>
                                <Droplet className="w-4 h-4" />
                                <span>Apply Operations</span>
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Advanced Transformations */}
            {showTransforms && (
                <div className="bg-white rounded-xl shadow-lg p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">Advanced Transformations</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {TRANSFORMATIONS.map((transform) => (
                            <div
                                key={transform.id}
                                className="p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 cursor-pointer transition-all"
                            >
                                <div className="text-2xl mb-2">{transform.icon}</div>
                                <h4 className="font-semibold text-sm">{transform.label}</h4>
                            </div>
                        ))}
                    </div>
                    <p className="text-sm text-gray-500 mt-4">
                        💡 Advanced transformations coming soon! These will allow type conversion, text normalization, outlier removal, and more.
                    </p>
                </div>
            )}

            {/* Saved Pipelines */}
            {showPipelines && (
                <div className="bg-white rounded-xl shadow-lg p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">Saved Pipelines</h3>
                    {pipelines.length === 0 ? (
                        <p className="text-gray-500">No saved pipelines yet. Create one by selecting operations and clicking "Save Pipeline".</p>
                    ) : (
                        <div className="space-y-2">
                            {pipelines.map((pipeline, idx) => (
                                <div key={idx} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                                    <div>
                                        <h4 className="font-semibold">{pipeline.name}</h4>
                                        <p className="text-sm text-gray-500">{pipeline.steps_count} steps • {new Date(pipeline.created_at).toLocaleDateString()}</p>
                                    </div>
                                    <button
                                        onClick={() => handleApplyPipeline(pipeline.filename)}
                                        className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                                    >
                                        <Play className="w-4 h-4" />
                                        <span>Apply</span>
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Data Grid */}
            {showGrid && (
                <div className="bg-white rounded-xl shadow-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-gray-900">Visual Data Editor</h3>
                        <div className="flex items-center space-x-2">
                            <button
                                onClick={handleUndo}
                                disabled={historyIndex <= 0}
                                className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                                title="Undo"
                            >
                                <Undo className="w-4 h-4" />
                            </button>
                            <button
                                onClick={handleRedo}
                                disabled={historyIndex >= history.length - 1}
                                className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                                title="Redo"
                            >
                                <Redo className="w-4 h-4" />
                            </button>
                            <button
                                onClick={handleSaveChanges}
                                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                            >
                                <Save className="w-4 h-4" />
                                <span>Save Changes</span>
                            </button>
                        </div>
                    </div>
                    <div className="ag-theme-alpine" style={{ height: 500, width: '100%' }}>
                        <AgGridReact
                            rowData={gridData}
                            columnDefs={columnDefs}
                            defaultColDef={{
                                flex: 1,
                                minWidth: 100,
                                editable: true,
                                sortable: true,
                                filter: true,
                                resizable: true,
                            }}
                            onCellValueChanged={handleCellValueChanged}
                            pagination={true}
                            paginationPageSize={20}
                        />
                    </div>
                </div>
            )}

            {/* Success Result */}
            {result && (
                <div className="bg-green-50 border border-green-200 rounded-xl p-6 animate-fade-in">
                    <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3">
                            <CheckCircle className="w-6 h-6 text-green-600 mt-1" />
                            <div>
                                <h4 className="text-lg font-bold text-green-900">Success!</h4>
                                <p className="text-green-700 mt-1">{result.summary}</p>
                            </div>
                        </div>
                        <a
                            href={`${import.meta.env.VITE_API_URL}${result.download_url}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2 font-medium shadow-sm"
                        >
                            <Download className="w-4 h-4" />
                            <span>Download</span>
                        </a>
                    </div>
                </div>
            )}
        </div>
    );
};
