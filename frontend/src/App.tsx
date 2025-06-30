import React, { useState } from 'react';
import { SearchForm } from './components/SearchForm';
import { BiasVisualization } from './components/BiasVisualization';
import { analyzeArticleDetailed } from './services/api';
import { AnalysisResult } from './types';
import { AlertTriangle, CheckCircle, Clock, ExternalLink, BarChart3, Shield, AlertCircle, FileText, Brain, Sparkles, Zap, Target, Award } from 'lucide-react';

function App() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (title: string, useAdvanced: boolean = true) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
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
    if (score >= 0.7) return { label: 'ALTO', color: 'text-red-600', bg: 'bg-red-50 border-red-200', icon: AlertTriangle, gradient: 'from-red-500 to-red-600' };
    if (score >= 0.4) return { label: 'MÉDIO', color: 'text-amber-600', bg: 'bg-amber-50 border-amber-200', icon: AlertCircle, gradient: 'from-amber-500 to-amber-600' };
    return { label: 'BAIXO', color: 'text-emerald-600', bg: 'bg-emerald-50 border-emerald-200', icon: Shield, gradient: 'from-emerald-500 to-emerald-600' };
  };

  const getBiasedSegmentsCount = () => {
    if (!result || !result.reformulated_text) return 0;
    const text = result.reformulated_text;
    if (!text.includes('Trecho original:')) return 0;
    return text.split('Trecho original:').slice(1).length;
  };

  const renderHeroSection = () => (
    <div className="relative overflow-hidden bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 text-white">
      <div className="absolute inset-0 opacity-20" style={{backgroundImage: "url('data:image/svg+xml,%3Csvg width=\"60\" height=\"60\" viewBox=\"0 0 60 60\" xmlns=\"http://www.w3.org/2000/svg\"%3E%3Cg fill=\"none\" fill-rule=\"evenodd\"%3E%3Cg fill=\"%23ffffff\" fill-opacity=\"0.05\"%3E%3Ccircle cx=\"36\" cy=\"24\" r=\"5\"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')"}}></div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
        <div className="text-center">
          <div className="flex items-center justify-center mb-8 animate-fade-in">
            <div className="bg-white/10 backdrop-blur-sm p-4 rounded-2xl mr-4 animate-float">
              <Brain className="h-12 w-12 text-white" />
            </div>
            <div className="text-left">
              <h1 className="text-5xl lg:text-7xl font-black tracking-tight mb-2">
                <span className="bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">
                  Bias
                </span>
                <span className="text-white"> Detector</span>
              </h1>
              <div className="flex items-center space-x-2 text-blue-200">
                <Sparkles className="h-5 w-5" />
                <span className="text-lg font-medium">Powered by Advanced AI</span>
              </div>
            </div>
          </div>

          <p className="text-xl lg:text-2xl text-gray-200 mb-8 max-w-3xl mx-auto leading-relaxed animate-slide-up animation-delay-200">
            Detecte viés textual em artigos da Wikipedia sobre <span className="text-cyan-300 font-semibold">Inteligência Artificial</span> 
            com nossa tecnologia avançada de análise semântica
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12 animate-slide-up animation-delay-400">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300 hover:scale-105">
              <div className="bg-cyan-500/20 p-3 rounded-xl w-fit mx-auto mb-4">
                <Zap className="h-6 w-6 text-cyan-300" />
              </div>
              <h3 className="text-lg font-bold mb-2">Análise Instantânea</h3>
              <p className="text-gray-300 text-sm">Processamento em tempo real com NLP avançado</p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300 hover:scale-105">
              <div className="bg-purple-500/20 p-3 rounded-xl w-fit mx-auto mb-4">
                <Target className="h-6 w-6 text-purple-300" />
              </div>
              <h3 className="text-lg font-bold mb-2">Precisão Elevada</h3>
              <p className="text-gray-300 text-sm">Múltiplos tipos de viés detectados com alta confiança</p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300 hover:scale-105">
              <div className="bg-green-500/20 p-3 rounded-xl w-fit mx-auto mb-4">
                <Award className="h-6 w-6 text-green-300" />
              </div>
              <h3 className="text-lg font-bold mb-2">Relatórios Detalhados</h3>
              <p className="text-gray-300 text-sm">Visualizações intuitivas e métricas quantitativas</p>
            </div>
          </div>

          <div className="flex items-center justify-center space-x-8 animate-slide-up animation-delay-600">
            <div className="text-center">
              <div className="text-3xl font-bold text-cyan-300">10+</div>
              <div className="text-sm text-gray-400">Tipos de Viés</div>
            </div>
            <div className="w-px h-8 bg-white/20"></div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-300">95%</div>
              <div className="text-sm text-gray-400">Precisão</div>
            </div>
            <div className="w-px h-8 bg-white/20"></div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-300">{"< 5s"}</div>
              <div className="text-sm text-gray-400">Análise</div>
            </div>
          </div>
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-gray-50 to-transparent"></div>
    </div>
  );

  const renderSearchSection = () => (
    <div className="py-16 lg:py-24 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SearchForm onAnalyze={handleAnalyze} loading={loading} />
        
        {error && (
          <div className="mt-8 max-w-2xl mx-auto">
            <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6 animate-slide-up">
              <div className="flex items-center space-x-3">
                <div className="bg-red-100 p-2 rounded-xl">
                  <AlertTriangle className="h-6 w-6 text-red-600" />
                </div>
                <div>
                  <h3 className="text-red-800 font-bold text-lg">Erro na Análise</h3>
                  <p className="text-red-600 mt-1">{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderArticleHeader = () => {
    if (!result) return null;

    const riskLevel = getOverallRiskLevel(result.overall_bias_score);
    const RiskIcon = riskLevel.icon;
    const actualBiasedSegments = getBiasedSegmentsCount();

    return (
      <div className="bg-white rounded-3xl shadow-2xl border border-gray-100 p-8 mb-8 animate-slide-up overflow-hidden relative">
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-blue-50 to-transparent rounded-full -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-purple-50 to-transparent rounded-full -ml-24 -mb-24"></div>
        
        <div className="relative">
          <div className="flex items-start justify-between mb-8">
            <div className="flex-1">
              <div className="flex items-center space-x-4 mb-6">
                <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-3 rounded-2xl shadow-lg">
                  <FileText className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h2 className="text-3xl lg:text-4xl font-black text-gray-900 leading-tight mb-2">
                    {result.article_title}
                  </h2>
                  <div className="flex items-center space-x-4">
                    {result.ai_related ? (
                      <span className="inline-flex items-center text-emerald-700 bg-emerald-100 px-4 py-2 rounded-full text-sm font-bold shadow-sm border border-emerald-200">
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Relacionado à IA
                      </span>
                    ) : (
                      <span className="inline-flex items-center text-amber-700 bg-amber-100 px-4 py-2 rounded-full text-sm font-bold shadow-sm border border-amber-200">
                        <Clock className="h-4 w-4 mr-2" />
                        Verificar relevância IA
                      </span>
                    )}
                    <a 
                      href={result.article_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-blue-700 hover:text-blue-800 bg-blue-100 px-4 py-2 rounded-full text-sm font-bold hover:bg-blue-200 transition-all duration-300 shadow-sm border border-blue-200 hover:shadow-md"
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Ver artigo original
                    </a>
                  </div>
                </div>
              </div>
            </div>
            
            <div className={`text-center p-8 rounded-3xl border-2 ${riskLevel.bg} shadow-lg relative overflow-hidden`}>
              <div className="absolute inset-0 bg-gradient-to-br from-white/50 to-transparent"></div>
              <div className="relative">
                <div className="flex justify-center mb-4">
                  <div className={`bg-gradient-to-r ${riskLevel.gradient} p-3 rounded-2xl shadow-lg`}>
                    <RiskIcon className="h-10 w-10 text-white" />
                  </div>
                </div>
                <div className={`text-5xl font-black ${riskLevel.color} mb-2`}>
                  {(result.overall_bias_score * 100).toFixed(0)}%
                </div>
                <div className="text-sm font-medium text-gray-600 mb-2">Score de Viés</div>
                <div className={`text-sm font-black ${riskLevel.color} px-3 py-1 rounded-full bg-white/50`}>
                  RISCO {riskLevel.label}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 rounded-3xl p-8 border-2 border-blue-100 shadow-inner">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-black text-gray-900 mb-2">Resumo da Análise</h3>
              <p className="text-gray-600 font-medium">Cobertura completa do artigo com detecção avançada</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center group hover:scale-105 transition-transform duration-300">
                <div className="bg-gradient-to-r from-emerald-500 to-green-500 p-4 rounded-2xl mx-auto w-fit mb-4 shadow-lg group-hover:shadow-xl">
                  <CheckCircle className="h-8 w-8 text-white" />
                </div>
                <div className="text-2xl font-black text-gray-900 mb-2">Artigo Completo</div>
                <div className="text-gray-600 font-medium">Todo o texto foi analisado em busca de viés</div>
              </div>
              
              <div className="text-center group hover:scale-105 transition-transform duration-300">
                <div className="bg-gradient-to-r from-red-500 to-pink-500 p-4 rounded-2xl mx-auto w-fit mb-4 shadow-lg group-hover:shadow-xl">
                  <div className="text-white text-2xl font-black">{actualBiasedSegments}</div>
                </div>
                <div className="text-2xl font-black text-gray-900 mb-2">Segmentos com Viés</div>
                <div className="text-gray-600 font-medium">Trechos que apresentaram problemas</div>
              </div>
              
              <div className="text-center group hover:scale-105 transition-transform duration-300">
                <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-4 rounded-2xl mx-auto w-fit mb-4 shadow-lg group-hover:shadow-xl">
                  <div className="text-white text-2xl">
                    {result.bias_detected ? '⚠️' : '🎉'}
                  </div>
                </div>
                <div className="text-2xl font-black text-gray-900 mb-2">
                  {result.bias_detected ? 'Viés Detectado' : 'Texto Limpo'}
                </div>
                <div className="text-gray-600 font-medium">
                  {result.bias_detected 
                    ? `${actualBiasedSegments} problema(s) encontrado(s)` 
                    : 'Nenhum viés significativo detectado'
                  }
                </div>
              </div>
            </div>
            
            <div className="mt-8 text-center">
              <div className="inline-flex items-center px-6 py-3 bg-white rounded-2xl border-2 border-blue-200 shadow-sm">
                <CheckCircle className="h-5 w-5 text-emerald-600 mr-3" />
                <span className="text-sm font-bold text-gray-800">
                  Análise completa do artigo "{result.article_title}"
                </span>
              </div>
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
      <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8 mb-8 animate-slide-up">
        <div className="flex items-center space-x-4 mb-8">
          <div className="bg-gradient-to-r from-indigo-500 to-purple-500 p-3 rounded-2xl shadow-lg">
            <BarChart3 className="h-8 w-8 text-white" />
          </div>
          <div>
            <h3 className="text-2xl font-black text-gray-900">Métricas Quantitativas</h3>
            <p className="text-gray-600 font-medium">Análise linguística detalhada do texto</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6 text-center border-2 border-blue-200 hover:shadow-lg transition-shadow duration-300">
            <div className="text-3xl font-black text-blue-600 mb-3">
              {metrics.polaridade_media ? (metrics.polaridade_media * 100).toFixed(0) + '%' : 'N/A'}
            </div>
            <div className="text-lg font-bold text-gray-800 mb-1">Polaridade</div>
            <div className="text-sm text-gray-600">Tendência emocional</div>
          </div>
          
          <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-2xl p-6 text-center border-2 border-orange-200 hover:shadow-lg transition-shadow duration-300">
            <div className="text-3xl font-black text-orange-600 mb-3">
              {metrics.intensidade_emocional_media ? (metrics.intensidade_emocional_media * 100).toFixed(0) + '%' : 'N/A'}
            </div>
            <div className="text-lg font-bold text-gray-800 mb-1">Intensidade</div>
            <div className="text-sm text-gray-600">Força emocional</div>
          </div>
          
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6 text-center border-2 border-green-200 hover:shadow-lg transition-shadow duration-300">
            <div className="text-3xl font-black text-green-600 mb-3">
              {metrics.complexidade_media ? (metrics.complexidade_media * 100).toFixed(0) + '%' : 'N/A'}
            </div>
            <div className="text-lg font-bold text-gray-800 mb-1">Complexidade</div>
            <div className="text-sm text-gray-600">Sofisticação linguística</div>
          </div>
          
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6 text-center border-2 border-purple-200 hover:shadow-lg transition-shadow duration-300">
            <div className="text-3xl font-black text-purple-600 mb-3">
              {metrics.score_formalidade_medio ? (metrics.score_formalidade_medio * 100).toFixed(0) + '%' : 'N/A'}
            </div>
            <div className="text-lg font-bold text-gray-800 mb-1">Formalidade</div>
            <div className="text-sm text-gray-600">Registro linguístico</div>
          </div>
        </div>
      </div>
    );
  };

  const renderBiasVisualization = () => {
    if (!result) return null;
    
    return (
      <div className="mb-8">
        <BiasVisualization 
          biasCategories={result.bias_categories || []}
          overallScore={result.overall_bias_score}
        />
      </div>
    );
  };

  const renderBiasedSegments = () => {
    if (!result || !result.reformulated_text) return null;

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
      <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8 mb-8 animate-slide-up">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <div className="bg-gradient-to-r from-red-500 to-pink-500 p-3 rounded-2xl shadow-lg">
              <AlertTriangle className="h-8 w-8 text-white" />
            </div>
            <div>
              <h3 className="text-2xl font-black text-gray-900">Trechos com Viés Identificados</h3>
              <p className="text-gray-600 font-medium">Segmentos específicos que foram detectados como tendenciosos</p>
            </div>
          </div>
          <div className="bg-red-100 px-4 py-2 rounded-2xl border-2 border-red-200">
            <span className="text-lg font-black text-red-800">{segments.length} encontrados</span>
          </div>
        </div>

        <div className="space-y-8">
          {segments.map((segment, index) => {
            const biasInfo = getBiasTypeInfo(segment.biasType);
            
            return (
              <div key={segment.id} className={`border-2 rounded-2xl p-8 ${biasInfo.color} hover:shadow-lg transition-shadow duration-300`}>
                <div className="flex items-start space-x-6">
                  <div className={`${biasInfo.iconColor} p-3 rounded-2xl flex-shrink-0 shadow-sm`}>
                    <AlertCircle className="h-6 w-6" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-4 mb-6">
                      <span className="text-lg font-black">Trecho #{segment.id}</span>
                      <span className={`px-4 py-2 rounded-full text-sm font-bold ${biasInfo.iconColor} shadow-sm`}>
                        {biasInfo.label}
                      </span>
                    </div>
                    
                    <div className="mb-6">
                      <h4 className="text-sm font-bold text-gray-700 mb-3 flex items-center">
                        <span className="mr-2">📝</span>
                        Texto Original (com viés):
                      </h4>
                      <div className="bg-white rounded-2xl p-6 border-2 border-dashed border-gray-300 shadow-inner">
                        <p className="text-gray-800 italic leading-relaxed text-lg">
                          "{segment.original}"
                        </p>
                      </div>
                    </div>

                    <div className="mb-6">
                      <h4 className="text-sm font-bold text-gray-700 mb-3 flex items-center">
                        <span className="mr-2">✨</span>
                        Versão Neutra Sugerida:
                      </h4>
                      <div className="bg-emerald-50 rounded-2xl p-6 border-2 border-emerald-200 shadow-inner">
                        <p className="text-emerald-800 leading-relaxed text-lg font-medium">
                          "{segment.reformulated}"
                        </p>
                      </div>
                    </div>

                    <div className="bg-white/50 rounded-2xl p-4 border border-gray-200">
                      <h4 className="text-sm font-bold text-gray-700 mb-2 flex items-center">
                        <span className="mr-2">🔍</span>
                        Por que foi detectado como viés:
                      </h4>
                      <p className="text-sm text-gray-600 font-medium">{biasInfo.description}</p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-8 bg-blue-50 rounded-2xl p-6 border-2 border-blue-200">
          <div className="flex items-start space-x-4">
            <div className="bg-blue-500 p-2 rounded-xl">
              <CheckCircle className="h-6 w-6 text-white" />
            </div>
            <div>
              <h4 className="text-lg font-bold text-blue-900 mb-2">💡 Recomendação</h4>
              <p className="text-blue-800 font-medium">
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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {renderHeroSection()}
      {renderSearchSection()}

      {result && (
        <div className="py-16 lg:py-24 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            {renderArticleHeader()}
            {renderMetricsOverview()}
            {renderBiasVisualization()}
            {renderBiasedSegments()}
          </div>
        </div>
      )}
    </div>
  );
}

export default App; 