import React from 'react';
import { Navbar, Nav, Container } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const location = useLocation();

    return (
        <>
            <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
                <Container>
                    <Navbar.Brand as={Link} to="/">
                        Post Pilot
                    </Navbar.Brand>
                    <Navbar.Toggle aria-controls="basic-navbar-nav" />
                    <Navbar.Collapse id="basic-navbar-nav">
                        <Nav className="me-auto">
                            <Nav.Link
                                as={Link}
                                to="/"
                                active={location.pathname === '/'}
                            >
                                Dashboard
                            </Nav.Link>
                            <Nav.Link
                                as={Link}
                                to="/themes"
                                active={location.pathname.startsWith('/themes')}
                            >
                                Themes
                            </Nav.Link>
                            <Nav.Link
                                as={Link}
                                to="/posts"
                                active={location.pathname.startsWith('/posts')}
                            >
                                Posts
                            </Nav.Link>
                        </Nav>
                        <Nav>
                            <Nav.Link href="http://localhost:8000/admin" target="_blank">
                                Admin
                            </Nav.Link>
                            <Nav.Link href="http://localhost:5555" target="_blank">
                                Flower
                            </Nav.Link>
                        </Nav>
                    </Navbar.Collapse>
                </Container>
            </Navbar>

            <Container className="mt-4">
                {children}
            </Container>
        </>
    );
};

export default Layout;
