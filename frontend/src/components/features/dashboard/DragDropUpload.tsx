import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from '../../ui/ToastProvider';
import axios from 'axios';
import type { Dataset } from '../../../types';

interface DragDropUploadProps {
    onUploadSuccess: (dataset: Dataset) => void;
}

export const DragDropUpload: React.FC<DragDropUploadProps> = ({ onUploadSuccess }) => {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);

    const onDrop = useCallback((acceptedFiles: File[]) => {
        const selectedFile = acceptedFiles[0];

        if (!selectedFile) return;

        // Validate file size (50MB)
        if (selectedFile.size > 50 * 1024 * 1024) {
            toast.error('File size exceeds 50MB limit');
            return;
        }

        // Validate file type
        const validTypes = ['.csv', '.xlsx', '.xls', '.json'];
        const fileExt = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();

        if (!validTypes.includes(fileExt)) {
            toast.error('Invalid file type. Please upload CSV, Excel, or JSON files.');
            return;
        }

        setFile(selectedFile);
        toast.success(`File "${selectedFile.name}" selected`);
    }, []);

    const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
        onDrop,
        accept: {
            'text/csv': ['.csv'],
            'application/vnd.ms-excel': ['.xls'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
            'application/json': ['.json']
        },
        maxFiles: 1,
        multiple: false
    });

    const handleUpload = async () => {
        if (!file) {
            toast.error('Please select a file first');
            return;
        }

        setUploading(true);
        setProgress(0);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post(
                `${import.meta.env.VITE_API_URL}/api/upload`,
                formData,
                {
                    headers: { 'Content-Type': 'multipart/form-data' },
                    onUploadProgress: (progressEvent) => {
                        const percentCompleted = Math.round(
                            (progressEvent.loaded * 100) / (progressEvent.total || 1)
                        );
                        setProgress(percentCompleted);
                    }
                }
            );

            toast.success('Dataset uploaded successfully!');
            onUploadSuccess(response.data);
            setFile(null);
            setProgress(0);
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    const removeFile = () => {
        setFile(null);
        setProgress(0);
    };

    return (
        <div className="max-w-2xl mx-auto">
            {/* Dropzone */}
            <div
                {...getRootProps()}
                className={`
                    border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
                    transition-all duration-200 ease-in-out
                    ${isDragActive && !isDragReject ? 'border-purple-500 bg-purple-50' : ''}
                    ${isDragReject ? 'border-red-500 bg-red-50' : ''}
                    ${!isDragActive && !file ? 'border-gray-300 hover:border-purple-400 hover:bg-gray-50' : ''}
                    ${file ? 'border-green-500 bg-green-50' : ''}
                `}
            >
                <input {...getInputProps()} />

                <div className="flex flex-col items-center space-y-4">
                    {file ? (
                        <>
                            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full">
                                <CheckCircle className="w-8 h-8 text-green-600" />
                            </div>
                            <div>
                                <p className="text-lg font-semibold text-gray-900">File Selected</p>
                                <p className="text-sm text-gray-600 mt-1">{file.name}</p>
                                <p className="text-xs text-gray-500 mt-1">
                                    {(file.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                            </div>
                        </>
                    ) : isDragActive ? (
                        <>
                            <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 rounded-full">
                                <Upload className="w-8 h-8 text-purple-600 animate-bounce" />
                            </div>
                            <div>
                                <p className="text-lg font-semibold text-purple-600">Drop your file here</p>
                                <p className="text-sm text-gray-600 mt-1">Release to upload</p>
                            </div>
                        </>
                    ) : isDragReject ? (
                        <>
                            <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full">
                                <AlertCircle className="w-8 h-8 text-red-600" />
                            </div>
                            <div>
                                <p className="text-lg font-semibold text-red-600">Invalid File Type</p>
                                <p className="text-sm text-gray-600 mt-1">Please upload CSV, Excel, or JSON files</p>
                            </div>
                        </>
                    ) : (
                        <>
                            <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full">
                                <Upload className="w-8 h-8 text-gray-600" />
                            </div>
                            <div>
                                <p className="text-lg font-semibold text-gray-900">
                                    Drag & drop your dataset here
                                </p>
                                <p className="text-sm text-gray-600 mt-1">
                                    or click to browse
                                </p>
                            </div>
                            <div className="flex items-center space-x-2 text-xs text-gray-500">
                                <File className="w-4 h-4" />
                                <span>CSV, Excel, JSON • Max 50MB</span>
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* File Preview & Actions */}
            {file && (
                <div className="mt-6 bg-white rounded-xl shadow-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-purple-100 rounded-lg">
                                <File className="w-5 h-5 text-purple-600" />
                            </div>
                            <div>
                                <p className="font-medium text-gray-900">{file.name}</p>
                                <p className="text-sm text-gray-500">
                                    {(file.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                            </div>
                        </div>
                        {!uploading && (
                            <button
                                onClick={removeFile}
                                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                            >
                                <X className="w-5 h-5 text-gray-600" />
                            </button>
                        )}
                    </div>

                    {/* Progress Bar */}
                    {uploading && (
                        <div className="mb-4">
                            <div className="flex justify-between text-sm text-gray-600 mb-2">
                                <span>Uploading...</span>
                                <span>{progress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                                <div
                                    className="bg-gradient-to-r from-purple-600 to-blue-600 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${progress}%` }}
                                ></div>
                            </div>
                        </div>
                    )}

                    {/* Upload Button */}
                    <button
                        onClick={handleUpload}
                        disabled={uploading}
                        className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                    >
                        {uploading ? (
                            <span className="flex items-center justify-center">
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                Uploading {progress}%
                            </span>
                        ) : (
                            'Upload Dataset'
                        )}
                    </button>
                </div>
            )}
        </div>
    );
};
