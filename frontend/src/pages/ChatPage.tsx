import React from 'react';
import type { Dataset } from '../types';
import { ChatSection } from '../components/features/dashboard/ChatSection';

interface ChatPageProps {
    dataset: Dataset;
    onNavigate: (section: string) => void;
}

export const ChatPage: React.FC<ChatPageProps> = ({ dataset, onNavigate }) => {
    return (
        <div className="space-y-6 h-full">
            <h2 className="text-3xl font-bold text-gray-900">Chat with Sight</h2>
            <ChatSection dataset={dataset} onNavigate={onNavigate} />
        </div>
    );
};
