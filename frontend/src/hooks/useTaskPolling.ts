import { useState, useEffect, useCallback } from 'react';
import { tasksApi } from '../services/api';

interface UseTaskPollingOptions {
    onSuccess?: (result: any) => void;
    onError?: (error: any) => void;
    pollingInterval?: number;
    maxAttempts?: number;
}

export const useTaskPolling = (
    taskId: string | null,
    options: UseTaskPollingOptions = {}
) => {
    const {
        onSuccess,
        onError,
        pollingInterval = 2000, // 2 segundos
        maxAttempts = 150 // 5 minutos máximo
    } = options;

    const [isPolling, setIsPolling] = useState(false);
    const [attempts, setAttempts] = useState(0);
    const [taskState, setTaskState] = useState<string | null>(null);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const checkTaskStatus = useCallback(async () => {
        if (!taskId) return;

        try {
            const status = await tasksApi.checkStatus(taskId);
            setTaskState(status.state);

            if (status.state === 'SUCCESS') {
                setResult(status.result);
                setIsPolling(false);
                onSuccess?.(status.result);
            } else if (status.state === 'FAILURE') {
                setError('Task failed');
                setIsPolling(false);
                onError?.(status.result);
            } else if (status.state === 'RETRY') {
                setError('Task is retrying...');
            }
        } catch (err) {
            console.error('Error checking task status:', err);
            setError('Error checking task status');
        }
    }, [taskId, onSuccess, onError]);

    useEffect(() => {
        if (!taskId || !isPolling) return;

        const interval = setInterval(() => {
            setAttempts(prev => {
                const newAttempts = prev + 1;

                if (newAttempts >= maxAttempts) {
                    setIsPolling(false);
                    setError('Polling timeout');
                    return newAttempts;
                }

                checkTaskStatus();
                return newAttempts;
            });
        }, pollingInterval);

        return () => clearInterval(interval);
    }, [isPolling, taskId, checkTaskStatus, pollingInterval, maxAttempts]);

    const startPolling = useCallback((newTaskId?: string) => {
        const id = newTaskId || taskId;
        if (!id) return;

        setIsPolling(true);
        setAttempts(0);
        setError(null);
        setResult(null);
        setTaskState(null);

        // Primeira verificação imediata
        setTimeout(() => checkTaskStatus(), 500);
    }, [taskId, checkTaskStatus]);

    const stopPolling = useCallback(() => {
        setIsPolling(false);
    }, []);

    return {
        isPolling,
        taskState,
        result,
        error,
        attempts,
        startPolling,
        stopPolling,
    };
};
