import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import PrivateRoute from './components/PrivateRoute';
import GenererPage from './pages/GenererPage';
import ProfilPage from './pages/ProfilPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

function Home() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-4xl font-serif mb-4">EnSoi</h1>
      <p className="text-ensoi-muted mb-6">
        Découvrez votre profil personnel à travers trois systèmes complémentaires.
      </p>
      <div className="flex gap-3">
        <Link to="/login" className="btn-secondary">Se connecter</Link>
        <Link to="/register" className="btn-primary">Créer un profil</Link>
      </div>
    </div>
  );
}

const Placeholder = ({ title }) => (
  <div className="container mx-auto p-6">
    <Link to="/" className="text-ensoi-primary hover:underline">← Retour</Link>
    <h2 className="text-2xl font-serif mt-4">{title}</h2>
    <p className="text-ensoi-muted mt-2">À implémenter dans la prochaine branche.</p>
  </div>
);

function NotFound() {
  return (
    <div className="container mx-auto p-6 text-center">
      <h1 className="text-6xl font-serif text-ensoi-primary">404</h1>
      <p className="text-ensoi-muted my-4">Cette page n'existe pas.</p>
      <Link to="/" className="btn-primary inline-block">Retour à l'accueil</Link>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/generer" element={<GenererPage />} />
          <Route path="/profils/:id" element={<ProfilPage />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Placeholder title="Mon historique" />
              </PrivateRoute>
            }
          />
          <Route path="/public/:token" element={<Placeholder title="Profil partagé" />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
