// Types para os modelos da API
export interface Theme {
    id: number;
    title: string;
    created_at: string;
    updated_at: string;
    is_active: boolean;
    processing_status: 'idle' | 'processing' | 'completed' | 'failed';
    is_processing: boolean;
    suggested_topics: {
        topics: Topic[];
    } | null;
    topics_generated_at: string | null;
    posts_count: number;
    articles_count: number;
    simple_posts_count: number;
}

export interface Topic {
    hook: string;
    post_type: string;
    summary: string;
    cta: string;
}

export interface Post {
    id: number;
    theme: number;
    theme_title: string;
    post_type: 'simple' | 'article';
    title: string;
    content: string;
    promotional_post: string;
    cover_image_prompt: string;
    topic: string;
    seo_title: string;
    seo_description: string;
    link: string;
    post_date: string;
    scheduled_date: string | null;
    status: 'draft' | 'generated' | 'published' | 'scheduled';
    processing_status: 'idle' | 'processing' | 'completed' | 'failed';
    is_processing: boolean;
    created_at: string;
    updated_at: string;
    generated_at: string | null;
    generation_prompt: string;
    ai_model_used: string;
    content_preview: string;
}

export interface DashboardStats {
    total_themes: number;
    total_posts: number;
    published_posts: number;
    draft_posts: number;
    generated_posts: number;
    ai_service: string;
    recent_posts: Post[];
    recent_themes: Theme[];
}

export interface TaskStatus {
    task_id: string;
    state: string;
    result: any;
    info: any;
}

export interface ApiResponse<T> {
    data: T;
    message?: string;
}

export interface GenerateTopicsRequest {
    theme_id: number;
}

export interface GeneratePostRequest {
    theme_id: number;
    topic: string;
    post_type: 'simple' | 'article';
    topic_data?: {
        hook: string;
        post_type: string;
        summary: string;
        cta: string;
    };
}

export interface ThemeCreateRequest {
    title: string;
}

export interface PostUpdateRequest {
    title?: string;
    content?: string;
    promotional_post?: string;
    seo_title?: string;
    seo_description?: string;
    link?: string;
    scheduled_date?: string;
    status?: string;
}
