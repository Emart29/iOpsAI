import React, { useState, ChangeEvent } from 'react';
import axios from 'axios';
import type { Dataset } from '../../../types';

interface UploadSectionProps {
    onUploadSuccess: (dataset: Dataset) => void;
}

export const UploadSection: React.FC<UploadSectionProps> = ({ onUploadSuccess }) => {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string>('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string>('');

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        const selected = e.target.files?.[0];
        if (selected) {
            if (selected.size > 50 * 1024 * 1024) {
                setError('File size exceeds 50MB limit');
                return;
            }
            if (!selected.name.endsWith('.csv')) {
                setError('Only CSV files are allowed');
                return;
            }
            setFile(selected);
            setError('');
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);
        const form = new FormData();
        form.append('file', file);
        try {
            const resp = await axios.post(`${import.meta.env.VITE_API_URL}/api/upload`, form, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            const data = resp.data as Dataset;
            onUploadSuccess(data);
            // Generate preview of first 10 rows
            const previewResp = await axios.get(
                `${import.meta.env.VITE_API_URL}/api/profile/${data.session_id}`
            );
            setPreview(JSON.stringify(previewResp.data, null, 2));
        } catch (e: any) {
            setError(e?.response?.data?.detail || 'Upload failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-lg">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Upload CSV Dataset</h2>
            <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="mb-4"
            />
            {error && <p className="text-red-600 mb-2">{error}</p>}
            <button
                onClick={handleUpload}
                disabled={!file || loading}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
            >
                {loading ? 'Uploading...' : 'Upload'}
            </button>
            {preview && (
                <pre className="mt-4 bg-gray-100 p-4 rounded overflow-x-auto text-sm">
                    {preview}
                </pre>
            )}
        </div>
    );
};
