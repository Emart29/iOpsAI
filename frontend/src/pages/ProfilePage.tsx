import React from 'react';
import type { Dataset } from '../types';
import { ProfileSection } from '../components/features/dashboard/ProfileSection';

interface ProfilePageProps {
    dataset: Dataset;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({ dataset }) => {
    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">Deep Data Profile</h2>
            <ProfileSection dataset={dataset} />
        </div>
    );
};
