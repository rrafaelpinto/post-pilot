import React, { useState, useEffect, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
    Container,
    Row,
    Col,
    Card,
    Button,
    Badge,
    Spinner,
    Alert,
    Form,
    InputGroup,
    Toast,
    ToastContainer
} from 'react-bootstrap';
import { Post, Theme } from '../types/api';
import { postsApi, themesApi, tasksApi } from '../services/api';

const PostsPage: React.FC = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const [posts, setPosts] = useState<Post[]>([]);
    const [filteredPosts, setFilteredPosts] = useState<Post[]>([]);
    const [themes, setThemes] = useState<Theme[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('all');
    const [typeFilter, setTypeFilter] = useState<string>('all');
    const [themeFilter, setThemeFilter] = useState<string>('all');
    const [processingPosts, setProcessingPosts] = useState<Set<number>>(new Set());
    const [showToast, setShowToast] = useState(false);
    const [toastMessage, setToastMessage] = useState('');
    const [toastVariant, setToastVariant] = useState<'success' | 'danger'>('success');

    useEffect(() => {
        loadData();

        // Verifica se há filtro de tema na URL
        const themeParam = searchParams.get('theme');
        if (themeParam) {
            setThemeFilter(themeParam);
        }
    }, [searchParams]);

    const loadData = async () => {
        try {
            setLoading(true);
            const [postsData, themesData] = await Promise.all([
                postsApi.getAll(),
                themesApi.getAll()
            ]);
            setPosts(Array.isArray(postsData) ? postsData : []);
            setThemes(Array.isArray(themesData) ? themesData : []);
        } catch (error) {
            setError('Erro ao carregar posts');
            console.error('Error loading posts:', error);
        } finally {
            setLoading(false);
        }
    };

    const applyFilters = useCallback(() => {
        let filtered = [...posts];

        // Filtro por termo de busca
        if (searchTerm) {
            filtered = filtered.filter(post =>
                post.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                post.topic?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                post.content?.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        // Filtro por status
        if (statusFilter !== 'all') {
            filtered = filtered.filter(post => post.status === statusFilter);
        }

        // Filtro por tipo
        if (typeFilter !== 'all') {
            filtered = filtered.filter(post => post.post_type === typeFilter);
        }

        // Filtro por tema
        if (themeFilter !== 'all') {
            filtered = filtered.filter(post => post.theme.toString() === themeFilter);
        }

        setFilteredPosts(filtered);
    }, [posts, searchTerm, statusFilter, typeFilter, themeFilter]);

    useEffect(() => {
        applyFilters();
    }, [applyFilters]);

    const handleImprovePost = async (postId: number) => {
        try {
            setProcessingPosts(prev => {
                const newSet = new Set(prev);
                newSet.add(postId);
                return newSet;
            });
            const response = await postsApi.improve(postId);
            showToastMessage('Melhoria do post iniciada!', 'success');

            setTimeout(() => checkTaskStatus(response.task_id, postId, 'improve'), 2000);
        } catch (error) {
            showToastMessage('Erro ao melhorar post', 'danger');
            console.error('Error improving post:', error);
            setProcessingPosts(prev => {
                const newSet = new Set(prev);
                newSet.delete(postId);
                return newSet;
            });
        }
    };

    const handleRegenerateImagePrompt = async (postId: number) => {
        try {
            setProcessingPosts(prev => {
                const newSet = new Set(prev);
                newSet.add(postId);
                return newSet;
            });
            const response = await postsApi.regenerateImagePrompt(postId);
            showToastMessage('Geração de prompt de imagem iniciada!', 'success');

            setTimeout(() => checkTaskStatus(response.task_id, postId, 'image'), 2000);
        } catch (error) {
            showToastMessage('Erro ao gerar prompt de imagem', 'danger');
            console.error('Error regenerating image prompt:', error);
            setProcessingPosts(prev => {
                const newSet = new Set(prev);
                newSet.delete(postId);
                return newSet;
            });
        }
    };

    const handlePublishPost = async (postId: number) => {
        try {
            await postsApi.publish(postId);
            showToastMessage('Post publicado com sucesso!', 'success');
            loadData(); // Recarrega para atualizar o status
        } catch (error) {
            showToastMessage('Erro ao publicar post', 'danger');
            console.error('Error publishing post:', error);
        }
    };

    const checkTaskStatus = async (taskId: string, postId: number, type: string) => {
        try {
            const status = await tasksApi.checkStatus(taskId);

            if (status.state === 'SUCCESS') {
                setProcessingPosts(prev => {
                    const newSet = new Set(prev);
                    newSet.delete(postId);
                    return newSet;
                });
                loadData();
                showToastMessage(`${type === 'improve' ? 'Melhoria' : 'Prompt de imagem'} concluída!`, 'success');
            } else if (status.state === 'FAILURE') {
                setProcessingPosts(prev => {
                    const newSet = new Set(prev);
                    newSet.delete(postId);
                    return newSet;
                });
                showToastMessage(`Erro na ${type === 'improve' ? 'melhoria' : 'geração de prompt'}`, 'danger');
            } else if (status.state === 'PENDING' || status.state === 'STARTED') {
                setTimeout(() => checkTaskStatus(taskId, postId, type), 3000);
            }
        } catch (error) {
            setProcessingPosts(prev => {
                const newSet = new Set(prev);
                newSet.delete(postId);
                return newSet;
            });
            showToastMessage('Erro ao verificar status da tarefa', 'danger');
        }
    };

    const showToastMessage = (message: string, variant: 'success' | 'danger') => {
        setToastMessage(message);
        setToastVariant(variant);
        setShowToast(true);
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getStatusBadge = (status: string) => {
        const statusMap = {
            'draft': { bg: 'secondary', text: 'Rascunho' },
            'generated': { bg: 'warning', text: 'Gerado' },
            'published': { bg: 'success', text: 'Publicado' },
            'scheduled': { bg: 'info', text: 'Agendado' }
        };
        const statusInfo = statusMap[status as keyof typeof statusMap] || { bg: 'secondary', text: status };
        return <Badge bg={statusInfo.bg}>{statusInfo.text}</Badge>;
    };

    const getThemeName = (themeId: number) => {
        const theme = themes.find(t => t.id === themeId);
        return theme ? theme.title : 'Tema não encontrado';
    };

    const clearFilters = () => {
        setSearchTerm('');
        setStatusFilter('all');
        setTypeFilter('all');
        setThemeFilter('all');
        setSearchParams({});
    };

    if (loading) {
        return (
            <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '50vh' }}>
                <Spinner animation="border" role="status">
                    <span className="visually-hidden">Carregando...</span>
                </Spinner>
            </Container>
        );
    }

    if (error) {
        return (
            <Container>
                <Alert variant="danger">{error}</Alert>
            </Container>
        );
    }

    return (
        <Container fluid>
            {/* Header */}
            <Row className="mb-4">
                <Col>
                    <div className="d-flex justify-content-between align-items-center">
                        <h1>Posts</h1>
                        <div>
                            <Link to="/themes" className="btn btn-outline-primary me-2">
                                Gerenciar Temas
                            </Link>
                            <Button variant="outline-secondary" onClick={clearFilters} size="sm">
                                Limpar Filtros
                            </Button>
                        </div>
                    </div>
                </Col>
            </Row>

            {/* Filtros */}
            <Row className="mb-4">
                <Col lg={3} md={6} className="mb-2">
                    <InputGroup>
                        <Form.Control
                            type="text"
                            placeholder="Buscar posts..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </InputGroup>
                </Col>
                <Col lg={2} md={3} sm={6} className="mb-2">
                    <Form.Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                        <option value="all">Todos os Status</option>
                        <option value="draft">Rascunho</option>
                        <option value="generated">Gerado</option>
                        <option value="published">Publicado</option>
                        <option value="scheduled">Agendado</option>
                    </Form.Select>
                </Col>
                <Col lg={2} md={3} sm={6} className="mb-2">
                    <Form.Select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
                        <option value="all">Todos os Tipos</option>
                        <option value="simple">Post Simples</option>
                        <option value="article">Artigo</option>
                    </Form.Select>
                </Col>
                <Col lg={3} md={6} className="mb-2">
                    <Form.Select value={themeFilter} onChange={(e) => setThemeFilter(e.target.value)}>
                        <option value="all">Todos os Temas</option>
                        {themes.map(theme => (
                            <option key={theme.id} value={theme.id.toString()}>
                                {theme.title}
                            </option>
                        ))}
                    </Form.Select>
                </Col>
                <Col lg={2} md={6} className="mb-2">
                    <div className="text-muted small">
                        {filteredPosts.length} de {posts.length} posts
                    </div>
                </Col>
            </Row>

            {/* Lista de Posts */}
            {filteredPosts.length === 0 ? (
                <Alert variant="info">
                    <h4>Nenhum post encontrado</h4>
                    {posts.length === 0 ? (
                        <p>Você ainda não possui posts. Vá para <Link to="/themes">Temas</Link> para começar a gerar conteúdo.</p>
                    ) : (
                        <p>Tente ajustar os filtros para encontrar o que procura.</p>
                    )}
                </Alert>
            ) : (
                <Row>
                    {filteredPosts.map((post) => (
                        <Col key={post.id} lg={6} xl={4} className="mb-4">
                            <Card className="h-100 shadow-sm">
                                <Card.Header>
                                    <div className="d-flex justify-content-between align-items-start">
                                        <div className="flex-grow-1">
                                            <h6 className="mb-1 text-truncate">
                                                <Link to={`/posts/${post.id}`} className="text-decoration-none">
                                                    {post.title || post.topic}
                                                </Link>
                                            </h6>
                                            <small className="text-muted">{getThemeName(post.theme)}</small>
                                        </div>
                                        <div className="text-end">
                                            {getStatusBadge(post.status)}
                                        </div>
                                    </div>
                                </Card.Header>
                                <Card.Body>
                                    <div className="mb-2">
                                        <Badge
                                            bg={post.post_type === 'article' ? 'primary' : 'info'}
                                            className="me-2"
                                        >
                                            {post.post_type === 'article' ? 'Artigo' : 'Post Simples'}
                                        </Badge>
                                        {post.is_processing && (
                                            <Badge bg="warning">Processando</Badge>
                                        )}
                                    </div>

                                    {post.content_preview && (
                                        <p className="text-muted small mb-2" style={{ fontSize: '0.85rem' }}>
                                            {post.content_preview.substring(0, 100)}...
                                        </p>
                                    )}

                                    <div className="mb-2">
                                        <small className="text-muted">
                                            Criado em {formatDate(post.created_at)}
                                        </small>
                                        {post.ai_model_used && (
                                            <div>
                                                <small className="text-muted">
                                                    Modelo: {post.ai_model_used}
                                                </small>
                                            </div>
                                        )}
                                    </div>
                                </Card.Body>
                                <Card.Footer>
                                    <div className="d-grid gap-1">
                                        <Link
                                            to={`/posts/${post.id}`}
                                            className="btn btn-outline-primary btn-sm"
                                        >
                                            Ver Detalhes
                                        </Link>

                                        <div className="btn-group" role="group">
                                            {post.status !== 'published' && !post.is_processing && (
                                                <>
                                                    <Button
                                                        variant="outline-success"
                                                        size="sm"
                                                        onClick={() => handleImprovePost(post.id)}
                                                        disabled={processingPosts.has(post.id)}
                                                    >
                                                        {processingPosts.has(post.id) ? (
                                                            <Spinner as="span" animation="border" size="sm" />
                                                        ) : (
                                                            '✨ Melhorar'
                                                        )}
                                                    </Button>

                                                    {post.post_type === 'article' && (
                                                        <Button
                                                            variant="outline-info"
                                                            size="sm"
                                                            onClick={() => handleRegenerateImagePrompt(post.id)}
                                                            disabled={processingPosts.has(post.id)}
                                                        >
                                                            {processingPosts.has(post.id) ? (
                                                                <Spinner as="span" animation="border" size="sm" />
                                                            ) : (
                                                                '🖼️ Imagem'
                                                            )}
                                                        </Button>
                                                    )}

                                                    <Button
                                                        variant="success"
                                                        size="sm"
                                                        onClick={() => handlePublishPost(post.id)}
                                                    >
                                                        🚀 Publicar
                                                    </Button>
                                                </>
                                            )}

                                            {post.status === 'published' && (
                                                <Badge bg="success" className="w-100 py-2">
                                                    ✅ Publicado
                                                </Badge>
                                            )}
                                        </div>
                                    </div>
                                </Card.Footer>
                            </Card>
                        </Col>
                    ))}
                </Row>
            )}

            {/* Toast para notificações */}
            <ToastContainer position="bottom-end" className="p-3">
                <Toast
                    show={showToast}
                    onClose={() => setShowToast(false)}
                    delay={5000}
                    autohide
                    bg={toastVariant}
                >
                    <Toast.Body className="text-white">
                        {toastMessage}
                    </Toast.Body>
                </Toast>
            </ToastContainer>
        </Container>
    );
};

export default PostsPage;
