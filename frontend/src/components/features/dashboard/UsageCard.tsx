import React, { useEffect, useState } from 'react';
import { usageService } from '../../../services/api';
import type { UsageStats } from '../../../types';

export const UsageCard: React.FC = () => {
    const [usage, setUsage] = useState<UsageStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadUsage();
    }, []);

    const loadUsage = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await usageService.getUsage();
            setUsage(data);
        } catch (err: any) {
            console.error('Failed to load usage stats:', err);
            setError(err.response?.data?.detail || 'Failed to load usage statistics');
        } finally {
            setLoading(false);
        }
    };

    const getProgressPercentage = (current: number, limit: number, unlimited: boolean): number => {
        if (unlimited) return 0;
        return Math.min((current / limit) * 100, 100);
    };

    const getProgressColor = (percentage: number): string => {
        if (percentage >= 90) return 'bg-red-500';
        if (percentage >= 70) return 'bg-yellow-500';
        return 'bg-green-500';
    };

    const shouldShowUpgrade = (current: number, limit: number, unlimited: boolean): boolean => {
        if (unlimited) return false;
        return (current / limit) >= 0.7; // Show upgrade when 70% or more used
    };

    const formatTierName = (tier: string): string => {
        return tier.charAt(0).toUpperCase() + tier.slice(1);
    };

    if (loading) {
        return (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 animate-pulse">
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
                <div className="space-y-4">
                    <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
                    <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
                    <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <div className="text-red-600 dark:text-red-400">
                    <p className="font-semibold">Error loading usage</p>
                    <p className="text-sm">{error}</p>
                </div>
            </div>
        );
    }

    if (!usage) {
        return null;
    }

    const showAnyUpgrade = 
        shouldShowUpgrade(usage.datasets.current, usage.datasets.limit, usage.datasets.unlimited) ||
        shouldShowUpgrade(usage.ai_messages.current, usage.ai_messages.limit, usage.ai_messages.unlimited) ||
        shouldShowUpgrade(usage.reports.current, usage.reports.limit, usage.reports.unlimited);

    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">Usage & Limits</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                        Current Plan: <span className="font-semibold text-purple-600 dark:text-purple-400">{formatTierName(usage.tier)}</span>
                    </p>
                </div>
                {showAnyUpgrade && usage.tier === 'free' && (
                    <button
                        onClick={() => window.location.href = '/pricing'}
                        className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors text-sm font-semibold"
                    >
                        Upgrade
                    </button>
                )}
            </div>

            <div className="space-y-6">
                {/* Datasets */}
                <div>
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Datasets Uploaded</span>
                        <span className="text-sm font-semibold text-gray-900 dark:text-white">
                            {usage.datasets.unlimited 
                                ? `${usage.datasets.current} / Unlimited` 
                                : `${usage.datasets.current} / ${usage.datasets.limit}`
                            }
                        </span>
                    </div>
                    {!usage.datasets.unlimited && (
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                            <div
                                className={`h-2.5 rounded-full transition-all ${getProgressColor(
                                    getProgressPercentage(usage.datasets.current, usage.datasets.limit, usage.datasets.unlimited)
                                )}`}
                                style={{
                                    width: `${getProgressPercentage(
                                        usage.datasets.current,
                                        usage.datasets.limit,
                                        usage.datasets.unlimited
                                    )}%`,
                                }}
                            ></div>
                        </div>
                    )}
                    {shouldShowUpgrade(usage.datasets.current, usage.datasets.limit, usage.datasets.unlimited) && (
                        <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
                            ⚠️ Approaching limit - consider upgrading
                        </p>
                    )}
                </div>

                {/* AI Messages */}
                <div>
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">AI Messages</span>
                        <span className="text-sm font-semibold text-gray-900 dark:text-white">
                            {usage.ai_messages.unlimited 
                                ? `${usage.ai_messages.current} / Unlimited` 
                                : `${usage.ai_messages.current} / ${usage.ai_messages.limit}`
                            }
                        </span>
                    </div>
                    {!usage.ai_messages.unlimited && (
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                            <div
                                className={`h-2.5 rounded-full transition-all ${getProgressColor(
                                    getProgressPercentage(usage.ai_messages.current, usage.ai_messages.limit, usage.ai_messages.unlimited)
                                )}`}
                                style={{
                                    width: `${getProgressPercentage(
                                        usage.ai_messages.current,
                                        usage.ai_messages.limit,
                                        usage.ai_messages.unlimited
                                    )}%`,
                                }}
                            ></div>
                        </div>
                    )}
                    {shouldShowUpgrade(usage.ai_messages.current, usage.ai_messages.limit, usage.ai_messages.unlimited) && (
                        <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
                            ⚠️ Approaching limit - consider upgrading
                        </p>
                    )}
                </div>

                {/* Public Reports */}
                <div>
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Public Reports</span>
                        <span className="text-sm font-semibold text-gray-900 dark:text-white">
                            {usage.reports.unlimited 
                                ? `${usage.reports.current} / Unlimited` 
                                : `${usage.reports.current} / ${usage.reports.limit}`
                            }
                        </span>
                    </div>
                    {!usage.reports.unlimited && (
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                            <div
                                className={`h-2.5 rounded-full transition-all ${getProgressColor(
                                    getProgressPercentage(usage.reports.current, usage.reports.limit, usage.reports.unlimited)
                                )}`}
                                style={{
                                    width: `${getProgressPercentage(
                                        usage.reports.current,
                                        usage.reports.limit,
                                        usage.reports.unlimited
                                    )}%`,
                                }}
                            ></div>
                        </div>
                    )}
                    {shouldShowUpgrade(usage.reports.current, usage.reports.limit, usage.reports.unlimited) && (
                        <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
                            ⚠️ Approaching limit - consider upgrading
                        </p>
                    )}
                </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-500 dark:text-gray-400">
                    Usage resets on the 1st of each month • Current period: {usage.month_year}
                </p>
            </div>
        </div>
    );
};
