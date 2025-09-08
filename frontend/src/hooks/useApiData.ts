import { useState, useEffect, useCallback } from 'react';

interface UseApiDataOptions<T> {
    initialData?: T;
    onSuccess?: (data: T) => void;
    onError?: (error: any) => void;
    autoFetch?: boolean;
}

export function useApiData<T>(
    apiFunction: () => Promise<T>,
    options: UseApiDataOptions<T> = {}
) {
    const {
        initialData,
        onSuccess,
        onError,
        autoFetch = true
    } = options;

    const [data, setData] = useState<T | undefined>(initialData);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const result = await apiFunction();
            setData(result);
            onSuccess?.(result);
        } catch (err: any) {
            const errorMessage = err?.response?.data?.message || err?.message || 'An error occurred';
            setError(errorMessage);
            onError?.(err);
        } finally {
            setLoading(false);
        }
    }, [apiFunction, onSuccess, onError]);

    const refetch = useCallback(() => {
        return fetchData();
    }, [fetchData]);

    const mutate = useCallback((newData: T) => {
        setData(newData);
    }, []);

    useEffect(() => {
        if (autoFetch) {
            fetchData();
        }
    }, [fetchData, autoFetch]);

    return {
        data,
        loading,
        error,
        refetch,
        mutate,
    };
}

// Hook específico para listas com refresh automático
export function useApiList<T>(
    apiFunction: () => Promise<T[]>,
    options: UseApiDataOptions<T[]> = {}
) {
    const {
        data: items,
        loading,
        error,
        refetch,
        mutate
    } = useApiData(apiFunction, options);

    const addItem = useCallback((newItem: T) => {
        if (items) {
            mutate([newItem, ...items]);
        }
    }, [items, mutate]);

    const updateItem = useCallback((id: number | string, updatedItem: Partial<T> & { id: number | string }) => {
        if (items) {
            const updated = items.map(item =>
                (item as any).id === id ? { ...item, ...updatedItem } : item
            );
            mutate(updated);
        }
    }, [items, mutate]);

    const removeItem = useCallback((id: number | string) => {
        if (items) {
            const filtered = items.filter(item => (item as any).id !== id);
            mutate(filtered);
        }
    }, [items, mutate]);

    return {
        items: items || [],
        loading,
        error,
        refetch,
        addItem,
        updateItem,
        removeItem,
    };
}
