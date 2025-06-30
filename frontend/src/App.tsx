import React, { useState } from 'react';
import { SearchForm } from './components/SearchForm';
import { BiasVisualization } from './components/BiasVisualization';
import { analyzeArticleDetailed } from './services/api';
import { AnalysisResult } from './types';
import { AlertTriangle, CheckCircle, Clock, ExternalLink, BarChart3, Shield, AlertCircle, FileText, Users, Star, Brain } from 'lucide-react';

function App() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (title: string, useAdvanced: boolean = true) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Use detailed analysis endpoint
      const response = await analyzeArticleDetailed(title, useAdvanced);
      
      if (response.success && response.final_result) {
        setResult(response.final_result);
      } else {
        setError(response.error_message || 'Erro desconhecido na análise');
      }
    } catch (err) {
      setError('Erro ao analisar artigo: ' + (err instanceof Error ? err.message : String(err)));
    } finally {
      setLoading(false);
    }
  };

  const getOverallRiskLevel = (score: number) => {
    if (score >= 0.7) return { label: 'ALTO', color: 'text-red-600', bg: 'bg-red-50 border-red-200', icon: AlertTriangle };
    if (score >= 0.4) return { label: 'MÉDIO', color: 'text-yellow-600', bg: 'bg-yellow-50 border-yellow-200', icon: AlertCircle };
    return { label: 'BAIXO', color: 'text-green-600', bg: 'bg-green-50 border-green-200', icon: Shield };
  };

  // Helper function to count actual biased segments from reformulated text
  const getBiasedSegmentsCount = () => {
    if (!result || !result.reformulated_text) return 0;
    
    const text = result.reformulated_text;
    if (!text.includes('Trecho original:')) return 0;
    
    return text.split('Trecho original:').slice(1).length;
  };

  const renderArticleHeader = () => {
    if (!result) return null;

    const riskLevel = getOverallRiskLevel(result.overall_bias_score);
    const RiskIcon = riskLevel.icon;
    const actualBiasedSegments = getBiasedSegmentsCount();

    return (
      <div className="bg-gradient-to-r from-white to-gray-50 rounded-xl shadow-lg border p-8 mb-8">
        <div className="flex items-start justify-between mb-6">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-blue-100 p-2 rounded-lg">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 leading-tight">
                  {result.article_title}
                </h2>
                <div className="flex items-center space-x-4 mt-2">
                  {result.ai_related ? (
                    <span className="inline-flex items-center text-green-600 bg-green-50 px-3 py-1 rounded-full text-sm font-medium">
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Relacionado à IA
                    </span>
                  ) : (
                    <span className="inline-flex items-center text-orange-600 bg-orange-50 px-3 py-1 rounded-full text-sm font-medium">
                      <Clock className="h-4 w-4 mr-1" />
                      Verificar relevância IA
                    </span>
                  )}
                  <a 
                    href={result.article_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-blue-600 hover:text-blue-800 bg-blue-50 px-3 py-1 rounded-full text-sm font-medium hover:bg-blue-100 transition-colors"
                  >
                    <ExternalLink className="h-4 w-4 mr-1" />
                    Ver artigo original
                  </a>
                </div>
              </div>
            </div>
          </div>
          
          <div className={`text-center p-6 rounded-xl border-2 ${riskLevel.bg}`}>
            <div className="flex justify-center mb-2">
              <RiskIcon className={`h-8 w-8 ${riskLevel.color}`} />
            </div>
            <div className={`text-3xl font-bold ${riskLevel.color} mb-1`}>
              {(result.overall_bias_score * 100).toFixed(0)}%
            </div>
            <div className="text-sm text-gray-600 mb-1">Score de Viés</div>
            <div className={`text-xs font-bold ${riskLevel.color}`}>
              RISCO {riskLevel.label}
            </div>
          </div>
        </div>

        {/* Clear Analysis Coverage Stats */}
        <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-xl p-6 mb-6 border border-blue-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">✅</div>
              <div className="text-lg font-semibold text-gray-900">Artigo Completo</div>
              <div className="text-sm text-gray-600">Todo o texto foi analisado em busca de viés</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600 mb-2">{actualBiasedSegments}</div>
              <div className="text-lg font-semibold text-gray-900">Segmentos com Viés</div>
              <div className="text-sm text-gray-600">Trechos que apresentaram problemas</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {result.bias_detected ? '⚠️' : '🎉'}
              </div>
              <div className="text-lg font-semibold text-gray-900">
                {result.bias_detected ? 'Viés Detectado' : 'Texto Limpo'}
              </div>
              <div className="text-sm text-gray-600">
                {result.bias_detected 
                  ? `${actualBiasedSegments} problema(s) encontrado(s)` 
                  : 'Nenhum viés significativo detectado'
                }
              </div>
            </div>
          </div>
          
          <div className="mt-4 text-center">
            <div className="inline-flex items-center px-4 py-2 bg-white rounded-full border border-blue-200">
              <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
              <span className="text-sm font-medium text-gray-700">
                Análise completa do artigo "{result.article_title}"
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderMetricsOverview = () => {
    if (!result || !result.metricas_quantitativas) return null;

    const metrics = result.metricas_quantitativas;

    return (
      <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
        <div className="flex items-center space-x-3 mb-6">
          <div className="bg-indigo-100 p-2 rounded-lg">
            <BarChart3 className="h-6 w-6 text-indigo-600" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-900">Métricas Quantitativas</h3>
            <p className="text-sm text-gray-600">Análise linguística detalhada do texto</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-blue-50 rounded-xl p-4 text-center border border-blue-200">
            <div className="text-2xl font-bold text-blue-600 mb-2">
              {metrics.polaridade_media ? (metrics.polaridade_media * 100).toFixed(0) + '%' : 'N/A'}
            </div>
            <div className="text-sm font-medium text-gray-700">Polaridade</div>
            <div className="text-xs text-gray-500">Tendência emocional</div>
          </div>
          
          <div className="bg-orange-50 rounded-xl p-4 text-center border border-orange-200">
            <div className="text-2xl font-bold text-orange-600 mb-2">
              {metrics.intensidade_emocional_media ? (metrics.intensidade_emocional_media * 100).toFixed(0) + '%' : 'N/A'}
            </div>
            <div className="text-sm font-medium text-gray-700">Intensidade</div>
            <div className="text-xs text-gray-500">Força emocional</div>
          </div>
          
          <div className="bg-green-50 rounded-xl p-4 text-center border border-green-200">
            <div className="text-2xl font-bold text-green-600 mb-2">
              {metrics.complexidade_media ? (metrics.complexidade_media * 100).toFixed(0) + '%' : 'N/A'}
            </div>
            <div className="text-sm font-medium text-gray-700">Complexidade</div>
            <div className="text-xs text-gray-500">Sofisticação linguística</div>
          </div>
          
          <div className="bg-purple-50 rounded-xl p-4 text-center border border-purple-200">
            <div className="text-2xl font-bold text-purple-600 mb-2">
              {metrics.score_formalidade_medio ? (metrics.score_formalidade_medio * 100).toFixed(0) + '%' : 'N/A'}
            </div>
            <div className="text-sm font-medium text-gray-700">Formalidade</div>
            <div className="text-xs text-gray-500">Registro linguístico</div>
          </div>
        </div>
      </div>
    );
  };

  const renderBiasVisualization = () => {
    if (!result) return null;
    
    return (
      <BiasVisualization 
        biasCategories={result.bias_categories || []}
        overallScore={result.overall_bias_score}
      />
    );
  };

  const renderBiasedSegments = () => {
    if (!result || !result.reformulated_text) return null;

    // Parse the reformulated text to extract original segments
    const segments: Array<{
      id: number;
      original: string;
      reformulated: string;
      biasType: string;
    }> = [];
    const text = result.reformulated_text;
    
    if (text.includes('Trecho original:')) {
      const parts = text.split('Trecho original:').slice(1);
      parts.forEach((part, index) => {
        const lines = part.trim().split('\n');
        if (lines.length >= 2) {
          const original = lines[0].trim();
          const reformulated = lines[1].replace('Versão reformulada:', '').trim();
          segments.push({
            id: index + 1,
            original,
            reformulated,
            // Try to determine bias type based on the order in bias_categories
            biasType: result.bias_categories?.[index] || 'linguagem_carregada'
          });
        }
      });
    }

    if (segments.length === 0) return null;

    const getBiasTypeInfo = (biasType: string) => {
      const types: Record<string, {
        label: string;
        color: string;
        iconColor: string;
        description: string;
      }> = {
        'linguagem_emocional': {
          label: 'Linguagem Emocional',
          color: 'bg-red-50 border-red-200 text-red-800',
          iconColor: 'bg-red-100 text-red-600',
          description: 'Uso de termos emocionalmente carregados'
        },
        'linguagem_carregada': {
          label: 'Linguagem Carregada',
          color: 'bg-orange-50 border-orange-200 text-orange-800',
          iconColor: 'bg-orange-100 text-orange-600',
          description: 'Termos que transmitem opinião ou julgamento'
        },
        'opiniao_como_fato': {
          label: 'Opinião como Fato',
          color: 'bg-purple-50 border-purple-200 text-purple-800',
          iconColor: 'bg-purple-100 text-purple-600',
          description: 'Apresentação de opiniões como se fossem fatos'
        },
        'termos_subjetivos': {
          label: 'Termos Subjetivos',
          color: 'bg-blue-50 border-blue-200 text-blue-800',
          iconColor: 'bg-blue-100 text-blue-600',
          description: 'Uso de linguagem subjetiva ou imprecisa'
        }
      };
      return types[biasType] || types['linguagem_carregada'];
    };

    return (
      <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
        <div className="flex items-center space-x-3 mb-6">
          <div className="bg-red-100 p-2 rounded-lg">
            <AlertTriangle className="h-6 w-6 text-red-600" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-900">Trechos com Viés Identificados</h3>
            <p className="text-sm text-gray-600">Segmentos específicos que foram detectados como tendenciosos</p>
          </div>
          <div className="ml-auto bg-red-100 px-3 py-1 rounded-full">
            <span className="text-sm font-medium text-red-800">{segments.length} encontrados</span>
          </div>
        </div>

        <div className="space-y-6">
          {segments.map((segment, index) => {
            const biasInfo = getBiasTypeInfo(segment.biasType);
            
            return (
              <div key={segment.id} className={`border-2 rounded-xl p-6 ${biasInfo.color}`}>
                <div className="flex items-start space-x-4">
                  <div className={`${biasInfo.iconColor} p-2 rounded-lg flex-shrink-0`}>
                    <AlertCircle className="h-5 w-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-3">
                      <span className="text-sm font-semibold">Trecho #{segment.id}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${biasInfo.iconColor}`}>
                        {biasInfo.label}
                      </span>
                    </div>
                    
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">📝 Texto Original (com viés):</h4>
                      <div className="bg-white rounded-lg p-4 border-2 border-dashed border-gray-300">
                        <p className="text-gray-800 italic leading-relaxed">
                          "{segment.original}"
                        </p>
                      </div>
                    </div>

                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">✨ Versão Neutra Sugerida:</h4>
                      <div className="bg-green-50 rounded-lg p-4 border-2 border-green-200">
                        <p className="text-green-800 leading-relaxed">
                          "{segment.reformulated}"
                        </p>
                      </div>
                    </div>

                    <div className="bg-white/50 rounded-lg p-3">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">🔍 Por que foi detectado como viés:</h4>
                      <p className="text-sm text-gray-600">{biasInfo.description}</p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-6 bg-blue-50 rounded-lg p-4 border border-blue-200">
          <div className="flex items-start space-x-3">
            <div className="bg-blue-100 p-1 rounded">
              <CheckCircle className="h-4 w-4 text-blue-600" />
            </div>
            <div>
              <h4 className="text-sm font-medium text-blue-900 mb-1">💡 Recomendação</h4>
              <p className="text-sm text-blue-800">
                Considere usar as versões reformuladas para tornar o texto mais neutro e objetivo, 
                mantendo a informação factual sem linguagem tendenciosa.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Detector de Viés em IA</h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Analise artigos da Wikipedia para identificar viéses e linguagem tendenciosa relacionada à Inteligência Artificial
          </p>
        </div>

        <SearchForm onAnalyze={handleAnalyze} loading={loading} />

        {error && (
          <div className="mt-8 max-w-4xl mx-auto">
            <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6 shadow-sm">
              <div className="flex items-center">
                <div className="bg-red-100 p-2 rounded-lg mr-4">
                  <AlertTriangle className="h-6 w-6 text-red-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-red-800">Erro na Análise</h3>
                  <p className="text-sm text-red-600 mt-1">{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {result && (
          <div className="mt-8 max-w-7xl mx-auto">
            {/* Article Header */}
            {renderArticleHeader()}

            {/* Quantitative Metrics */}
            {renderMetricsOverview()}

            {/* Bias Visualization */}
            {renderBiasVisualization()}

            {/* Biased Segments - Show specific text segments identified */}
            {renderBiasedSegments()}
          </div>
        )}
      </div>
    </div>
  );
}

export default App; 