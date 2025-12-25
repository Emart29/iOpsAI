interface SkeletonProps {
    className?: string;
    style?: React.CSSProperties;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '', style }) => {
    return (
        <div className={`animate-pulse bg-gray-200 rounded ${className}`} style={style}></div>
    );
};

export const CardSkeleton = () => {
    return (
        <div className="bg-white rounded-xl shadow-lg p-6 space-y-4">
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <div className="flex space-x-2 mt-4">
                <Skeleton className="h-8 w-20" />
                <Skeleton className="h-8 w-20" />
            </div>
        </div>
    );
};

export const TableSkeleton = () => {
    return (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="p-4 border-b border-gray-200">
                <Skeleton className="h-8 w-48" />
            </div>
            <div className="divide-y divide-gray-200">
                {[...Array(5)].map((_, i) => (
                    <div key={i} className="p-4 flex items-center space-x-4">
                        <Skeleton className="h-10 w-10 rounded-full" />
                        <div className="flex-1 space-y-2">
                            <Skeleton className="h-4 w-1/3" />
                            <Skeleton className="h-3 w-1/2" />
                        </div>
                        <Skeleton className="h-8 w-24" />
                    </div>
                ))}
            </div>
        </div>
    );
};

export const ChartSkeleton = () => {
    return (
        <div className="bg-white rounded-xl shadow-lg p-6">
            <Skeleton className="h-6 w-48 mb-4" />
            <div className="h-64 flex items-end space-x-2">
                {[...Array(8)].map((_, i) => (
                    <Skeleton
                        key={i}
                        className="flex-1"
                        style={{ height: `${Math.random() * 100 + 50}px` }}
                    />
                ))}
            </div>
        </div>
    );
};

export const ListSkeleton = () => {
    return (
        <div className="space-y-3">
            {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-white rounded-lg p-4 flex items-center space-x-3">
                    <Skeleton className="h-12 w-12 rounded-lg" />
                    <div className="flex-1 space-y-2">
                        <Skeleton className="h-4 w-3/4" />
                        <Skeleton className="h-3 w-1/2" />
                    </div>
                    <Skeleton className="h-8 w-8 rounded-full" />
                </div>
            ))}
        </div>
    );
};

export const ProfileSkeleton = () => {
    return (
        <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center space-x-4 mb-6">
                <Skeleton className="h-20 w-20 rounded-full" />
                <div className="flex-1 space-y-2">
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-32" />
                </div>
            </div>
            <div className="space-y-4">
                <div>
                    <Skeleton className="h-4 w-24 mb-2" />
                    <Skeleton className="h-10 w-full" />
                </div>
                <div>
                    <Skeleton className="h-4 w-24 mb-2" />
                    <Skeleton className="h-10 w-full" />
                </div>
                <div>
                    <Skeleton className="h-4 w-24 mb-2" />
                    <Skeleton className="h-10 w-full" />
                </div>
            </div>
        </div>
    );
};
