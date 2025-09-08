export interface Post {
    id: number;
    title: string;
    content: string;
    seo_title?: string;
    seo_description?: string;
    promotional_post?: string;
    status: 'draft' | 'generated' | 'scheduled' | 'published';
    theme: number;
    link?: string;
    cover_image_prompt?: string;
    generation_prompt?: string;
    created_at: string;
    updated_at: string;
}
