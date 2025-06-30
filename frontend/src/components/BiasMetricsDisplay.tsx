import React from 'react';
import { BiasAnalysis, BiasTypeLabels, BiasTypeColors, AnalyzeResponse } from '../types';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Target, BarChart3, Shield, Zap, Brain, Eye, FileText } from 'lucide-react';

interface BiasMetricsDisplayProps {
  analyses: BiasAnalysis[];
  response?: AnalyzeResponse;
}

export const BiasMetricsDisplay: React.FC<BiasMetricsDisplayProps> = ({ analyses, response }) => {
  const totalAnalyzed = response?.total_trechos_analisados || 0;
  const totalWithBias = response?.total_trechos_com_vies || analyses.length;
  const totalWithoutBias = totalAnalyzed - totalWithBias;

  if (!analyses || analyses.length === 0) {
    return (
      <div className="space-y-6">
        {/* Coverage Information */}
        {response && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-blue-100 p-2 rounded-lg">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Cobertura da Análise</h3>
                <p className="text-sm text-gray-600">Estatísticas completas do texto analisado</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">{totalAnalyzed}</div>
                <div className="text-sm text-gray-600">Segmentos Analisados</div>
                <div className="text-xs text-gray-500 mt-1">Total de trechos verificados</div>
              </div>
              <div className="bg-white rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-600">{totalWithoutBias}</div>
                <div className="text-sm text-gray-600">Sem Viés Detectado</div>
                <div className="text-xs text-gray-500 mt-1">{totalAnalyzed > 0 ? Math.round((totalWithoutBias/totalAnalyzed)*100) : 0}% do total</div>
              </div>
              <div className="bg-white rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-red-600">{totalWithBias}</div>
                <div className="text-sm text-gray-600">Com Viés Detectado</div>
                <div className="text-xs text-gray-500 mt-1">{totalAnalyzed > 0 ? Math.round((totalWithBias/totalAnalyzed)*100) : 0}% do total</div>
              </div>
            </div>
          </div>
        )}

        <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-8 text-center shadow-sm">
          <div className="flex justify-center mb-4">
            <div className="bg-green-100 p-3 rounded-full">
              <Shield className="h-8 w-8 text-green-600" />
            </div>
          </div>
          <h3 className="text-green-800 font-semibold text-lg">✅ Análise Limpa</h3>
          <p className="text-green-600 text-sm mt-2">
            {totalAnalyzed > 0 
              ? `Nenhum viés detectado em ${totalAnalyzed} segmentos analisados`
              : 'Nenhum viés significativo detectado no texto'
            }
          </p>
          <div className="mt-4 text-xs text-green-500 bg-green-100 px-3 py-1 rounded-full inline-block">
            Baixo risco de viés
          </div>
        </div>
      </div>
    );
  }

  const formatBiasType = (biasType: string): string => {
    return BiasTypeLabels[biasType] || biasType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getBiasTypeColor = (biasType: string): string => {
    return BiasTypeColors[biasType] || "bg-gray-100 text-gray-800 border-gray-200";
  };

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 0.7) return <AlertTriangle className="h-4 w-4 text-red-600" />;
    if (confidence >= 0.4) return <Eye className="h-4 w-4 text-yellow-600" />;
    return <Shield className="h-4 w-4 text-green-600" />;
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return "text-red-600";
    if (confidence >= 0.4) return "text-yellow-600"; 
    return "text-green-600";
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.7) return "ALTA";
    if (confidence >= 0.4) return "MÉDIA";
    return "BAIXA";
  };

  const getConfidenceBgColor = (confidence: number) => {
    if (confidence >= 0.7) return "bg-red-50 border-red-200";
    if (confidence >= 0.4) return "bg-yellow-50 border-yellow-200";
    return "bg-green-50 border-green-200";
  };

  const getSentimentIcon = (polarity: number | undefined) => {
    if (!polarity) return <Minus className="h-4 w-4 text-gray-400" />;
    if (polarity > 0.3) return <TrendingUp className="h-4 w-4 text-blue-600" />;
    if (polarity < -0.3) return <TrendingDown className="h-4 w-4 text-red-600" />;
    return <Minus className="h-4 w-4 text-gray-600" />;
  };

  const getMetricBar = (value: number | undefined, maxValue: number = 1, colorClass: string = "bg-blue-500") => {
    const percentage = ((value || 0) / maxValue) * 100;
    return (
      <div className="w-full bg-gray-200 rounded-full h-3 relative overflow-hidden">
        <div 
          className={`${colorClass} h-3 rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white/20 rounded-full" />
      </div>
    );
  };

  // Calculate aggregate metrics
  const avgConfidence = analyses.reduce((sum, a) => sum + a.confianca, 0) / analyses.length;
  const avgEmotionalIntensity = analyses.reduce((sum, a) => sum + (a.intensidade_emocional || 0), 0) / analyses.length;
  const avgPolarity = analyses.reduce((sum, a) => sum + (a.polaridade_sentimento || 0), 0) / analyses.length;
  const avgCertainty = analyses.reduce((sum, a) => sum + (a.nivel_certeza || 0), 0) / analyses.length;

  // Categorize analyses by confidence
  const highConfidence = analyses.filter(a => a.confianca >= 0.7);
  const mediumConfidence = analyses.filter(a => a.confianca >= 0.4 && a.confianca < 0.7);
  const lowConfidence = analyses.filter(a => a.confianca < 0.4);

  // Bias type distribution for chart
  const biasDistribution: Record<string, number> = {};
  analyses.forEach(analysis => {
    biasDistribution[analysis.tipo_vies] = (biasDistribution[analysis.tipo_vies] || 0) + 1;
  });

  return (
    <div className="space-y-8">
      {/* Coverage Information */}
      {response && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 shadow-sm">
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-blue-100 p-2 rounded-lg">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900">Cobertura da Análise</h3>
              <p className="text-sm text-gray-600">Estatísticas completas do texto analisado</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">{totalAnalyzed}</div>
              <div className="text-sm text-gray-600">Segmentos Analisados</div>
              <div className="text-xs text-gray-500 mt-1">Total de trechos verificados</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">{totalWithoutBias}</div>
              <div className="text-sm text-gray-600">Sem Viés Detectado</div>
              <div className="text-xs text-gray-500 mt-1">{totalAnalyzed > 0 ? Math.round((totalWithoutBias/totalAnalyzed)*100) : 0}% do total</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-red-600">{totalWithBias}</div>
              <div className="text-sm text-gray-600">Com Viés Detectado</div>
              <div className="text-xs text-gray-500 mt-1">{totalAnalyzed > 0 ? Math.round((totalWithBias/totalAnalyzed)*100) : 0}% do total</div>
            </div>
          </div>
        </div>
      )}

      {/* Risk Level Overview */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-100 p-2 rounded-lg">
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900">Métricas dos Segmentos com Viés</h3>
              <p className="text-sm text-gray-600">Análise detalhada dos trechos problemáticos</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-red-600">{analyses.length}</div>
            <div className="text-sm text-gray-600">Trechos com viés</div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl p-4 shadow-sm border">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-gray-700">Confiança Geral</span>
              {getConfidenceIcon(avgConfidence)}
            </div>
            <div className={`text-2xl font-bold ${getConfidenceColor(avgConfidence)} mb-2`}>
              {(avgConfidence * 100).toFixed(0)}%
            </div>
            {getMetricBar(avgConfidence, 1, getConfidenceColor(avgConfidence).includes('red') ? 'bg-red-500' : getConfidenceColor(avgConfidence).includes('yellow') ? 'bg-yellow-500' : 'bg-green-500')}
            <div className="text-xs text-gray-500 mt-1">{getConfidenceLabel(avgConfidence)}</div>
          </div>
          
          <div className="bg-white rounded-xl p-4 shadow-sm border">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-gray-700">Intensidade Emocional</span>
              <Zap className="h-4 w-4 text-orange-600" />
            </div>
            <div className="text-2xl font-bold text-orange-600 mb-2">
              {(avgEmotionalIntensity * 100).toFixed(0)}%
            </div>
            {getMetricBar(avgEmotionalIntensity, 1, 'bg-orange-500')}
            <div className="text-xs text-gray-500 mt-1">
              {avgEmotionalIntensity > 0.7 ? 'ALTA' : avgEmotionalIntensity > 0.4 ? 'MÉDIA' : 'BAIXA'}
            </div>
          </div>
          
          <div className="bg-white rounded-xl p-4 shadow-sm border">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-gray-700">Polaridade</span>
              {getSentimentIcon(avgPolarity)}
            </div>
            <div className="text-2xl font-bold text-gray-800 mb-2">
              {avgPolarity >= 0 ? '+' : ''}{(avgPolarity * 100).toFixed(0)}%
            </div>
            {getMetricBar(Math.abs(avgPolarity), 1, avgPolarity > 0 ? 'bg-blue-500' : 'bg-red-500')}
            <div className="text-xs text-gray-500 mt-1">
              {Math.abs(avgPolarity) > 0.3 ? 'FORTE' : Math.abs(avgPolarity) > 0.1 ? 'MODERADA' : 'NEUTRA'}
            </div>
          </div>
          
          <div className="bg-white rounded-xl p-4 shadow-sm border">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-gray-700">Nível de Certeza</span>
              <Brain className="h-4 w-4 text-purple-600" />
            </div>
            <div className="text-2xl font-bold text-purple-600 mb-2">
              {(avgCertainty * 100).toFixed(0)}%
            </div>
            {getMetricBar(avgCertainty, 1, 'bg-purple-500')}
            <div className="text-xs text-gray-500 mt-1">
              {avgCertainty > 0.7 ? 'ALTA' : avgCertainty > 0.4 ? 'MÉDIA' : 'BAIXA'}
            </div>
          </div>
        </div>
      </div>

      {/* Confidence Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className={`rounded-xl p-6 border-2 ${getConfidenceBgColor(0.8)}`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <span className="font-semibold text-red-800">Risco Alto</span>
            </div>
            <span className="text-2xl font-bold text-red-600">{highConfidence.length}</span>
          </div>
          <div className="text-sm text-red-700">Viéses com alta confiança (≥70%)</div>
          {highConfidence.length > 0 && (
            <div className="mt-3">
              {getMetricBar(highConfidence.length, analyses.length, 'bg-red-500')}
              <div className="text-xs text-red-600 mt-1">
                {((highConfidence.length / analyses.length) * 100).toFixed(0)}% do total
              </div>
            </div>
          )}
        </div>

        <div className={`rounded-xl p-6 border-2 ${getConfidenceBgColor(0.5)}`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Eye className="h-5 w-5 text-yellow-600" />
              <span className="font-semibold text-yellow-800">Risco Médio</span>
            </div>
            <span className="text-2xl font-bold text-yellow-600">{mediumConfidence.length}</span>
          </div>
          <div className="text-sm text-yellow-700">Viéses com média confiança (40-69%)</div>
          {mediumConfidence.length > 0 && (
            <div className="mt-3">
              {getMetricBar(mediumConfidence.length, analyses.length, 'bg-yellow-500')}
              <div className="text-xs text-yellow-600 mt-1">
                {((mediumConfidence.length / analyses.length) * 100).toFixed(0)}% do total
              </div>
            </div>
          )}
        </div>

        <div className={`rounded-xl p-6 border-2 ${getConfidenceBgColor(0.2)}`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-green-600" />
              <span className="font-semibold text-green-800">Risco Baixo</span>
            </div>
            <span className="text-2xl font-bold text-green-600">{lowConfidence.length}</span>
          </div>
          <div className="text-sm text-green-700">Viéses com baixa confiança (&lt;40%)</div>
          {lowConfidence.length > 0 && (
            <div className="mt-3">
              {getMetricBar(lowConfidence.length, analyses.length, 'bg-green-500')}
              <div className="text-xs text-green-600 mt-1">
                {((lowConfidence.length / analyses.length) * 100).toFixed(0)}% do total
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bias Types Distribution */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
          <Target className="h-5 w-5 mr-2 text-red-600" />
          Tipos de Viés Detectados
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(biasDistribution)
            .sort(([,a], [,b]) => b - a)
            .map(([type, count]) => (
              <div key={type} className={`p-4 rounded-xl border-2 ${getBiasTypeColor(type)} transition-all hover:shadow-md`}>
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold text-sm">{formatBiasType(type)}</span>
                  <span className="text-2xl font-bold">{count}</span>
                </div>
                <div className="mb-3">
                  {getMetricBar(count, Math.max(...Object.values(biasDistribution)), 'bg-current opacity-30')}
                </div>
                <div className="text-xs opacity-75">
                  {((count / analyses.length) * 100).toFixed(0)}% dos trechos
                </div>
              </div>
          ))}
        </div>
      </div>

      {/* Individual Analysis Cards */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-semibold text-gray-900">Análises Detalhadas</h3>
          <div className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
            {analyses.length} trechos identificados
          </div>
        </div>
        
        <div className="space-y-4">
          {analyses
            .sort((a, b) => b.confianca - a.confianca)
            .map((analysis, index) => (
              <div key={index} className={`bg-white rounded-xl shadow-sm border-l-4 ${
                analysis.confianca >= 0.7 ? 'border-red-500' : 
                analysis.confianca >= 0.4 ? 'border-yellow-500' : 'border-green-500'
              } p-6 hover:shadow-md transition-shadow`}>
                
                <div className="flex items-start justify-between mb-4">
                  <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border-2 ${getBiasTypeColor(analysis.tipo_vies)}`}>
                    {formatBiasType(analysis.tipo_vies)}
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className={`px-3 py-1 rounded-full text-xs font-bold ${getConfidenceBgColor(analysis.confianca)}`}>
                      {getConfidenceLabel(analysis.confianca)}
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className={`text-lg font-bold ${getConfidenceColor(analysis.confianca)}`}>
                        {(analysis.confianca * 100).toFixed(0)}%
                      </span>
                      {getConfidenceIcon(analysis.confianca)}
                    </div>
                  </div>
                </div>
                
                <blockquote className="border-l-4 border-gray-300 pl-4 italic text-gray-700 mb-4 bg-gray-50 p-3 rounded-r-lg">
                  <span className="text-sm text-gray-500">Trecho identificado:</span>
                  <br />
                  <span className="text-gray-800">"{analysis.trecho_original}"</span>
                </blockquote>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <h5 className="text-sm font-semibold text-blue-800 mb-2">💡 Explicação:</h5>
                  <p className="text-sm text-blue-700">
                    {analysis.explicacao}
                  </p>
                </div>
                
                {/* Quantitative Metrics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="text-center p-3 bg-orange-50 rounded-lg border border-orange-200">
                    <div className="text-lg font-bold text-orange-600">
                      {((analysis.intensidade_emocional || 0) * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-orange-700">Intensidade Emocional</div>
                  </div>
                  <div className="text-center p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="text-lg font-bold text-blue-600">
                      {(analysis.polaridade_sentimento || 0) >= 0 ? '+' : ''}
                      {((analysis.polaridade_sentimento || 0) * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-blue-700">Polaridade</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg border border-green-200">
                    <div className="text-lg font-bold text-green-600">
                      {((analysis.complexidade_sintatica || 0) * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-green-700">Complexidade</div>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded-lg border border-purple-200">
                    <div className="text-lg font-bold text-purple-600">
                      {((analysis.nivel_certeza || 0) * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-purple-700">Nível Certeza</div>
                  </div>
                </div>
                
                {analysis.reformulacao_sugerida && (
                  <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4">
                    <h5 className="text-sm font-semibold text-green-800 mb-2 flex items-center">
                      <Target className="h-4 w-4 mr-1" />
                      ✨ Reformulação Sugerida:
                    </h5>
                    <p className="text-sm text-green-700 font-medium">
                      {analysis.reformulacao_sugerida}
                    </p>
                  </div>
                )}
              </div>
          ))}
        </div>
      </div>
    </div>
  );
}; 