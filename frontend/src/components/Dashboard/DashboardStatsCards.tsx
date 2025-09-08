import React from 'react';
import { Row, Col, Card, ListGroup, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { DashboardStats } from '../../types/api';

interface DashboardStatsCardsProps {
    stats: DashboardStats;
}

const DashboardStatsCards: React.FC<DashboardStatsCardsProps> = ({ stats }) => {
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
        const variants: { [key: string]: string } = {
            'draft': 'secondary',
            'generated': 'info',
            'published': 'success',
            'scheduled': 'warning'
        };
        return variants[status] || 'secondary';
    };

    return (
        <>
            {/* Stats Cards */}
            <Row className="mb-4">
                <Col md={3}>
                    <Card className="text-center h-100">
                        <Card.Body>
                            <Card.Title className="text-primary">{stats.total_themes}</Card.Title>
                            <Card.Text>Active Themes</Card.Text>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={3}>
                    <Card className="text-center h-100">
                        <Card.Body>
                            <Card.Title className="text-info">{stats.total_posts}</Card.Title>
                            <Card.Text>Total Posts</Card.Text>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={3}>
                    <Card className="text-center h-100">
                        <Card.Body>
                            <Card.Title className="text-success">{stats.published_posts}</Card.Title>
                            <Card.Text>Published</Card.Text>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={3}>
                    <Card className="text-center h-100">
                        <Card.Body>
                            <Card.Title className="text-warning">{stats.draft_posts}</Card.Title>
                            <Card.Text>Drafts</Card.Text>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            {/* AI Service Info */}
            <Row className="mb-4">
                <Col>
                    <Card>
                        <Card.Body>
                            <Card.Title>AI Service Status</Card.Title>
                            <Badge bg="success" className="me-2">Active</Badge>
                            <span>Current Provider: <strong>{stats.ai_service}</strong></span>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            {/* Recent Activity */}
            <Row>
                <Col md={6}>
                    <Card>
                        <Card.Header>
                            <Card.Title className="mb-0">Recent Themes</Card.Title>
                        </Card.Header>
                        <Card.Body>
                            {stats.recent_themes.length === 0 ? (
                                <p className="text-muted">No themes yet</p>
                            ) : (
                                <ListGroup variant="flush">
                                    {stats.recent_themes.map(theme => (
                                        <ListGroup.Item key={theme.id} className="d-flex justify-content-between align-items-start">
                                            <div>
                                                <Link to={`/themes/${theme.id}`} className="text-decoration-none">
                                                    <strong>{theme.title}</strong>
                                                </Link>
                                                <div className="text-muted small">
                                                    {theme.posts_count} posts • Created {formatDate(theme.created_at)}
                                                </div>
                                            </div>
                                            <Badge
                                                bg={theme.is_processing ? 'warning' : 'secondary'}
                                                pill
                                            >
                                                {theme.is_processing ? 'Processing' : 'Ready'}
                                            </Badge>
                                        </ListGroup.Item>
                                    ))}
                                </ListGroup>
                            )}
                        </Card.Body>
                    </Card>
                </Col>

                <Col md={6}>
                    <Card>
                        <Card.Header>
                            <Card.Title className="mb-0">Recent Posts</Card.Title>
                        </Card.Header>
                        <Card.Body>
                            {stats.recent_posts.length === 0 ? (
                                <p className="text-muted">No posts yet</p>
                            ) : (
                                <ListGroup variant="flush">
                                    {stats.recent_posts.map(post => (
                                        <ListGroup.Item key={post.id} className="d-flex justify-content-between align-items-start">
                                            <div>
                                                <Link to={`/posts/${post.id}`} className="text-decoration-none">
                                                    <strong>{post.title}</strong>
                                                </Link>
                                                <div className="text-muted small">
                                                    {post.theme_title} • {post.post_type} • {formatDate(post.created_at)}
                                                </div>
                                            </div>
                                            <Badge bg={getStatusBadge(post.status)} pill>
                                                {post.status}
                                            </Badge>
                                        </ListGroup.Item>
                                    ))}
                                </ListGroup>
                            )}
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </>
    );
};

export default DashboardStatsCards;
