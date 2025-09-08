import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
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
    ToastContainer
} from 'react-bootstrap';
import { Theme } from '../types/api';
import { themesApi, tasksApi } from '../services/api';

const ThemesPage: React.FC = () => {
    const [themes, setThemes] = useState<Theme[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newThemeTitle, setNewThemeTitle] = useState('');
    const [creatingTheme, setCreatingTheme] = useState(false);
    const [showToast, setShowToast] = useState(false);
    const [toastMessage, setToastMessage] = useState('');
    const [toastVariant, setToastVariant] = useState<'success' | 'danger'>('success');
    const [generatingTopics, setGeneratingTopics] = useState<number | null>(null);

    useEffect(() => {
        loadThemes();
    }, []);

    const loadThemes = async () => {
        try {
            setLoading(true);
            const data = await themesApi.getAll();
            setThemes(Array.isArray(data) ? data : []);
        } catch (error) {
            setError('Erro ao carregar temas');
            console.error('Error loading themes:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateTheme = async () => {
        if (!newThemeTitle.trim()) return;

        try {
            setCreatingTheme(true);
            const newTheme = await themesApi.create({ title: newThemeTitle });
            setThemes([newTheme, ...themes]);
            setNewThemeTitle('');
            setShowCreateModal(false);
            showToastMessage('Tema criado com sucesso!', 'success');
        } catch (error) {
            showToastMessage('Erro ao criar tema', 'danger');
            console.error('Error creating theme:', error);
        } finally {
            setCreatingTheme(false);
        }
    };

    const handleGenerateTopics = async (themeId: number) => {
        try {
            setGeneratingTopics(themeId);
            const response = await themesApi.generateTopics(themeId);
            showToastMessage('Geração de tópicos iniciada! Aguarde...', 'success');

            // Monitora o progresso da tarefa
            setTimeout(() => checkTaskStatus(response.task_id, themeId), 2000);
        } catch (error) {
            showToastMessage('Erro ao gerar tópicos', 'danger');
            console.error('Error generating topics:', error);
            setGeneratingTopics(null);
        }
    };

    const checkTaskStatus = async (taskId: string, themeId: number) => {
        try {
            const status = await tasksApi.checkStatus(taskId);

            if (status.state === 'SUCCESS') {
                setGeneratingTopics(null);
                loadThemes(); // Recarrega para mostrar os tópicos gerados
                showToastMessage('Tópicos gerados com sucesso!', 'success');
            } else if (status.state === 'FAILURE') {
                setGeneratingTopics(null);
                showToastMessage('Erro ao gerar tópicos', 'danger');
            } else if (status.state === 'PENDING' || status.state === 'STARTED') {
                // Continua monitorando
                setTimeout(() => checkTaskStatus(taskId, themeId), 3000);
            }
        } catch (error) {
            setGeneratingTopics(null);
            showToastMessage('Erro ao verificar status da tarefa', 'danger');
        }
    };

    const showToastMessage = (message: string, variant: 'success' | 'danger') => {
        setToastMessage(message);
        setToastVariant(variant);
        setShowToast(true);
    };

    const getStatusBadge = (theme: Theme) => {
        if (theme.is_processing) {
            return <Badge bg="warning">Processando</Badge>;
        }
        if (theme.suggested_topics && theme.suggested_topics.topics?.length > 0) {
            return <Badge bg="success">Tópicos Gerados</Badge>;
        }
        return <Badge bg="secondary">Sem Tópicos</Badge>;
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('pt-BR');
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
            <Row className="mb-4">
                <Col>
                    <div className="d-flex justify-content-between align-items-center">
                        <h1>Temas</h1>
                        <Button
                            variant="primary"
                            onClick={() => setShowCreateModal(true)}
                            size="lg"
                        >
                            + Novo Tema
                        </Button>
                    </div>
                </Col>
            </Row>

            {themes.length === 0 ? (
                <Row>
                    <Col>
                        <Alert variant="info">
                            <h4>Nenhum tema encontrado</h4>
                            <p>Comece criando seu primeiro tema para gerar conteúdo.</p>
                            <Button variant="primary" onClick={() => setShowCreateModal(true)}>
                                Criar Primeiro Tema
                            </Button>
                        </Alert>
                    </Col>
                </Row>
            ) : (
                <Row>
                    {themes.map((theme) => (
                        <Col key={theme.id} lg={4} md={6} sm={12} className="mb-4">
                            <Card className="h-100 shadow-sm">
                                <Card.Header className="d-flex justify-content-between align-items-center">
                                    <h5 className="mb-0 text-truncate">{theme.title}</h5>
                                    {getStatusBadge(theme)}
                                </Card.Header>
                                <Card.Body>
                                    <div className="mb-3">
                                        <small className="text-muted">
                                            Criado em {formatDate(theme.created_at)}
                                        </small>
                                    </div>

                                    <Row className="text-center mb-3">
                                        <Col>
                                            <div className="fs-4 fw-bold text-primary">{theme.posts_count}</div>
                                            <small className="text-muted">Posts Total</small>
                                        </Col>
                                        <Col>
                                            <div className="fs-4 fw-bold text-success">{theme.articles_count}</div>
                                            <small className="text-muted">Artigos</small>
                                        </Col>
                                        <Col>
                                            <div className="fs-4 fw-bold text-info">{theme.simple_posts_count}</div>
                                            <small className="text-muted">Posts Simples</small>
                                        </Col>
                                    </Row>

                                    {theme.suggested_topics && theme.suggested_topics.topics?.length > 0 && (
                                        <div className="mb-3">
                                            <Badge bg="success" className="me-1">
                                                {theme.suggested_topics.topics.length} tópicos gerados
                                            </Badge>
                                        </div>
                                    )}
                                </Card.Body>
                                <Card.Footer>
                                    <div className="d-grid gap-2">
                                        <Link to={`/themes/${theme.id}`} className="btn btn-outline-primary">
                                            Ver Detalhes
                                        </Link>
                                        {!theme.suggested_topics?.topics?.length && !theme.is_processing && (
                                            <Button
                                                variant="success"
                                                size="sm"
                                                onClick={() => handleGenerateTopics(theme.id)}
                                                disabled={generatingTopics === theme.id}
                                            >
                                                {generatingTopics === theme.id ? (
                                                    <>
                                                        <Spinner as="span" animation="border" size="sm" className="me-2" />
                                                        Gerando Tópicos...
                                                    </>
                                                ) : (
                                                    '🧠 Gerar Tópicos'
                                                )}
                                            </Button>
                                        )}
                                    </div>
                                </Card.Footer>
                            </Card>
                        </Col>
                    ))}
                </Row>
            )}

            {/* Modal para criar novo tema */}
            <Modal show={showCreateModal} onHide={() => setShowCreateModal(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>Novo Tema</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form>
                        <Form.Group>
                            <Form.Label>Título do Tema</Form.Label>
                            <Form.Control
                                type="text"
                                placeholder="Ex: Tecnologia e Inovação"
                                value={newThemeTitle}
                                onChange={(e) => setNewThemeTitle(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleCreateTheme()}
                            />
                            <Form.Text className="text-muted">
                                Escolha um título descritivo para o tema que será usado para gerar conteúdo.
                            </Form.Text>
                        </Form.Group>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowCreateModal(false)}>
                        Cancelar
                    </Button>
                    <Button
                        variant="primary"
                        onClick={handleCreateTheme}
                        disabled={!newThemeTitle.trim() || creatingTheme}
                    >
                        {creatingTheme ? (
                            <>
                                <Spinner as="span" animation="border" size="sm" className="me-2" />
                                Criando...
                            </>
                        ) : (
                            'Criar Tema'
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

export default ThemesPage;
