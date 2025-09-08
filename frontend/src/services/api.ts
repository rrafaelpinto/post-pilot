import axios from 'axios';
import {
    Theme,
    Post,
    DashboardStats,
    TaskStatus,
    ThemeCreateRequest,
    GeneratePostRequest,
    PostUpdateRequest
} from '../types/api';

// Configuração base do axios
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor para adicionar token de autenticação (se necessário no futuro)
api.interceptors.request.use(
    (config) => {
        // Adicionar token de auth aqui se necessário
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor para tratamento de respostas
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);

// ========== DASHBOARD ==========
export const dashboardApi = {
    getStats: (): Promise<DashboardStats> =>
        api.get('/api/dashboard/stats/').then(res => res.data),
};

// ========== THEMES ==========
export const themesApi = {
    getAll: (): Promise<Theme[]> =>
        api.get('/api/themes/').then(res => res.data.results || res.data),

    getById: (id: number): Promise<Theme> =>
        api.get(`/api/themes/${id}/`).then(res => res.data),

    create: (data: ThemeCreateRequest): Promise<Theme> =>
        api.post('/api/themes/', data).then(res => res.data),

    update: (id: number, data: Partial<Theme>): Promise<Theme> =>
        api.patch(`/api/themes/${id}/`, data).then(res => res.data),

    delete: (id: number): Promise<void> =>
        api.delete(`/api/themes/${id}/`),

    generateTopics: (id: number): Promise<{ task_id: string; message: string }> =>
        api.post(`/api/themes/${id}/generate_topics/`).then(res => res.data),

    generatePost: (id: number, data: Omit<GeneratePostRequest, 'theme_id'>): Promise<{ task_id: string; message: string }> =>
        api.post(`/api/themes/${id}/generate_post/`, data).then(res => res.data),

    getPosts: (id: number): Promise<Post[]> =>
        api.get(`/api/themes/${id}/posts/`).then(res => res.data),

    getStatus: (id: number): Promise<any> =>
        api.get(`/api/themes/${id}/status/`).then(res => res.data),
};

// ========== POSTS ==========
export const postsApi = {
    getAll: (): Promise<Post[]> =>
        api.get('/api/posts/').then(res => res.data.results || res.data),

    getById: (id: number): Promise<Post> =>
        api.get(`/api/posts/${id}/`).then(res => res.data),

    update: (id: number, data: PostUpdateRequest): Promise<Post> =>
        api.patch(`/api/posts/${id}/`, data).then(res => res.data),

    delete: (id: number): Promise<void> =>
        api.delete(`/api/posts/${id}/`),

    improve: (id: number): Promise<{ task_id: string; message: string }> =>
        api.post(`/api/posts/${id}/improve/`).then(res => res.data),

    regenerateImagePrompt: (id: number): Promise<{ task_id: string; message: string }> =>
        api.post(`/api/posts/${id}/regenerate_image_prompt/`).then(res => res.data),

    publish: (id: number): Promise<{ message: string }> =>
        api.post(`/api/posts/${id}/publish/`).then(res => res.data),

    getStatus: (id: number): Promise<any> =>
        api.get(`/api/posts/${id}/status/`).then(res => res.data),
};

// ========== TASKS ==========
export const tasksApi = {
    checkStatus: (taskId: string): Promise<TaskStatus> =>
        api.get(`/api/tasks/check/?task_id=${taskId}`).then(res => res.data),
};

export default api;
