import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          {/* Outras rotas serão adicionadas aqui */}
          <Route path="/themes" element={<div>Themes page coming soon...</div>} />
          <Route path="/posts" element={<div>Posts page coming soon...</div>} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
