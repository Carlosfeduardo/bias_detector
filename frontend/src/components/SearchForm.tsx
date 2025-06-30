import React, { useState } from 'react';
import { Search, Brain, Zap } from 'lucide-react';

interface SearchFormProps {
  onAnalyze: (title: string, useAdvanced?: boolean) => void;
  loading: boolean;
}

export const SearchForm: React.FC<SearchFormProps> = ({ onAnalyze, loading }) => {
  const [title, setTitle] = useState('');
  const [useAdvanced, setUseAdvanced] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      onAnalyze(title.trim(), useAdvanced);
    }
  };

  const exampleTitles = [
    'Inteligência artificial',
    'Machine learning',
    'Redes neurais',
    'Aprendizado de máquina',
    'Deep learning'
  ];

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center mb-6">
          <div className="flex items-center justify-center mb-4">
            <Brain className="h-8 w-8 text-blue-600 mr-2" />
            <h1 className="text-2xl font-bold text-gray-900">
              Detector de Viés em IA
            </h1>
          </div>
          <p className="text-gray-600">
            Analise artigos da Wikipedia sobre Inteligência Artificial em busca de viés textual
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="article-title" className="block text-sm font-medium text-gray-700 mb-2">
              Título do Artigo da Wikipedia
            </label>
            <div className="relative">
              <input
                id="article-title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Ex: Inteligência Artificial, Machine Learning, Deep Learning..."
                className="w-full px-4 py-3 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />
              <Search className="absolute left-3 top-3.5 h-4 w-4 text-gray-400" />
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="advanced-detector"
                  type="checkbox"
                  checked={useAdvanced}
                  onChange={(e) => setUseAdvanced(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="advanced-detector" className="ml-2 block text-sm text-gray-700">
                  Usar Detector Avançado
                </label>
              </div>
              <Zap className="h-4 w-4 text-yellow-500" />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {useAdvanced 
                ? "Análise completa com NLP avançado, métricas quantitativas e mais tipos de viés"
                : "Análise básica com detecção de padrões fundamentais"
              }
            </p>
          </div>

          <button
            type="submit"
            disabled={loading || !title.trim()}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Analisando...
              </div>
            ) : (
              <div className="flex items-center justify-center">
                <Search className="h-4 w-4 mr-2" />
                Analisar Artigo
              </div>
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            Artigos devem ser relacionados à IA e estar disponíveis na Wikipedia em português
          </p>
        </div>
      </div>

      <div className="text-center mt-6">
        <p className="text-sm text-gray-500 mb-3">Exemplos de artigos para testar:</p>
        <div className="flex flex-wrap justify-center gap-2">
          {exampleTitles.map((example) => (
            <button
              key={example}
              onClick={() => setTitle(example)}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}; 