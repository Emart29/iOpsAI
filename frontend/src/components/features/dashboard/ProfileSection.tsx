import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, Database, FileText } from 'lucide-react';
import type { Dataset, FullDataProfile } from '../../../types';
import { datasetService } from '../../../services/api';

interface ProfileSectionProps {
    dataset: Dataset;
}

export const ProfileSection: React.FC<ProfileSectionProps> = ({ dataset }) => {
    const [profile, setProfile] = useState<FullDataProfile | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string>('');

    useEffect(() => {
        const fetchProfile = async () => {
            setLoading(true);
            try {
                const data = await datasetService.getProfile(dataset.session_id);
                setProfile(data);
            } catch (e: any) {
                setError(e?.response?.data?.detail || 'Failed to load profile');
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [dataset.session_id]);

    if (loading) return <div className="text-center py-10">Generating comprehensive data profile...</div>;
    if (error) return <div className="text-red-600 py-10">{error}</div>;
    if (!profile) return null;

    return (
        <div className="space-y-8">
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex items-center space-x-3 mb-2">
                        <Database className="w-5 h-5 text-purple-600" />
                        <h4 className="font-semibold text-gray-700">Dimensions</h4>
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{profile.overview.rows} rows</p>
                    <p className="text-sm text-gray-500">{profile.overview.columns} columns</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex items-center space-x-3 mb-2">
                        <Activity className="w-5 h-5 text-blue-600" />
                        <h4 className="font-semibold text-gray-700">Quality Score</h4>
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{profile.data_quality.score.toFixed(1)}/100</p>
                    <p className="text-sm text-gray-500">Overall Health</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex items-center space-x-3 mb-2">
                        <AlertTriangle className="w-5 h-5 text-orange-600" />
                        <h4 className="font-semibold text-gray-700">Missing Data</h4>
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{profile.overview.total_missing}</p>
                    <p className="text-sm text-gray-500">Total missing cells</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex items-center space-x-3 mb-2">
                        <FileText className="w-5 h-5 text-green-600" />
                        <h4 className="font-semibold text-gray-700">Completeness</h4>
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{(profile.overview.completeness_score * 100).toFixed(1)}%</p>
                    <p className="text-sm text-gray-500">Data filled</p>
                </div>
            </div>

            {/* Data Quality Issues */}
            {profile.data_quality.issues.length > 0 && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="p-4 bg-red-50 border-b border-red-100 flex items-center space-x-2">
                        <AlertTriangle className="w-5 h-5 text-red-600" />
                        <h3 className="font-bold text-red-900">Quality Issues Detected</h3>
                    </div>
                    <div className="divide-y divide-gray-100">
                        {profile.data_quality.issues.map((issue, idx) => (
                            <div key={idx} className="p-4 hover:bg-gray-50 transition-colors">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h5 className="font-semibold text-gray-900">{issue.message}</h5>
                                        <p className="text-sm text-gray-600 mt-1">Suggestion: {issue.suggestion}</p>
                                    </div>
                                    <span className={`px-2 py-1 rounded text-xs font-medium ${issue.severity === 'high' ? 'bg-red-100 text-red-700' :
                                        issue.severity === 'medium' ? 'bg-orange-100 text-orange-700' :
                                            'bg-yellow-100 text-yellow-700'
                                        }`}>
                                        {issue.severity.toUpperCase()}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Column Details */}
            <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-900">Column Analysis</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(profile.columns).map(([colName, colData]) => (
                        <div key={colName} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h4 className="text-lg font-bold text-gray-900">{colName}</h4>
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 mt-1">
                                        {colData.dtype}
                                    </span>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm text-gray-500">Unique: {colData.unique}</p>
                                    <p className="text-sm text-gray-500">Missing: {colData.missing} ({colData.missing_percentage.toFixed(1)}%)</p>
                                </div>
                            </div>

                            {colData.type === 'numeric' && colData.stats && (
                                <div className="grid grid-cols-2 gap-2 text-sm">
                                    <div className="bg-gray-50 p-2 rounded">
                                        <span className="text-gray-500 block">Mean</span>
                                        <span className="font-medium">{colData.stats.mean.toFixed(2)}</span>
                                    </div>
                                    <div className="bg-gray-50 p-2 rounded">
                                        <span className="text-gray-500 block">Median</span>
                                        <span className="font-medium">{colData.stats.median.toFixed(2)}</span>
                                    </div>
                                    <div className="bg-gray-50 p-2 rounded">
                                        <span className="text-gray-500 block">Min</span>
                                        <span className="font-medium">{colData.stats.min.toFixed(2)}</span>
                                    </div>
                                    <div className="bg-gray-50 p-2 rounded">
                                        <span className="text-gray-500 block">Max</span>
                                        <span className="font-medium">{colData.stats.max.toFixed(2)}</span>
                                    </div>
                                </div>
                            )}

                            {colData.type === 'categorical' && colData.stats && (
                                <div className="bg-gray-50 p-3 rounded text-sm">
                                    <p className="text-gray-500 mb-1">Top Value</p>
                                    <p className="font-medium truncate">{colData.stats.top_value}</p>
                                    <p className="text-xs text-gray-400 mt-1">Freq: {colData.stats.top_frequency}</p>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};
