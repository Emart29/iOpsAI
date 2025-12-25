export interface Dataset {
    session_id: string;
    filename: string;
    rows: number;
    columns: number;
    upload_timestamp: string;
    file_path?: string;
}

export interface DataProfile {
    column: string;
    dtype: string;
    non_null: number;
    unique: number;
    missing_pct: number;
    stats?: {
        mean?: number;
        median?: number;
        std?: number;
        min?: number;
        max?: number;
        q1?: number;
        q3?: number;
    };
    top_values?: Array<{ value: string; count: number }>;
}

export interface FullDataProfile {
    overview: {
        rows: number;
        columns: number;
        memory_usage: number;
        duplicate_rows: number;
        total_missing: number;
        completeness_score: number;
    };
    columns: {
        [key: string]: {
            dtype: string;
            missing: number;
            missing_percentage: number;
            unique: number;
            type: 'numeric' | 'categorical';
            stats: any;
            outliers?: any;
            sample_data: any[];
        };
    };
    data_quality: {
        score: number;
        issues: Array<{
            type: string;
            column: string;
            severity: string;
            message: string;
            suggestion: string;
        }>;
    };
}

export interface Insight {
    category: string;
    title: string;
    description: string;
}

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export interface ChartData {
    [key: string]: {
        data: any[];
        layout: any;
    };
}

export interface CleaningOperation {
    id: string;
    label: string;
    description: string;
}

export interface Experiment {
    id: number;
    session_id: string;
    dataset_name: string;
    timestamp: string;
    rows: number;
    columns: number;
    insights_generated: boolean;
    report_generated: boolean;
    status: string;
}

export interface UsageStats {
    tier: string;
    month_year: string;
    datasets: {
        current: number;
        limit: number;
        unlimited: boolean;
    };
    ai_messages: {
        current: number;
        limit: number;
        unlimited: boolean;
    };
    reports: {
        current: number;
        limit: number;
        unlimited: boolean;
    };
}
