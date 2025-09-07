import React from 'react';
import { Alert } from 'react-bootstrap';
import { dashboardApi } from '../services/api';
import { useApiData } from '../hooks/useApiData';
import LoadingSpinner from '../components/LoadingSpinner';
import DashboardStatsCards from '../components/Dashboard/DashboardStatsCards';

const DashboardPage: React.FC = () => {
    const {
        data: stats,
        loading,
        error,
        refetch
    } = useApiData(dashboardApi.getStats);

    if (loading) {
        return <LoadingSpinner text="Loading dashboard..." />;
    }

    if (error) {
        return (
            <Alert variant="danger">
                <Alert.Heading>Error loading dashboard</Alert.Heading>
                <p>{error}</p>
                <button className="btn btn-outline-danger" onClick={refetch}>
                    Try Again
                </button>
            </Alert>
        );
    }

    if (!stats) {
        return null;
    }

    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1>Dashboard</h1>
                <button
                    className="btn btn-outline-primary"
                    onClick={refetch}
                    disabled={loading}
                >
                    {loading ? 'Refreshing...' : 'Refresh'}
                </button>
            </div>

            <DashboardStatsCards stats={stats} />
        </div>
    );
};

export default DashboardPage;
