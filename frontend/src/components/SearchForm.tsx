import React, { useState } from 'react';
import { Search, Brain, Zap, Sparkles, ArrowRight } from 'lucide-react';

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
    'Deep learning',
    'Processamento de linguagem natural'
  ];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Main Search Card */}
      <div className="bg-white/90 backdrop-blur-lg rounded-3xl shadow-2xl border border-white/50 p-8 lg:p-12 relative overflow-hidden">
        {/* Background decorations */}
        <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-bl from-blue-100/50 to-transparent rounded-full -mr-20 -mt-20"></div>
        <div className="absolute bottom-0 left-0 w-32 h-32 bg-gradient-to-tr from-purple-100/50 to-transparent rounded-full -ml-16 -mb-16"></div>
        
        <div className="relative">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center mb-6">
              <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-4 rounded-2xl shadow-lg mr-4">
                <Brain className="h-10 w-10 text-white" />
              </div>
              <div className="text-left">
                <h2 className="text-3xl lg:text-4xl font-black text-gray-900 mb-2">
                  Analisador de Artigos
                </h2>
                <div className="flex items-center space-x-2 text-gray-600">
                  <Sparkles className="h-5 w-5 text-blue-500" />
                  <span className="text-lg font-semibold">Wikipedia + IA</span>
                </div>
              </div>
            </div>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Insira o título de um artigo da Wikipedia sobre <span className="text-blue-600 font-bold">Inteligência Artificial</span> 
              para uma análise detalhada de viés textual
            </p>
          </div>

          {/* Search Form */}
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Input Field */}
            <div className="relative">
              <label htmlFor="article-title" className="block text-lg font-bold text-gray-800 mb-4">
                Título do Artigo da Wikipedia
              </label>
              <div className="relative group">
                <input
                  id="article-title"
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Ex: Inteligência Artificial, Machine Learning, Deep Learning..."
                  className="w-full px-6 py-4 pl-14 pr-6 bg-white border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-300 text-lg placeholder-gray-400 shadow-sm group-hover:shadow-md"
                  disabled={loading}
                />
                <div className="absolute left-4 top-1/2 -translate-y-1/2">
                  <Search className="h-6 w-6 text-gray-400 group-hover:text-blue-500 transition-colors duration-300" />
                </div>
              </div>
            </div>

            {/* Advanced Options */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border-2 border-blue-100">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-4">
                  <div className="bg-gradient-to-r from-blue-500 to-indigo-500 p-2 rounded-xl">
                    <Zap className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <label htmlFor="advanced-detector" className="text-lg font-bold text-gray-800 cursor-pointer">
                      Detector Avançado
                    </label>
                    <p className="text-sm text-gray-600 mt-1">
                      Análise completa com NLP avançado e múltiplos tipos de viés
                    </p>
                  </div>
                </div>
                <div className="relative">
                  <input
                    id="advanced-detector"
                    type="checkbox"
                    checked={useAdvanced}
                    onChange={(e) => setUseAdvanced(e.target.checked)}
                    className="sr-only"
                  />
                  <div 
                    onClick={() => setUseAdvanced(!useAdvanced)}
                    className={`w-14 h-8 rounded-full cursor-pointer transition-all duration-300 ${
                      useAdvanced 
                        ? 'bg-gradient-to-r from-blue-500 to-indigo-500 shadow-lg' 
                        : 'bg-gray-300'
                    }`}
                  >
                    <div className={`w-6 h-6 rounded-full bg-white shadow-md transition-transform duration-300 mt-1 ${
                      useAdvanced ? 'translate-x-7' : 'translate-x-1'
                    }`}></div>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-gray-700">Métricas quantitativas</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-gray-700">Análise semântica avançada</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span className="text-gray-700">Detecção de múltiplos vieses</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  <span className="text-gray-700">Reformulação de texto</span>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !title.trim()}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-8 rounded-2xl hover:from-blue-700 hover:to-purple-700 focus:ring-4 focus:ring-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:hover:transform-none text-lg font-bold"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-3">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent"></div>
                  <span>Analisando artigo...</span>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center space-x-3">
                  <Search className="h-6 w-6" />
                  <span>Analisar Artigo</span>
                  <ArrowRight className="h-6 w-6" />
                </div>
              )}
            </button>
          </form>

          {/* Footer Info */}
          <div className="mt-8 text-center">
            <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-2xl p-6 border border-gray-200">
              <p className="text-sm text-gray-600 mb-4 font-medium">
                ✨ <strong>Dica:</strong> Artigos devem ser relacionados à IA e estar disponíveis na Wikipedia em português
              </p>
              <div className="flex items-center justify-center space-x-6 text-xs text-gray-500">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Análise Instantânea</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span>Alta Precisão</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span>Relatórios Detalhados</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Example Articles */}
      <div className="mt-8 text-center">
        <p className="text-lg font-bold text-gray-700 mb-6">💡 Exemplos de artigos para testar:</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {exampleTitles.map((example, index) => (
            <button
              key={example}
              onClick={() => setTitle(example)}
              className="group p-4 bg-white/80 backdrop-blur-sm border-2 border-gray-200 rounded-2xl hover:border-blue-300 hover:bg-white transition-all duration-300 shadow-sm hover:shadow-md transform hover:-translate-y-1"
              disabled={loading}
            >
              <div className="text-sm font-bold text-gray-800 group-hover:text-blue-600 transition-colors duration-300">
                {example}
              </div>
              <div className="text-xs text-gray-500 mt-1 group-hover:text-blue-500 transition-colors duration-300">
                Clique para usar
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}; 