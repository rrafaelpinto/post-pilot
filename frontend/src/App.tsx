import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import ThemesPage from './pages/ThemesPage';
import ThemeDetailPage from './pages/ThemeDetailPage';
import PostsPage from './pages/PostsPage';
import PostDetailPage from './pages/PostDetailPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/themes" element={<ThemesPage />} />
          <Route path="/themes/:id" element={<ThemeDetailPage />} />
          <Route path="/posts" element={<PostsPage />} />
          <Route path="/posts/:id" element={<PostDetailPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
