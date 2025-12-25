import React, { useState, useEffect } from 'react';
import {
    Brain, Play, Target, Award, Download,
    Settings, Loader2, CheckCircle, AlertCircle, BarChart3
} from 'lucide-react';
import type { Dataset } from '../../../types';

interface MLSectionProps {
    dataset: Dataset;
}

interface ModelResult {
    metrics: any;
    status: string;
    error?: string;
}

export const MLSection: React.FC<MLSectionProps> = ({ dataset }) => {
    const [taskType, setTaskType] = useState<'classification' | 'regression'>('classification');
    const [targetColumn, setTargetColumn] = useState('');
    const [columns, setColumns] = useState<string[]>([]);
    const [training, setTraining] = useState(false);
    const [results, setResults] = useState<Record<string, ModelResult> | null>(null);
    const [featureImportance, setFeatureImportance] = useState<any[]>([]);
    const [bestModel, setBestModel] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchColumns();
    }, [dataset.session_id]);

    const fetchColumns = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/data-preview/${dataset.session_id}?limit=1`);
            const data = await response.json();
            if (data.columns) {
                setColumns(data.columns);
                if (data.columns.length > 0) {
                    setTargetColumn(data.columns[data.columns.length - 1]);
                }
            }
        } catch (e) {
            console.error('Failed to fetch columns:', e);
        }
    };

    const handleTrain = async () => {
        if (!targetColumn) {
            setError('Please select a target column');
            return;
        }

        setTraining(true);
        setError('');
        setResults(null);

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/ml/train/${dataset.session_id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    target_column: targetColumn,
                    task_type: taskType,
                    test_size: 0.2
                })
            });

            if (!response.ok) {
                throw new Error('Training failed');
            }

            const data = await response.json();
            setResults(data.results);
            setFeatureImportance(data.feature_importance || []);
            setBestModel(data.best_model || '');
        } catch (e: any) {
            setError(e.message || 'Failed to train models');
        } finally {
            setTraining(false);
        }
    };

    const getMetricDisplay = (_model: string, result: ModelResult) => {
        if (result.status !== 'success') {
            return (
                <div className="text-red-600 text-sm">
                    <AlertCircle className="w-4 h-4 inline mr-1" />
                    {result.error || 'Training failed'}
                </div>
            );
        }
        const metrics = result.metrics;
        if (taskType === 'classification') {
            return (
                <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                        <span className="text-gray-600">Accuracy:</span>
                        <span className="font-semibold ml-2">{(metrics.accuracy * 100).toFixed(2)}%</span>
                    </div>
                    <div>
                        <span className="text-gray-600">F1 Score:</span>
                        <span className="font-semibold ml-2">{(metrics.f1_score * 100).toFixed(2)}%</span>
                    </div>
                    <div>
                        <span className="text-gray-600">Precision:</span>
                        <span className="font-semibold ml-2">{(metrics.precision * 100).toFixed(2)}%</span>
                    </div>
                    <div>
                        <span className="text-gray-600">Recall:</span>
                        <span className="font-semibold ml-2">{(metrics.recall * 100).toFixed(2)}%</span>
                    </div>
                </div>
            );
        } else {
            return (
                <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                        <span className="text-gray-600">R² Score:</span>
                        <span className="font-semibold ml-2">{metrics.r2_score.toFixed(4)}</span>
                    </div>
                    <div>
                        <span className="text-gray-600">RMSE:</span>
                        <span className="font-semibold ml-2">{metrics.rmse.toFixed(4)}</span>
                    </div>
                    <div>
                        <span className="text-gray-600">MAE:</span>
                        <span className="font-semibold ml-2">{metrics.mae.toFixed(4)}</span>
                    </div>
                    <div>
                        <span className="text-gray-600">MSE:</span>
                        <span className="font-semibold ml-2">{metrics.mse.toFixed(4)}</span>
                    </div>
                </div>
            );
        }
    };

    return (
        <div className="space-y-8">
            {/* Configuration Panel */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center space-x-3 mb-6">
                    <div className="bg-purple-100 p-2 rounded-lg">
                        <Brain className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-gray-900">AutoML Training</h3>
                        <p className="text-gray-600 text-sm">Automatically train and compare multiple ML models</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    {/* Task Type */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Task Type
                        </label>
                        <select
                            value={taskType}
                            onChange={(e) => setTaskType(e.target.value as 'classification' | 'regression')}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                            <option value="classification">Classification</option>
                            <option value="regression">Regression</option>
                        </select>
                    </div>

                    {/* Target Column */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Target Column
                        </label>
                        <select
                            value={targetColumn}
                            onChange={(e) => setTargetColumn(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                            <option value="">Select target...</option>
                            {columns.map((col) => (
                                <option key={col} value={col}>{col}</option>
                            ))}
                        </select>
                    </div>

                    {/* Train Button */}
                    <div className="flex items-end">
                        <button
                            onClick={handleTrain}
                            disabled={training || !targetColumn}
                            className="w-full bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 font-medium"
                        >
                            {training ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    <span>Training...</span>
                                </>
                            ) : (
                                <>
                                    <Play className="w-4 h-4" />
                                    <span>Train Models</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-4 rounded-lg flex items-center space-x-2">
                        <AlertCircle className="w-5 h-5" />
                        <span>{error}</span>
                    </div>
                )}
            </div>

            {/* Results */}
            {results && (
                <>
                    {/* Model Comparison */}
                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-lg font-bold text-gray-900">Model Comparison</h3>
                            {bestModel && (
                                <div className="flex items-center space-x-2 text-green-600">
                                    <Award className="w-5 h-5" />
                                    <span className="font-semibold">Best: {bestModel}</span>
                                </div>
                            )}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {Object.entries(results).map(([modelName, result]) => (
                                <div
                                    key={modelName}
                                    className={`p-4 rounded-lg border-2 ${modelName === bestModel
                                        ? 'border-green-500 bg-green-50'
                                        : 'border-gray-200'
                                        }`}
                                >
                                    <div className="flex items-center justify-between mb-3">
                                        <h4 className="font-semibold text-gray-900">{modelName}</h4>
                                        {modelName === bestModel && (
                                            <CheckCircle className="w-5 h-5 text-green-600" />
                                        )}
                                    </div>
                                    {getMetricDisplay(modelName, result)}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Feature Importance */}
                    {featureImportance.length > 0 && (
                        <div className="bg-white rounded-xl shadow-lg p-6">
                            <div className="flex items-center space-x-2 mb-6">
                                <BarChart3 className="w-5 h-5 text-purple-600" />
                                <h3 className="text-lg font-bold text-gray-900">Feature Importance</h3>
                            </div>
                            <div className="space-y-3">
                                {featureImportance.map((feature, idx) => (
                                    <div key={idx} className="flex items-center space-x-3">
                                        <span className="text-sm font-medium text-gray-700 w-32 truncate">
                                            {feature.feature}
                                        </span>
                                        <div className="flex-1 bg-gray-200 rounded-full h-4">
                                            <div
                                                className="bg-purple-600 h-4 rounded-full transition-all"
                                                style={{ width: `${feature.importance * 100}%` }}
                                            />
                                        </div>
                                        <span className="text-sm text-gray-600 w-16 text-right">
                                            {(feature.importance * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Actions */}
                    <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6">
                        <h3 className="text-lg font-bold text-gray-900 mb-4">Next Steps</h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <button className="flex items-center justify-center space-x-2 px-4 py-3 bg-white border-2 border-purple-200 rounded-lg hover:border-purple-500 transition-colors">
                                <Settings className="w-5 h-5 text-purple-600" />
                                <span className="font-medium">Tune Hyperparameters</span>
                            </button>
                            <button className="flex items-center justify-center space-x-2 px-4 py-3 bg-white border-2 border-blue-200 rounded-lg hover:border-blue-500 transition-colors">
                                <Target className="w-5 h-5 text-blue-600" />
                                <span className="font-medium">Make Predictions</span>
                            </button>
                            <button className="flex items-center justify-center space-x-2 px-4 py-3 bg-white border-2 border-green-200 rounded-lg hover:border-green-500 transition-colors">
                                <Download className="w-5 h-5 text-green-600" />
                                <span className="font-medium">Export Model</span>
                            </button>
                        </div>
                    </div>
                </>
            )}

            {/* Info Card */}
            {!results && !training && (
                <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-8 text-center">
                    <Brain className="w-16 h-16 text-purple-600 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-gray-900 mb-2">Ready to Train</h3>
                    <p className="text-gray-600 mb-4">
                        Select your task type and target column, then click "Train Models" to automatically
                        train and compare multiple machine learning algorithms.
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 text-sm">
                        <div className="bg-white p-3 rounded-lg">
                            <div className="font-semibold text-purple-600">6+</div>
                            <div className="text-gray-600">Algorithms</div>
                        </div>
                        <div className="bg-white p-3 rounded-lg">
                            <div className="font-semibold text-blue-600">Auto</div>
                            <div className="text-gray-600">Preprocessing</div>
                        </div>
                        <div className="bg-white p-3 rounded-lg">
                            <div className="font-semibold text-green-600">5-Fold</div>
                            <div className="text-gray-600">Cross-Val</div>
                        </div>
                        <div className="bg-white p-3 rounded-lg">
                            <div className="font-semibold text-orange-600">Best</div>
                            <div className="text-gray-600">Auto-Select</div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
