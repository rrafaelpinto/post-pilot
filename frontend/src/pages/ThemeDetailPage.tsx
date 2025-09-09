import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
    Container,
    Row,
    Col,
    Card,
    Button,
    Badge,
    Spinner,
    Alert,
    Modal,
    Form,
    Toast,
    ToastContainer,
    ListGroup
} from 'react-bootstrap';
import { Theme, Post, Topic } from '../types/api';
import { themesApi, tasksApi } from '../services/api';

const ThemeDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [theme, setTheme] = useState<Theme | null>(null);
    const [posts, setPosts] = useState<Post[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showGenerateModal, setShowGenerateModal] = useState(false);
    const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
    const [selectedPostType, setSelectedPostType] = useState<'simple' | 'article'>('simple');
    const [generatingPost, setGeneratingPost] = useState(false);
    const [generatingTopics, setGeneratingTopics] = useState(false);
    const [showToast, setShowToast] = useState(false);
    const [toastMessage, setToastMessage] = useState('');
    const [toastVariant, setToastVariant] = useState<'success' | 'danger'>('success');
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [deleting, setDeleting] = useState(false);

    useEffect(() => {
        if (id) {
            loadThemeData(parseInt(id));
        }
    }, [id]);

    const loadThemeData = async (themeId: number) => {
        try {
            setLoading(true);
            const [themeData, postsData] = await Promise.all([
                themesApi.getById(themeId),
                themesApi.getPosts(themeId)
            ]);
            setTheme(themeData);
            setPosts(Array.isArray(postsData) ? postsData : []);
        } catch (error) {
            setError('Erro ao carregar dados do tema');
            console.error('Error loading theme data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateTopics = async () => {
        if (!theme) return;

        try {
            setGeneratingTopics(true);
            const response = await themesApi.generateTopics(theme.id);
            showToastMessage('Geração de tópicos iniciada!', 'success');

            setTimeout(() => checkTaskStatus(response.task_id, 'topics'), 2000);
        } catch (error) {
            showToastMessage('Erro ao gerar tópicos', 'danger');
            console.error('Error generating topics:', error);
            setGeneratingTopics(false);
        }
    };

    const handleGeneratePost = async () => {
        if (!theme || !selectedTopic) return;

        try {
            setGeneratingPost(true);
            const response = await themesApi.generatePost(theme.id, {
                topic: selectedTopic.hook || 'Tópico sem título',
                post_type: selectedPostType,
                topic_data: selectedTopic
            });

            setShowGenerateModal(false);
            showToastMessage('Geração de post iniciada!', 'success');

            setTimeout(() => checkTaskStatus(response.task_id, 'post'), 2000);
        } catch (error) {
            showToastMessage('Erro ao gerar post', 'danger');
            console.error('Error generating post:', error);
            setGeneratingPost(false);
        }
    };

    const checkTaskStatus = async (taskId: string, type: 'topics' | 'post') => {
        try {
            const status = await tasksApi.checkStatus(taskId);

            if (status.state === 'SUCCESS') {
                if (type === 'topics') {
                    setGeneratingTopics(false);
                    if (theme) loadThemeData(theme.id);
                    showToastMessage('Tópicos gerados com sucesso!', 'success');
                } else {
                    setGeneratingPost(false);
                    if (theme) loadThemeData(theme.id);
                    showToastMessage('Post gerado com sucesso!', 'success');
                }
            } else if (status.state === 'FAILURE') {
                setGeneratingTopics(false);
                setGeneratingPost(false);
                showToastMessage(`Erro ao gerar ${type === 'topics' ? 'tópicos' : 'post'}`, 'danger');
            } else if (status.state === 'PENDING' || status.state === 'STARTED') {
                setTimeout(() => checkTaskStatus(taskId, type), 3000);
            }
        } catch (error) {
            setGeneratingTopics(false);
            setGeneratingPost(false);
            showToastMessage('Erro ao verificar status da tarefa', 'danger');
        }
    };

    const showToastMessage = (message: string, variant: 'success' | 'danger') => {
        setToastMessage(message);
        setToastVariant(variant);
        setShowToast(true);
    };

    const handleDeleteTheme = async () => {
        if (!theme) return;

        try {
            setDeleting(true);
            await themesApi.delete(theme.id);
            showToastMessage('Tema removido com sucesso!', 'success');
            setShowDeleteModal(false);

            // Redirecionar para a página de temas após 1 segundo
            setTimeout(() => {
                navigate('/themes');
            }, 1000);
        } catch (error) {
            showToastMessage('Erro ao remover tema', 'danger');
            console.error('Error deleting theme:', error);
        } finally {
            setDeleting(false);
        }
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

    if (loading) {
        return (
            <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '50vh' }}>
                <Spinner animation="border" role="status">
                    <span className="visually-hidden">Carregando...</span>
                </Spinner>
            </Container>
        );
    }

    if (error || !theme) {
        return (
            <Container>
                <Alert variant="danger">
                    {error || 'Tema não encontrado'}
                    <div className="mt-2">
                        <Button variant="outline-danger" onClick={() => navigate('/themes')}>
                            Voltar para Temas
                        </Button>
                    </div>
                </Alert>
            </Container>
        );
    }

    return (
        <Container fluid>
            {/* Header */}
            <Row className="mb-4">
                <Col>
                    <div className="d-flex justify-content-between align-items-center">
                        <div>
                            <nav aria-label="breadcrumb">
                                <ol className="breadcrumb">
                                    <li className="breadcrumb-item">
                                        <Link to="/themes">Temas</Link>
                                    </li>
                                    <li className="breadcrumb-item active">{theme.title}</li>
                                </ol>
                            </nav>
                            <h1>{theme.title}</h1>
                        </div>
                        <div>
                            {!theme.suggested_topics?.topics?.length && !theme.is_processing && (
                                <Button
                                    variant="success"
                                    onClick={handleGenerateTopics}
                                    disabled={generatingTopics}
                                    className="me-2"
                                >
                                    {generatingTopics ? (
                                        <>
                                            <Spinner as="span" animation="border" size="sm" className="me-2" />
                                            Gerando Tópicos...
                                        </>
                                    ) : (
                                        '🧠 Gerar Tópicos'
                                    )}
                                </Button>
                            )}
                            <div className="d-flex gap-2">
                                <Link to="/themes" className="btn btn-outline-secondary">
                                    Voltar
                                </Link>
                                <Button
                                    variant="outline-danger"
                                    onClick={() => setShowDeleteModal(true)}
                                    size="sm"
                                >
                                    🗑️ Remover Tema
                                </Button>
                            </div>
                        </div>
                    </div>
                </Col>
            </Row>

            {/* Estatísticas */}
            <Row className="mb-4">
                <Col lg={3} md={6} sm={6} className="mb-3">
                    <Card className="text-center">
                        <Card.Body>
                            <div className="fs-2 fw-bold text-primary">{theme.posts_count}</div>
                            <div className="text-muted">Posts Total</div>
                        </Card.Body>
                    </Card>
                </Col>
                <Col lg={3} md={6} sm={6} className="mb-3">
                    <Card className="text-center">
                        <Card.Body>
                            <div className="fs-2 fw-bold text-success">{theme.articles_count}</div>
                            <div className="text-muted">Artigos</div>
                        </Card.Body>
                    </Card>
                </Col>
                <Col lg={3} md={6} sm={6} className="mb-3">
                    <Card className="text-center">
                        <Card.Body>
                            <div className="fs-2 fw-bold text-info">{theme.simple_posts_count}</div>
                            <div className="text-muted">Posts Simples</div>
                        </Card.Body>
                    </Card>
                </Col>
                <Col lg={3} md={6} sm={6} className="mb-3">
                    <Card className="text-center">
                        <Card.Body>
                            <div className="fs-2 fw-bold text-warning">
                                {theme.suggested_topics?.topics?.length || 0}
                            </div>
                            <div className="text-muted">Tópicos</div>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            <Row>
                {/* Tópicos */}
                <Col lg={6} className="mb-4">
                    <Card>
                        <Card.Header>
                            <h5>Tópicos Sugeridos</h5>
                        </Card.Header>
                        <Card.Body>
                            {theme.suggested_topics?.topics?.length ? (
                                <div>
                                    <ListGroup variant="flush">
                                        {theme.suggested_topics.topics.map((topic, index) => (
                                            <ListGroup.Item key={index} className="px-0">
                                                <div className="d-flex justify-content-between align-items-start">
                                                    <div className="flex-grow-1">
                                                        <h6 className="mb-1">{topic.hook}</h6>
                                                        <p className="mb-1 text-muted">{topic.summary}</p>
                                                        <Badge bg="light" text="dark">{topic.post_type}</Badge>
                                                    </div>
                                                    <Button
                                                        variant="outline-primary"
                                                        size="sm"
                                                        onClick={() => {
                                                            setSelectedTopic(topic);
                                                            setShowGenerateModal(true);
                                                        }}
                                                    >
                                                        Gerar Post
                                                    </Button>
                                                </div>
                                            </ListGroup.Item>
                                        ))}
                                    </ListGroup>
                                    {theme.topics_generated_at && (
                                        <small className="text-muted">
                                            Gerados em {formatDate(theme.topics_generated_at)}
                                        </small>
                                    )}
                                </div>
                            ) : (
                                <Alert variant="info" className="mb-0">
                                    <p className="mb-0">Nenhum tópico gerado ainda.</p>
                                    {!theme.is_processing && (
                                        <Button
                                            variant="success"
                                            size="sm"
                                            className="mt-2"
                                            onClick={handleGenerateTopics}
                                            disabled={generatingTopics}
                                        >
                                            {generatingTopics ? 'Gerando...' : 'Gerar Tópicos'}
                                        </Button>
                                    )}
                                </Alert>
                            )}
                        </Card.Body>
                    </Card>
                </Col>

                {/* Posts */}
                <Col lg={6} className="mb-4">
                    <Card>
                        <Card.Header className="d-flex justify-content-between align-items-center">
                            <h5>Posts do Tema</h5>
                            <Link to="/posts" className="btn btn-outline-primary btn-sm">
                                Ver Todos os Posts
                            </Link>
                        </Card.Header>
                        <Card.Body>
                            {posts.length ? (
                                <div>
                                    <ListGroup variant="flush">
                                        {posts.slice(0, 5).map((post) => (
                                            <ListGroup.Item key={post.id} className="px-0">
                                                <div className="d-flex justify-content-between align-items-start">
                                                    <div className="flex-grow-1">
                                                        <h6 className="mb-1">
                                                            <Link to={`/posts/${post.id}`} className="text-decoration-none">
                                                                {post.title || post.topic}
                                                            </Link>
                                                        </h6>
                                                        <div className="mb-1">
                                                            {getStatusBadge(post.status)}
                                                            <Badge bg="light" text="dark" className="ms-2">
                                                                {post.post_type}
                                                            </Badge>
                                                        </div>
                                                        <small className="text-muted">
                                                            {formatDate(post.created_at)}
                                                        </small>
                                                    </div>
                                                </div>
                                            </ListGroup.Item>
                                        ))}
                                    </ListGroup>
                                    {posts.length > 5 && (
                                        <div className="text-center mt-3">
                                            <Link to={`/posts?theme=${theme.id}`} className="btn btn-outline-primary">
                                                Ver todos os {posts.length} posts
                                            </Link>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <Alert variant="info" className="mb-0">
                                    Nenhum post criado ainda. Gere tópicos e use-os para criar posts!
                                </Alert>
                            )}
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            {/* Modal para gerar post */}
            <Modal show={showGenerateModal} onHide={() => setShowGenerateModal(false)} size="lg">
                <Modal.Header closeButton>
                    <Modal.Title>Gerar Post</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {selectedTopic && (
                        <div>
                            <h6>Tópico Selecionado:</h6>
                            <Alert variant="light">
                                <strong>{selectedTopic.hook}</strong>
                                <p className="mb-0 mt-2">{selectedTopic.summary}</p>
                            </Alert>

                            <Form>
                                <Form.Group className="mb-3">
                                    <Form.Label>Tipo de Post</Form.Label>
                                    <div>
                                        <Form.Check
                                            type="radio"
                                            id="simple"
                                            label="Post Simples - Conteúdo curto para redes sociais"
                                            value="simple"
                                            checked={selectedPostType === 'simple'}
                                            onChange={(e) => setSelectedPostType('simple')}
                                        />
                                        <Form.Check
                                            type="radio"
                                            id="article"
                                            label="Artigo - Conteúdo detalhado e longo"
                                            value="article"
                                            checked={selectedPostType === 'article'}
                                            onChange={(e) => setSelectedPostType('article')}
                                        />
                                    </div>
                                </Form.Group>
                            </Form>
                        </div>
                    )}
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowGenerateModal(false)}>
                        Cancelar
                    </Button>
                    <Button
                        variant="primary"
                        onClick={handleGeneratePost}
                        disabled={generatingPost}
                    >
                        {generatingPost ? (
                            <>
                                <Spinner as="span" animation="border" size="sm" className="me-2" />
                                Gerando Post...
                            </>
                        ) : (
                            'Gerar Post'
                        )}
                    </Button>
                </Modal.Footer>
            </Modal>

            {/* Modal para confirmar deleção */}
            <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>Confirmar Remoção</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Alert variant="warning">
                        <Alert.Heading>⚠️ Atenção!</Alert.Heading>
                        <p>
                            Você está prestes a remover o tema <strong>"{theme?.title}"</strong>.
                        </p>
                        <p className="mb-0">
                            Esta ação também removerá <strong>todos os posts</strong> associados a este tema e <strong>não pode ser desfeita</strong>.
                        </p>
                    </Alert>
                    <p>Tem certeza que deseja continuar?</p>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
                        Cancelar
                    </Button>
                    <Button
                        variant="danger"
                        onClick={handleDeleteTheme}
                        disabled={deleting}
                    >
                        {deleting ? (
                            <>
                                <Spinner as="span" animation="border" size="sm" className="me-2" />
                                Removendo...
                            </>
                        ) : (
                            'Sim, Remover Tema'
                        )}
                    </Button>
                </Modal.Footer>
            </Modal>

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

export default ThemeDetailPage;
