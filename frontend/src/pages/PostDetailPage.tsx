import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Container,
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
    ToastContainer
} from 'react-bootstrap';
import ReactMarkdown from 'react-markdown';
import { Post } from '../types/post';
import { Theme } from '../types/theme';
import Layout from '../components/Layout';

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

    useEffect(() => {
        if (id) {
            fetchPost();
        }
    }, [id]);

    const fetchPost = async () => {
        try {
            setLoading(true);
            const response = await fetch(`http://localhost:8000/api/posts/${id}/`);

            if (!response.ok) {
                throw new Error(`Erro: ${response.status}`);
            }

            const postData = await response.json();
            setPost(postData);
            setEditData(postData);

            // Buscar detalhes do tema
            if (postData.theme) {
                const themeResponse = await fetch(`http://localhost:8000/api/themes/${postData.theme}/`);
                if (themeResponse.ok) {
                    const themeData = await themeResponse.json();
                    setTheme(themeData);
                }
            }
        } catch (err) {
            console.error('Erro ao buscar post:', err);
            setError('Erro ao carregar post');
        } finally {
            setLoading(false);
        }
    };

    const showToastMessage = (message: string, variant: 'success' | 'danger' = 'success') => {
        setToastMessage(message);
        setToastVariant(variant);
        setShowToast(true);
    };

    const copyToClipboard = async (text: string, fieldName: string) => {
        try {
            await navigator.clipboard.writeText(text);
            showToastMessage(`${fieldName} copiado para a área de transferência!`);
        } catch (err) {
            showToastMessage(`Erro ao copiar ${fieldName}`, 'danger');
        }
    };

    const handleUpdatePost = async () => {
        if (!post) return;

        try {
            setUpdating(true);
            const response = await fetch(`http://localhost:8000/api/posts/${post.id}/`, {
                method: 'PUT',
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
            showToastMessage('Post atualizado com sucesso!');
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
            const response = await fetch(`http://localhost:8000/api/posts/${post.id}/improve/`, {
                method: 'POST',
            });

            if (!response.ok) {
                throw new Error('Erro ao melhorar post');
            }

            showToastMessage('Post sendo melhorado em segundo plano');
            // Recarregar post após alguns segundos
            setTimeout(fetchPost, 3000);
        } catch (err) {
            console.error('Erro ao melhorar post:', err);
            showToastMessage('Erro ao melhorar post', 'danger');
        } finally {
            setImproving(false);
        }
    };

    const handleGenerateImage = async () => {
        if (!post) return;

        try {
            setGenerating(true);
            const response = await fetch(`http://localhost:8000/api/posts/${post.id}/generate-image/`, {
                method: 'POST',
            });

            if (!response.ok) {
                throw new Error('Erro ao gerar imagem');
            }

            showToastMessage('Imagem sendo gerada em segundo plano');
            // Recarregar post após alguns segundos
            setTimeout(fetchPost, 3000);
        } catch (err) {
            console.error('Erro ao gerar imagem:', err);
            showToastMessage('Erro ao gerar imagem', 'danger');
        } finally {
            setGenerating(false);
        }
    };

    const getStatusBadge = (status: string) => {
        const statusConfig = {
            draft: { variant: 'secondary', text: 'Rascunho' },
            generated: { variant: 'success', text: 'Gerado' },
            scheduled: { variant: 'primary', text: 'Agendado' },
            published: { variant: 'info', text: 'Publicado' }
        };

        const config = statusConfig[status as keyof typeof statusConfig] ||
            { variant: 'secondary', text: status };

        return <Badge bg={config.variant}>{config.text}</Badge>;
    };

    if (loading) {
        return (
            <Layout>
                <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
                    <Spinner animation="border" role="status">
                        <span className="visually-hidden">Carregando...</span>
                    </Spinner>
                </Container>
            </Layout>
        );
    }

    if (error || !post) {
        return (
            <Layout>
                <Container className="mt-4">
                    <Alert variant="danger">
                        {error || 'Post não encontrado'}
                    </Alert>
                    <Button variant="outline-primary" onClick={() => navigate('/posts')}>
                        Voltar para Posts
                    </Button>
                </Container>
            </Layout>
        );
    }

    return (
        <Layout>
            <Container className="mt-4">
                <Row>
                    {/* Breadcrumb */}
                    <Col xs={12} className="mb-3">
                        <Breadcrumb>
                            <Breadcrumb.Item href="/">Home</Breadcrumb.Item>
                            <Breadcrumb.Item href="/posts">Posts</Breadcrumb.Item>
                            <Breadcrumb.Item active>{post.title}</Breadcrumb.Item>
                        </Breadcrumb>
                    </Col>

                    {/* Conteúdo Principal */}
                    <Col lg={8} md={12} className="mb-4">
                        {/* Header do Post */}
                        <Card className="mb-4">
                            <Card.Body>
                                <div className="d-flex justify-content-between align-items-start mb-3">
                                    <div>
                                        <h1 className="mb-2">{post.title}</h1>
                                        <div className="mb-2">
                                            {getStatusBadge(post.status)}
                                            {theme && (
                                                <Badge bg="outline-secondary" className="ms-2">
                                                    {theme.name}
                                                </Badge>
                                            )}
                                        </div>
                                        <small className="text-muted">
                                            Criado em: {new Date(post.created_at).toLocaleDateString()}
                                            {post.updated_at !== post.created_at && (
                                                <> • Atualizado em: {new Date(post.updated_at).toLocaleDateString()}</>
                                            )}
                                        </small>
                                    </div>
                                </div>
                            </Card.Body>
                        </Card>

                        {/* Conteúdo do Post */}
                        <Card className="mb-4">
                            <Card.Header>
                                <h5>Conteúdo</h5>
                            </Card.Header>
                            <Card.Body>
                                <ReactMarkdown>{post.content}</ReactMarkdown>
                            </Card.Body>
                        </Card>

                        {/* Post Promocional */}
                        {post.promotional_post && (
                            <Card className="mb-4">
                                <Card.Header className="d-flex justify-content-between align-items-center">
                                    <h5>Post Promocional</h5>
                                    <Button
                                        variant="outline-primary"
                                        size="sm"
                                        onClick={() => copyToClipboard(post.promotional_post!, 'Post promocional')}
                                    >
                                        Copiar
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
                                    <h5>SEO</h5>
                                </Card.Header>
                                <Card.Body>
                                    {post.seo_title && (
                                        <div className="mb-3">
                                            <div className="d-flex justify-content-between align-items-center">
                                                <strong>Título SEO:</strong>
                                                <Button
                                                    variant="outline-primary"
                                                    size="sm"
                                                    onClick={() => copyToClipboard(post.seo_title!, 'Título SEO')}
                                                >
                                                    Copiar
                                                </Button>
                                            </div>
                                            <p className="mb-0 mt-1">{post.seo_title}</p>
                                        </div>
                                    )}
                                    {post.seo_description && (
                                        <div>
                                            <div className="d-flex justify-content-between align-items-center">
                                                <strong>Descrição SEO:</strong>
                                                <Button
                                                    variant="outline-primary"
                                                    size="sm"
                                                    onClick={() => copyToClipboard(post.seo_description!, 'Descrição SEO')}
                                                >
                                                    Copiar
                                                </Button>
                                            </div>
                                            <p className="mb-0 mt-1">{post.seo_description}</p>
                                        </div>
                                    )}
                                </Card.Body>
                            </Card>
                        )}

                        {/* Prompt de Imagem */}
                        {post.cover_image_prompt && (
                            <Card className="mb-4">
                                <Card.Header className="d-flex justify-content-between align-items-center">
                                    <h6>Prompt de Imagem</h6>
                                    <Button
                                        variant="outline-primary"
                                        size="sm"
                                        onClick={() => copyToClipboard(post.cover_image_prompt!, 'Prompt de imagem')}
                                    >
                                        Copiar
                                    </Button>
                                </Card.Header>
                                <Card.Body>
                                    <small className="text-muted">
                                        {post.cover_image_prompt}
                                    </small>
                                </Card.Body>
                            </Card>
                        )}

                        {/* Prompt de Geração */}
                        {post.generation_prompt && (
                            <Card>
                                <Card.Header>
                                    <h6>Prompt de Geração</h6>
                                </Card.Header>
                                <Card.Body>
                                    <small className="text-muted">
                                        {post.generation_prompt}
                                    </small>
                                </Card.Body>
                            </Card>
                        )}
                    </Col>

                    {/* Sidebar com Ações */}
                    <Col lg={4} md={12}>
                        <Card className="position-sticky" style={{ top: '20px' }}>
                            <Card.Header>
                                <h5>Ações</h5>
                            </Card.Header>
                            <Card.Body>
                                <div className="d-grid gap-2">
                                    <Button
                                        variant="primary"
                                        onClick={() => setShowEditModal(true)}
                                    >
                                        Editar Post
                                    </Button>

                                    <Button
                                        variant="warning"
                                        onClick={handleImprovePost}
                                        disabled={improving}
                                    >
                                        {improving ? (
                                            <>
                                                <Spinner as="span" animation="border" size="sm" className="me-2" />
                                                Melhorando...
                                            </>
                                        ) : (
                                            'Melhorar Post'
                                        )}
                                    </Button>

                                    <Button
                                        variant="info"
                                        onClick={handleGenerateImage}
                                        disabled={generating}
                                    >
                                        {generating ? (
                                            <>
                                                <Spinner as="span" animation="border" size="sm" className="me-2" />
                                                Gerando...
                                            </>
                                        ) : (
                                            'Gerar Imagem'
                                        )}
                                    </Button>

                                    <Button
                                        variant="success"
                                        disabled={post.status === 'published'}
                                    >
                                        {post.status === 'published' ? 'Publicado' : 'Publicar'}
                                    </Button>

                                    <hr />

                                    <Button
                                        variant="outline-secondary"
                                        onClick={() => navigate('/posts')}
                                    >
                                        Voltar para Posts
                                    </Button>
                                </div>
                            </Card.Body>
                        </Card>
                    </Col>
                </Row>

                {/* Modal para editar post */}
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
                                    value={editData.title || ''}
                                    onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Conteúdo</Form.Label>
                                <Form.Control
                                    as="textarea"
                                    rows={10}
                                    value={editData.content || ''}
                                    onChange={(e) => setEditData({ ...editData, content: e.target.value })}
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Post Promocional</Form.Label>
                                <Form.Control
                                    as="textarea"
                                    rows={4}
                                    value={editData.promotional_post || ''}
                                    onChange={(e) => setEditData({ ...editData, promotional_post: e.target.value })}
                                />
                            </Form.Group>

                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Título SEO</Form.Label>
                                        <Form.Control
                                            type="text"
                                            value={editData.seo_title || ''}
                                            onChange={(e) => setEditData({ ...editData, seo_title: e.target.value })}
                                        />
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Status</Form.Label>
                                        <Form.Select
                                            value={editData.status || ''}
                                            onChange={(e) => setEditData({ ...editData, status: e.target.value as Post['status'] })}
                                        >
                                            <option value="draft">Rascunho</option>
                                            <option value="generated">Gerado</option>
                                            <option value="scheduled">Agendado</option>
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                            </Row>

                            <Form.Group className="mb-3">
                                <Form.Label>Descrição SEO</Form.Label>
                                <Form.Control
                                    as="textarea"
                                    rows={3}
                                    value={editData.seo_description || ''}
                                    onChange={(e) => setEditData({ ...editData, seo_description: e.target.value })}
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Link</Form.Label>
                                <Form.Control
                                    type="url"
                                    value={editData.link || ''}
                                    onChange={(e) => setEditData({ ...editData, link: e.target.value })}
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
                            {updating ? (
                                <>
                                    <Spinner as="span" animation="border" size="sm" className="me-2" />
                                    Salvando...
                                </>
                            ) : (
                                'Salvar Alterações'
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
        </Layout>
    );
};

export default PostDetailPage;