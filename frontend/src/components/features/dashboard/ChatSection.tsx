import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import type { ChatMessage, Dataset } from '../../../types';
import { datasetService } from '../../../services/api';

interface ChatSectionProps {
    dataset: Dataset;
    onNavigate: (section: string) => void;
}

export const ChatSection: React.FC<ChatSectionProps> = ({ dataset, onNavigate }) => {
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            role: 'assistant',
            content: `Hello! I'm Sight, your AI data assistant. I've analyzed ${dataset.filename}. Ask me anything about your data!`,
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim() || loading) return;

        const userMessage: ChatMessage = {
            role: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await datasetService.chat(dataset.session_id, userMessage.content, messages);

            const botMessage: ChatMessage = {
                role: 'assistant',
                content: response,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, botMessage]);

            // Agentic Action Handling
            if (response.includes("**Action:**")) {
                if (response.includes("Generating") && (response.includes("chart") || response.includes("histogram") || response.includes("bar"))) {
                    setTimeout(() => onNavigate('charts'), 1500);
                } else if (response.includes("applying") || response.includes("cleaning")) {
                    setTimeout(() => onNavigate('clean'), 1500);
                }
            }

        } catch (error) {
            const errorMessage: ChatMessage = {
                role: 'assistant',
                content: 'Sorry, I encountered an error processing your request.',
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-200px)] bg-white rounded-xl shadow-lg overflow-hidden">
            {/* Chat Header */}
            <div className="bg-purple-600 p-4 text-white flex items-center space-x-3">
                <Bot className="w-6 h-6" />
                <div>
                    <h3 className="font-bold">Sight AI Assistant</h3>
                    <p className="text-xs text-purple-200">Analyzing {dataset.filename}</p>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'user'
                                ? 'bg-purple-600 text-white rounded-br-none'
                                : 'bg-white text-gray-800 shadow-sm rounded-bl-none border border-gray-200'
                                }`}
                        >
                            <div className="flex items-center space-x-2 mb-1">
                                {msg.role === 'assistant' ? (
                                    <Bot className="w-4 h-4 text-purple-600" />
                                ) : (
                                    <User className="w-4 h-4 text-purple-200" />
                                )}
                                <span className="text-xs opacity-70">
                                    {msg.role === 'user' ? 'You' : 'Sight'}
                                </span>
                            </div>
                            <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-white text-gray-800 shadow-sm rounded-lg rounded-bl-none border border-gray-200 p-3">
                            <div className="flex items-center space-x-2">
                                <Loader2 className="w-4 h-4 animate-spin text-purple-600" />
                                <span className="text-sm text-gray-500">Thinking...</span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-gray-200">
                <form onSubmit={handleSend} className="flex space-x-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a question about your data..."
                        className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || loading}
                        className="bg-purple-600 text-white p-2 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </form>
            </div>
        </div>
    );
};
