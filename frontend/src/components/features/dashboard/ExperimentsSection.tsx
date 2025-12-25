import React, { useEffect, useState } from 'react';
import { BookOpen, Trash2, Clock, Loader2 } from 'lucide-react';
import type { Experiment } from '../../../types';
import { datasetService } from '../../../services/api';

export const ExperimentsSection: React.FC = () => {
    const [experiments, setExperiments] = useState<Experiment[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string>('');

    useEffect(() => {
        fetchExperiments();
    }, []);

    const fetchExperiments = async () => {
        try {
            const data = await datasetService.getExperiments();
            setExperiments(data);
        } catch (e: any) {
            setError('Failed to load experiments');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (sessionId: string) => {
        if (!window.confirm('Are you sure you want to delete this experiment?')) return;

        try {
            await datasetService.deleteExperiment(sessionId);
            setExperiments(prev => prev.filter(exp => exp.session_id !== sessionId));
        } catch (e) {
            alert('Failed to delete experiment');
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center py-20">
                <Loader2 className="w-8 h-8 text-purple-600 animate-spin" />
            </div>
        );
    }

    if (error) {
        return <div className="text-red-600 text-center py-10">{error}</div>;
    }

    return (
        <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <BookOpen className="w-6 h-6 text-purple-600" />
                        <h3 className="text-xl font-bold text-gray-900">Experiment Log</h3>
                    </div>
                    <span className="text-sm text-gray-500">{experiments.length} experiments found</span>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 text-gray-600 uppercase text-xs font-semibold">
                            <tr>
                                <th className="px-6 py-4">Dataset</th>
                                <th className="px-6 py-4">Date</th>
                                <th className="px-6 py-4">Status</th>
                                <th className="px-6 py-4">Features Used</th>
                                <th className="px-6 py-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {experiments.map((exp) => (
                                <tr key={exp.id} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-6 py-4">
                                        <div className="font-medium text-gray-900">{exp.dataset_name}</div>
                                        <div className="text-xs text-gray-500 font-mono">{exp.session_id.slice(0, 8)}</div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center space-x-2 text-gray-600">
                                            <Clock className="w-4 h-4" />
                                            <span>{new Date(exp.timestamp).toLocaleDateString()}</span>
                                        </div>
                                        <div className="text-xs text-gray-400 pl-6">
                                            {new Date(exp.timestamp).toLocaleTimeString()}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`
                                            inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                            ${exp.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}
                                        `}>
                                            {exp.status === 'completed' ? 'Completed' : 'In Progress'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex space-x-2">
                                            {exp.insights_generated && (
                                                <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs">Insights</span>
                                            )}
                                            {exp.report_generated && (
                                                <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs">Report</span>
                                            )}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button
                                            onClick={() => handleDelete(exp.session_id)}
                                            className="text-gray-400 hover:text-red-600 transition-colors p-2 rounded-full hover:bg-red-50"
                                            title="Delete Experiment"
                                        >
                                            <Trash2 className="w-5 h-5" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {experiments.length === 0 && (
                                <tr>
                                    <td colSpan={5} className="px-6 py-10 text-center text-gray-500">
                                        No experiments recorded yet. Upload a dataset to get started.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};
