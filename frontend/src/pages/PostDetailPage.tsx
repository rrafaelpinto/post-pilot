import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Row,
    Col,
    Card,
    Button,
    Badge,
    Alert,
    Modal,
    Form,
    Spinner,
    Breadcrumb,
    Toast,
    ToastContainer,
    Dropdown,
    ButtonGroup
} from 'react-bootstrap';
import ReactMarkdown from 'react-markdown';
import { Post } from '../types/post';
import { Theme } from '../types/theme';
import Layout from '../components/Layout';
import { postsApi, tasksApi } from '../services/api';

const PostDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();

    const [post, setPost] = useState<Post | null>(null);
    const [theme, setTheme] = useState<Theme | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string>('');
    const [showEditModal, setShowEditModal] = useState<boolean>(false);
    const [editData, setEditData] = useState<Partial<Post>>({});
    const [updating, setUpdating] = useState<boolean>(false);
    const [improving, setImproving] = useState<boolean>(false);
    const [generating, setGenerating] = useState<boolean>(false);
    const [showToast, setShowToast] = useState<boolean>(false);
    const [toastMessage, setToastMessage] = useState<string>('');
    const [toastVariant, setToastVariant] = useState<'success' | 'danger'>('success');

    // Funções para calcular métricas do conteúdo
    const calculateMetrics = (content: string) => {
        if (!content) return { wordCount: 0, charCount: 0, charCountNoSpaces: 0, readingTime: 0 };

        // Remove markdown syntax para contagem mais precisa
        const plainText = content
            .replace(/#{1,6}\s+/g, '') // Headers
            .replace(/\*\*(.*?)\*\*/g, '$1') // Bold
            .replace(/\*(.*?)\*/g, '$1') // Italic
            .replace(/`(.*?)`/g, '$1') // Inline code
            .replace(/```[\s\S]*?```/g, '') // Code blocks
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Links
            .replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1') // Images
            .replace(/>\s*/g, '') // Blockquotes
            .replace(/^\s*[-*+]\s+/gm, '') // List items
            .replace(/^\s*\d+\.\s+/gm, '') // Numbered lists
            .replace(/\n+/g, ' ') // Multiple newlines
            .trim();

        const wordCount = plainText.split(/\s+/).filter(word => word.length > 0).length;
        const charCount = content.length;
        const charCountNoSpaces = content.replace(/\s/g, '').length;

        // Cálculo de tempo de leitura (assumindo 200 palavras por minuto)
        const readingTime = Math.ceil(wordCount / 200);

        return {
            wordCount,
            charCount,
            charCountNoSpaces,
            readingTime: readingTime || 1 // Mínimo 1 minuto
        };
    };

    useEffect(() => {
        if (id) {
            fetchPost();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [id]);

    const fetchPost = async () => {
        try {
            setLoading(true);
            const response = await fetch(`http://localhost:8000/api/posts/${id}/`);

            if (!response.ok) {
                throw new Error(`Erro: ${response.status}`);
            }

            const data = await response.json();
            setPost(data);

            // Buscar tema se existir
            if (data.theme) {
                const themeResponse = await fetch(`http://localhost:8000/api/themes/${data.theme}/`);
                if (themeResponse.ok) {
                    const themeData = await themeResponse.json();
                    setTheme(themeData);
                }
            }
        } catch (err) {
            setError('Erro ao carregar post');
            console.error('Error fetching post:', err);
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadge = (status: string) => {
        const statusMap: { [key: string]: { variant: string; text: string } } = {
            draft: { variant: 'secondary', text: 'Rascunho' },
            published: { variant: 'success', text: 'Publicado' },
            archived: { variant: 'warning', text: 'Arquivado' },
        };

        const statusInfo = statusMap[status] || { variant: 'secondary', text: status };
        return <Badge bg={statusInfo.variant}>{statusInfo.text}</Badge>;
    };

    const copyToClipboard = async (text: string, name: string) => {
        try {
            await navigator.clipboard.writeText(text);
            showToastMessage(`${name} copiado para área de transferência!`, 'success');
        } catch (err) {
            console.error('Erro ao copiar:', err);
            showToastMessage('Erro ao copiar texto', 'danger');
        }
    };

    const handleUpdatePost = async () => {
        try {
            setUpdating(true);
            const response = await fetch(`http://localhost:8000/api/posts/${post!.id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(editData),
            });

            if (!response.ok) {
                throw new Error('Erro ao atualizar post');
            }

            const updatedPost = await response.json();
            setPost(updatedPost);
            setShowEditModal(false);
            setEditData({});
            showToastMessage('Post atualizado com sucesso!', 'success');
        } catch (err) {
            console.error('Erro ao atualizar post:', err);
            showToastMessage('Erro ao atualizar post', 'danger');
        } finally {
            setUpdating(false);
        }
    };

    const handleImprovePost = async () => {
        if (!post) return;

        try {
            setImproving(true);
            const response = await postsApi.improve(post.id);

            showToastMessage('Post sendo melhorado em segundo plano');
            setTimeout(() => checkTaskStatus(response.task_id, 'improve'), 2000);
        } catch (err) {
            console.error('Erro ao melhorar post:', err);
            showToastMessage('Erro ao melhorar post', 'danger');
            setImproving(false);
        }
    };

    const checkTaskStatus = async (taskId: string, type: string) => {
        try {
            const status = await tasksApi.checkStatus(taskId);

            if (status.state === 'SUCCESS') {
                setImproving(false);
                fetchPost();
                showToastMessage(`${type === 'improve' ? 'Melhoria' : 'Prompt de imagem'} concluída!`, 'success');
            } else if (status.state === 'FAILURE') {
                setImproving(false);

                let errorMessage = `Erro na ${type === 'improve' ? 'melhoria' : 'geração de prompt'}`;

                if (status.result && typeof status.result === 'object') {
                    if (status.result.message) {
                        errorMessage = status.result.message;
                    } else if (status.result.status === 'error' && status.result.message) {
                        errorMessage = status.result.message;
                    }
                } else if (typeof status.result === 'string') {
                    errorMessage = status.result;
                }

                showToastMessage(errorMessage, 'danger');
            } else if (status.state === 'PENDING' || status.state === 'STARTED') {
                setTimeout(() => checkTaskStatus(taskId, type), 3000);
            }
        } catch (error) {
            setImproving(false);
            showToastMessage('Erro ao verificar status da tarefa', 'danger');
        }
    };

    const handleGenerateImage = async () => {
        if (!post) return;

        try {
            setGenerating(true);
            const response = await fetch(`http://localhost:8000/api/posts/${post.id}/regenerate-image-prompt/`, {
                method: 'POST',
            });

            if (!response.ok) {
                throw new Error('Erro ao gerar imagem');
            }

            showToastMessage('Prompt de imagem sendo gerado em segundo plano');
            setTimeout(fetchPost, 3000);
        } catch (err) {
            console.error('Erro ao gerar imagem:', err);
            showToastMessage('Erro ao gerar prompt de imagem', 'danger');
        } finally {
            setGenerating(false);
        }
    };

    const showToastMessage = (message: string, variant: 'success' | 'danger' = 'success') => {
        setToastMessage(message);
        setToastVariant(variant);
        setShowToast(true);
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('pt-BR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <Layout>
                <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
                    <Spinner animation="border" role="status">
                        <span className="visually-hidden">Carregando...</span>
                    </Spinner>
                </div>
            </Layout>
        );
    }

    if (error || !post) {
        return (
            <Layout>
                <Alert variant="danger" className="mt-4">
                    {error || 'Post não encontrado'}
                </Alert>
            </Layout>
        );
    }

    return (
        <Layout>
            {/* Breadcrumb e Ações */}
            <Row className="mb-3">
                <Col xs={12}>
                    <div className="d-flex align-items-center justify-content-between flex-wrap">
                        <Breadcrumb className="mb-0">
                            <Breadcrumb.Item href="/">Home</Breadcrumb.Item>
                            <Breadcrumb.Item href="/posts">Posts</Breadcrumb.Item>
                            <Breadcrumb.Item active>
                                {post.title?.substring(0, 50)}{post.title?.length > 50 ? '...' : ''}
                            </Breadcrumb.Item>
                        </Breadcrumb>

                        <div className="d-flex align-items-center gap-2 mt-2 mt-md-0">
                            <Button
                                variant="outline-secondary"
                                size="sm"
                                onClick={() => navigate('/posts')}
                            >
                                ← Voltar
                            </Button>

                            <Dropdown as={ButtonGroup}>
                                <Dropdown.Toggle variant="primary" size="sm">
                                    Ações
                                </Dropdown.Toggle>
                                <Dropdown.Menu>
                                    <Dropdown.Item onClick={() => setShowEditModal(true)}>
                                        ✏️ Editar Post
                                    </Dropdown.Item>
                                    <Dropdown.Item
                                        onClick={handleImprovePost}
                                        disabled={improving}
                                    >
                                        {improving ? '⏳ Melhorando...' : '✨ Melhorar Post'}
                                    </Dropdown.Item>
                                    {post.post_type === 'article' && (
                                        <Dropdown.Item
                                            onClick={handleGenerateImage}
                                            disabled={generating}
                                        >
                                            {generating ? '⏳ Gerando...' : '🖼️ Gerar Prompt de Imagem'}
                                        </Dropdown.Item>
                                    )}
                                    <Dropdown.Divider />
                                    <Dropdown.Item
                                        onClick={() => copyToClipboard(post.content, 'Conteúdo')}
                                    >
                                        📋 Copiar Conteúdo
                                    </Dropdown.Item>
                                </Dropdown.Menu>
                            </Dropdown>
                        </div>
                    </div>
                </Col>
            </Row>

            <Row>
                {/* Conteúdo Principal */}
                <Col lg={8} md={12} className="mb-4">
                    {/* Header do Post */}
                    <Card className="mb-4">
                        <Card.Body>
                            <h1 className="mb-3">{post.title}</h1>
                            <div className="mb-2">
                                {getStatusBadge(post.status)}
                                <Badge bg="secondary" className="ms-2">
                                    {post.post_type === 'simple' ? 'Post Simples' : 'Artigo'}
                                </Badge>
                                {theme && (
                                    <Badge bg="info" className="ms-2">
                                        {theme.name}
                                    </Badge>
                                )}
                            </div>
                        </Card.Body>
                    </Card>

                    {/* Conteúdo do Post */}
                    <Card className="mb-4">
                        <Card.Header>
                            <h5 className="mb-0">Conteúdo</h5>
                        </Card.Header>
                        <Card.Body>
                            <ReactMarkdown>{post.content}</ReactMarkdown>
                        </Card.Body>
                    </Card>

                    {/* Post Promocional */}
                    {post.promotional_post && (
                        <Card className="mb-4">
                            <Card.Header className="d-flex justify-content-between align-items-center">
                                <h5 className="mb-0">Post Promocional</h5>
                                <Button
                                    variant="outline-primary"
                                    size="sm"
                                    onClick={() => copyToClipboard(post.promotional_post!, 'Post promocional')}
                                >
                                    📋 Copiar
                                </Button>
                            </Card.Header>
                            <Card.Body>
                                <ReactMarkdown>{post.promotional_post}</ReactMarkdown>
                            </Card.Body>
                        </Card>
                    )}

                    {/* SEO */}
                    {(post.seo_title || post.seo_description) && (
                        <Card className="mb-4">
                            <Card.Header>
                                <h5 className="mb-0">SEO</h5>
                            </Card.Header>
                            <Card.Body>
                                {post.seo_title && (
                                    <div className="mb-3">
                                        <label className="form-label fw-bold">Título SEO:</label>
                                        <div className="p-2 bg-light rounded">{post.seo_title}</div>
                                    </div>
                                )}
                                {post.seo_description && (
                                    <div>
                                        <label className="form-label fw-bold">Descrição SEO:</label>
                                        <div className="p-2 bg-light rounded">{post.seo_description}</div>
                                    </div>
                                )}
                            </Card.Body>
                        </Card>
                    )}
                </Col>

                {/* Sidebar */}
                <Col lg={4} md={12}>
                    {/* Métricas */}
                    <Card className="mb-4">
                        <Card.Header>
                            <h6 className="mb-0">📊 Métricas</h6>
                        </Card.Header>
                        <Card.Body>
                            {(() => {
                                const metrics = calculateMetrics(post.content);
                                return (
                                    <div className="row text-center g-3">
                                        <div className="col-6">
                                            <div className="border rounded p-2">
                                                <div className="h5 mb-1 text-primary">{metrics.wordCount.toLocaleString()}</div>
                                                <small className="text-muted">Palavras</small>
                                            </div>
                                        </div>
                                        <div className="col-6">
                                            <div className="border rounded p-2">
                                                <div className="h5 mb-1 text-success">{metrics.charCount.toLocaleString()}</div>
                                                <small className="text-muted">Caracteres</small>
                                            </div>
                                        </div>
                                        <div className="col-6">
                                            <div className="border rounded p-2">
                                                <div className="h5 mb-1 text-info">{metrics.charCountNoSpaces.toLocaleString()}</div>
                                                <small className="text-muted">Sem espaços</small>
                                            </div>
                                        </div>
                                        <div className="col-6">
                                            <div className="border rounded p-2">
                                                <div className="h5 mb-1 text-warning">{metrics.readingTime} min</div>
                                                <small className="text-muted">Leitura</small>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })()}
                        </Card.Body>
                    </Card>

                    {/* Informações de Data */}
                    <Card className="mb-4">
                        <Card.Header>
                            <h6 className="mb-0">📅 Datas</h6>
                        </Card.Header>
                        <Card.Body>
                            <div className="mb-3">
                                <small className="text-muted d-block">Criado em:</small>
                                <strong>{formatDate(post.created_at)}</strong>
                            </div>
                            {post.updated_at !== post.created_at && (
                                <div className="mb-3">
                                    <small className="text-muted d-block">Atualizado em:</small>
                                    <strong>{formatDate(post.updated_at)}</strong>
                                </div>
                            )}
                        </Card.Body>
                    </Card>

                    {/* Informações do Tema */}
                    {theme && (
                        <Card className="mb-4">
                            <Card.Header>
                                <h6 className="mb-0">Tema</h6>
                            </Card.Header>
                            <Card.Body>
                                <div className="mb-2">
                                    <strong>{theme.name}</strong>
                                </div>
                                {post.topic && (
                                    <div className="mb-2">
                                        <small className="text-muted">Tópico:</small>
                                        <div>{post.topic}</div>
                                    </div>
                                )}
                                {theme.stack && (
                                    <div>
                                        <small className="text-muted">Stack:</small>
                                        <div>{theme.stack}</div>
                                    </div>
                                )}
                            </Card.Body>
                        </Card>
                    )}

                    {/* Informações de IA */}
                    {(post.ai_provider_used || post.ai_model_used) && (
                        <Card className="mb-4">
                            <Card.Header>
                                <h6 className="mb-0">🤖 Informações de IA</h6>
                            </Card.Header>
                            <Card.Body>
                                {post.ai_provider_used && (
                                    <div className="mb-2">
                                        <small className="text-muted d-block">Provedor:</small>
                                        <Badge
                                            bg={
                                                post.ai_provider_used === 'openai' ? 'success' :
                                                    post.ai_provider_used === 'grok' ? 'warning' :
                                                        post.ai_provider_used === 'gemini' ? 'info' : 'secondary'
                                            }
                                            className="text-capitalize"
                                        >
                                            {
                                                post.ai_provider_used === 'openai' ? 'OpenAI' :
                                                    post.ai_provider_used === 'grok' ? 'Grok (X.AI)' :
                                                        post.ai_provider_used === 'gemini' ? 'Google Gemini' :
                                                            post.ai_provider_used
                                            }
                                        </Badge>
                                    </div>
                                )}
                                {post.ai_model_used && (
                                    <div>
                                        <small className="text-muted d-block">Modelo:</small>
                                        <code className="text-dark">{post.ai_model_used}</code>
                                    </div>
                                )}
                            </Card.Body>
                        </Card>
                    )}

                    {/* Prompt de Geração */}
                    {post.generation_prompt && (
                        <Card className="mb-4">
                            <Card.Header>
                                <h6 className="mb-0">🤖 Prompt de Geração</h6>
                            </Card.Header>
                            <Card.Body>
                                <div className="small text-muted" style={{ fontSize: '0.85rem' }}>
                                    {post.generation_prompt}
                                </div>
                            </Card.Body>
                        </Card>
                    )}

                    {/* Prompt de Imagem de Capa */}
                    {post.cover_image_prompt && (
                        <Card className="mb-4">
                            <Card.Header className="d-flex justify-content-between align-items-center">
                                <h6 className="mb-0">🖼️ Prompt de Imagem</h6>
                                <Button
                                    variant="outline-primary"
                                    size="sm"
                                    onClick={() => copyToClipboard(post.cover_image_prompt!, 'Prompt de imagem')}
                                >
                                    📋
                                </Button>
                            </Card.Header>
                            <Card.Body>
                                <div className="small text-muted" style={{ fontSize: '0.85rem' }}>
                                    {post.cover_image_prompt}
                                </div>
                            </Card.Body>
                        </Card>
                    )}
                </Col>
            </Row>

            {/* Modal de Edição */}
            <Modal show={showEditModal} onHide={() => setShowEditModal(false)} size="lg">
                <Modal.Header closeButton>
                    <Modal.Title>Editar Post</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form>
                        <Form.Group className="mb-3">
                            <Form.Label>Título</Form.Label>
                            <Form.Control
                                type="text"
                                value={editData.title || post.title}
                                onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                            />
                        </Form.Group>
                        {post.topic && (
                            <Form.Group className="mb-3">
                                <Form.Label>Tópico</Form.Label>
                                <Form.Control
                                    type="text"
                                    value={editData.topic || post.topic}
                                    onChange={(e) => setEditData({ ...editData, topic: e.target.value })}
                                />
                            </Form.Group>
                        )}
                        <Form.Group className="mb-3">
                            <Form.Label>Status</Form.Label>
                            <Form.Select
                                value={editData.status || post.status}
                                onChange={(e) => setEditData({ ...editData, status: e.target.value as 'draft' | 'generated' | 'scheduled' | 'published' })}
                            >
                                <option value="draft">Rascunho</option>
                                <option value="published">Publicado</option>
                                <option value="generated">Gerado</option>
                                <option value="scheduled">Agendado</option>
                            </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Conteúdo</Form.Label>
                            <Form.Control
                                as="textarea"
                                rows={10}
                                value={editData.content || post.content}
                                onChange={(e) => setEditData({ ...editData, content: e.target.value })}
                            />
                        </Form.Group>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowEditModal(false)}>
                        Cancelar
                    </Button>
                    <Button
                        variant="primary"
                        onClick={handleUpdatePost}
                        disabled={updating}
                    >
                        {updating ? 'Salvando...' : 'Salvar'}
                    </Button>
                </Modal.Footer>
            </Modal>

            {/* Toast de Notificação */}
            <ToastContainer position="bottom-end" className="p-3">
                <Toast
                    show={showToast}
                    onClose={() => setShowToast(false)}
                    delay={3000}
                    autohide
                    bg={toastVariant}
                >
                    <Toast.Body className="text-white">
                        {toastMessage}
                    </Toast.Body>
                </Toast>
            </ToastContainer>
        </Layout>
    );
};

export default PostDetailPage;
