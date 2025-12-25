import { useState } from 'react';
import { Sidebar } from '../components/layout/Sidebar';
import { UploadSection } from '../components/features/dashboard/UploadSection';
import { UsageCard } from '../components/features/dashboard/UsageCard';
import { InsightsPage } from '../pages/InsightsPage';
import { ChartsPage } from '../pages/ChartsPage';
import { ChatPage } from '../pages/ChatPage';
import { ReportPage } from '../pages/ReportPage';
import { CleanPage } from '../pages/CleanPage';
import { ScriptPage } from '../pages/ScriptPage';
import { RecommendationsPage } from '../pages/RecommendationsPage';
import { ExperimentsPage } from '../pages/ExperimentsPage';
import { ProfilePage } from '../pages/ProfilePage';
import { MLPage } from '../pages/MLPage';
import type { Dataset } from '../types';

export const DashboardPage = () => {
    const [activeSection, setActiveSection] = useState<string>('home');
    const [currentDataset, setCurrentDataset] = useState<Dataset | null>(null);

    const handleUploadSuccess = (dataset: Dataset) => {
        console.log('Upload successful, received data:', dataset);
        setCurrentDataset(dataset);
        setActiveSection('summary');
    };

    const renderContent = () => {
        switch (activeSection) {
            case 'home':
                return (
                    <div className="space-y-8">
                        {/* Usage Card */}
                        <UsageCard />
                        
                        {/* Welcome Section */}
                        <div className="max-w-4xl mx-auto text-center py-12">
                            <h1 className="text-4xl font-bold text-gray-900 mb-4">Welcome to Insight Studio</h1>
                            <p className="text-xl text-gray-600 mb-8">
                                Upload your dataset to get started with AI-powered analysis
                            </p>
                            <button
                                onClick={() => setActiveSection('upload')}
                                className="bg-purple-600 text-white px-8 py-4 rounded-lg hover:bg-purple-700 transition-colors font-semibold text-lg"
                            >
                                Upload Dataset
                            </button>
                        </div>
                    </div>
                );

            case 'upload':
                return <UploadSection onUploadSuccess={handleUploadSuccess} />;

            case 'summary':
                return (
                    <div>
                        <h2 className="text-3xl font-bold text-gray-900 mb-6">Data Summary</h2>
                        {currentDataset ? (
                            <div className="bg-white rounded-xl shadow-lg p-6">
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="bg-purple-50 p-4 rounded-lg">
                                        <p className="text-sm text-gray-600 mb-1">Filename</p>
                                        <p className="text-lg font-semibold text-gray-900">
                                            {currentDataset.filename || 'N/A'}
                                        </p>
                                    </div>
                                    <div className="bg-blue-50 p-4 rounded-lg">
                                        <p className="text-sm text-gray-600 mb-1">Rows</p>
                                        <p className="text-lg font-semibold text-gray-900">
                                            {currentDataset.rows?.toLocaleString() ?? '0'}
                                        </p>
                                    </div>
                                    <div className="bg-green-50 p-4 rounded-lg">
                                        <p className="text-sm text-gray-600 mb-1">Columns</p>
                                        <p className="text-lg font-semibold text-gray-900">
                                            {currentDataset.columns ?? '0'}
                                        </p>
                                    </div>
                                    <div className="bg-pink-50 p-4 rounded-lg">
                                        <p className="text-sm text-gray-600 mb-1">Session ID</p>
                                        <p className="text-lg font-semibold text-gray-900 truncate">
                                            {currentDataset.session_id?.slice(0, 8) || 'N/A'}...
                                        </p>
                                    </div>
                                </div>

                                {/* Additional Info */}
                                <div className="mt-6 pt-6 border-t border-gray-200">
                                    <p className="text-sm text-gray-600">
                                        Uploaded: {currentDataset.upload_timestamp
                                            ? new Date(currentDataset.upload_timestamp).toLocaleString()
                                            : 'Unknown'}
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <p className="text-gray-600">No dataset uploaded yet. Please upload a dataset first.</p>
                        )}
                    </div>
                );

            case 'profile':
                return currentDataset ? (
                    <ProfilePage dataset={currentDataset} />
                ) : (
                    <p className="text-gray-600">No dataset uploaded yet. Please upload a dataset first.</p>
                );

            case 'insights':
                return currentDataset ? (
                    <InsightsPage dataset={currentDataset} />
                ) : (
                    <p className="text-gray-600">No dataset uploaded yet. Please upload a dataset first.</p>
                );

            case 'charts':
                return currentDataset ? (
                    <ChartsPage dataset={currentDataset} />
                ) : (
                    <p className="text-gray-600">No dataset uploaded yet. Please upload a dataset first.</p>
                );

            case 'ml':
                return currentDataset ? (
                    <MLPage dataset={currentDataset} />
                ) : (
                    <p className="text-gray-600">No dataset uploaded yet. Please upload a dataset first.</p>
                );

            case 'chat':
                return currentDataset ? (
                    <ChatPage dataset={currentDataset} onNavigate={setActiveSection} />
                ) : (
                    <p className="text-gray-600">No dataset uploaded yet. Please upload a dataset first.</p>
                );

            case 'report':
                return currentDataset ? (
                    <ReportPage dataset={currentDataset} />
                ) : (
                    <p className="text-gray-600">No dataset uploaded yet. Please upload a dataset first.</p>
                );

            case 'clean':
                return currentDataset ? (
                    <CleanPage dataset={currentDataset} />
                ) : (
                    <p className="text-gray-600">No dataset uploaded yet. Please upload a dataset first.</p>
                );

            case 'script':
                return currentDataset ? (
                    <ScriptPage dataset={currentDataset} />
                ) : (
                    <p className="text-gray-600">No dataset uploaded yet. Please upload a dataset first.</p>
                );

            case 'recommendations':
                return currentDataset ? (
                    <RecommendationsPage dataset={currentDataset} />
                ) : (
                    <p className="text-gray-600">No dataset uploaded yet. Please upload a dataset first.</p>
                );

            case 'experiments':
                return <ExperimentsPage />;

            default:
                return (
                    <div className="text-center py-20">
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">
                            {activeSection.charAt(0).toUpperCase() + activeSection.slice(1)}
                        </h2>
                        <p className="text-gray-600">This feature is being implemented...</p>
                    </div>
                );
        }
    };

    return (
        <div className="flex min-h-screen bg-gray-50">
            <Sidebar activeSection={activeSection} onSectionChange={setActiveSection} />
            <main className="flex-1 md:ml-64 p-8">
                <div className="max-w-7xl mx-auto">
                    {/* Breadcrumb */}
                    <div className="mb-6">
                        <nav className="flex items-center space-x-2 text-sm text-gray-600">
                            <span>Dashboard</span>
                            <span>/</span>
                            <span className="text-purple-600 font-medium">
                                {activeSection.charAt(0).toUpperCase() + activeSection.slice(1)}
                            </span>
                        </nav>
                    </div>
                    {/* Content */}
                    {renderContent()}
                </div>
            </main>
        </div>
    );
};