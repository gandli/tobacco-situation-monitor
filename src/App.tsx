import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/common/Layout';
import { Dashboard } from './pages/Dashboard';
import { CluesPage } from './pages/CluesPage';
import { ClueDetailPage } from './pages/ClueDetailPage';
import { CasesPage } from './pages/CasesPage';
import { GraphPage } from './pages/GraphPage';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/clues" element={<CluesPage />} />
          <Route path="/clues/:id" element={<ClueDetailPage />} />
          <Route path="/cases" element={<CasesPage />} />
          <Route path="/graph" element={<GraphPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;