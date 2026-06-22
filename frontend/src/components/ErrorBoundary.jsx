import { Component } from 'react';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Erreur React capturée :', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center p-6 bg-ensoi-light">
          <div className="card max-w-md text-center">
            <h1 className="text-2xl font-serif text-ensoi-dark mb-3">
              Une erreur est survenue
            </h1>
            <p className="text-ensoi-muted mb-6">
              Quelque chose s'est mal passé. Vous pouvez réessayer en rechargeant la page.
            </p>
            {import.meta.env.DEV && this.state.error && (
              <pre className="text-left text-xs bg-gray-100 p-3 rounded mb-4 overflow-auto">
                {this.state.error.toString()}
              </pre>
            )}
            <button onClick={this.handleReset} className="btn-primary">
              Retour à l'accueil
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
