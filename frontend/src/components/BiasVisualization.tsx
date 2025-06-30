import React from 'react';
import { BiasTypeLabels } from '../types';
import { Target, AlertTriangle, Shield, Eye, TrendingUp, TrendingDown, PieChart, BarChart3, Activity, CheckCircle2 } from 'lucide-react';

interface BiasVisualizationProps {
  biasCategories: string[];
  overallScore: number;
}

export const BiasVisualization: React.FC<BiasVisualizationProps> = ({ 
  biasCategories, 
  overallScore 
}) => {
  if (!biasCategories || biasCategories.length === 0) {
    return (
      <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8 animate-slide-up overflow-hidden relative">
        {/* Background decoration */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-emerald-50 to-transparent rounded-full -mr-16 -mt-16"></div>
        <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-green-50 to-transparent rounded-full -ml-12 -mb-12"></div>
        
        <div className="relative text-center">
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-r from-emerald-500 to-green-500 p-6 rounded-3xl shadow-2xl">
              <Shield className="h-16 w-16 text-white" />
            </div>
          </div>
          <h3 className="text-3xl font-black text-emerald-800 mb-4">✅ Análise Limpa</h3>
          <p className="text-xl text-emerald-600 mb-6 font-semibold">Nenhum viés significativo detectado</p>
          <div className="inline-block bg-gradient-to-r from-emerald-100 to-green-100 text-emerald-800 px-8 py-3 rounded-2xl text-lg font-black border-2 border-emerald-200 shadow-sm">
            🎉 Baixo Risco de Viés
          </div>
          
          {/* Clean analysis features */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-emerald-50 p-4 rounded-2xl border border-emerald-200">
              <CheckCircle2 className="h-6 w-6 text-emerald-600 mx-auto mb-2" />
              <div className="text-sm font-bold text-emerald-800">Linguagem Neutra</div>
            </div>
            <div className="bg-green-50 p-4 rounded-2xl border border-green-200">
              <Activity className="h-6 w-6 text-green-600 mx-auto mb-2" />
              <div className="text-sm font-bold text-green-800">Conteúdo Objetivo</div>
            </div>
            <div className="bg-teal-50 p-4 rounded-2xl border border-teal-200">
              <Shield className="h-6 w-6 text-teal-600 mx-auto mb-2" />
              <div className="text-sm font-bold text-teal-800">Análise Confiável</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Count bias types
  const biasDistribution: Record<string, number> = {};
  biasCategories.forEach(category => {
    biasDistribution[category] = (biasDistribution[category] || 0) + 1;
  });

  // Get risk level styling
  const getRiskStyling = (score: number) => {
    if (score >= 0.7) return {
      color: 'text-red-600',
      bg: 'bg-red-50 border-red-200',
      gradient: 'from-red-500 to-red-600',
      icon: AlertTriangle,
      label: 'ALTO RISCO',
      description: 'Múltiplos viéses detectados com alta confiança',
      accentColor: 'red'
    };
    if (score >= 0.4) return {
      color: 'text-amber-600', 
      bg: 'bg-amber-50 border-amber-200',
      gradient: 'from-amber-500 to-amber-600',
      icon: Eye,
      label: 'MÉDIO RISCO',
      description: 'Alguns viéses detectados, requer atenção',
      accentColor: 'amber'
    };
    return {
      color: 'text-emerald-600',
      bg: 'bg-emerald-50 border-emerald-200',
      gradient: 'from-emerald-500 to-emerald-600',
      icon: Shield,
      label: 'BAIXO RISCO',
      description: 'Poucos viéses detectados com baixa confiança',
      accentColor: 'emerald'
    };
  };

  const risk = getRiskStyling(overallScore);
  const RiskIcon = risk.icon;

  // Create visualization data
  const chartData = Object.entries(biasDistribution)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 6); // Top 6 most common

  const total = Object.values(biasDistribution).reduce((sum, count) => sum + count, 0);

  // Enhanced color palette
  const colors = [
    { bg: 'from-red-500 to-pink-500', text: 'text-red-600', light: 'bg-red-50', border: 'border-red-200' },
    { bg: 'from-orange-500 to-yellow-500', text: 'text-orange-600', light: 'bg-orange-50', border: 'border-orange-200' },
    { bg: 'from-purple-500 to-indigo-500', text: 'text-purple-600', light: 'bg-purple-50', border: 'border-purple-200' },
    { bg: 'from-blue-500 to-cyan-500', text: 'text-blue-600', light: 'bg-blue-50', border: 'border-blue-200' },
    { bg: 'from-green-500 to-emerald-500', text: 'text-green-600', light: 'bg-green-50', border: 'border-green-200' },
    { bg: 'from-indigo-500 to-purple-500', text: 'text-indigo-600', light: 'bg-indigo-50', border: 'border-indigo-200' }
  ];

  const formatBiasType = (biasType: string): string => {
    return BiasTypeLabels[biasType] || biasType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="space-y-8">
      {/* Enhanced Risk Level Header */}
      <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8 animate-slide-up overflow-hidden relative">
        {/* Background decorations */}
        <div className={`absolute top-0 right-0 w-40 h-40 bg-gradient-to-bl from-${risk.accentColor}-50 to-transparent rounded-full -mr-20 -mt-20`}></div>
        <div className={`absolute bottom-0 left-0 w-32 h-32 bg-gradient-to-tr from-${risk.accentColor}-100/50 to-transparent rounded-full -ml-16 -mb-16`}></div>
        
        <div className="relative">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-6">
              <div className={`bg-gradient-to-r ${risk.gradient} p-4 rounded-3xl shadow-2xl`}>
                <RiskIcon className="h-12 w-12 text-white" />
              </div>
              <div>
                <h3 className={`text-3xl font-black ${risk.color} mb-2`}>{risk.label}</h3>
                <p className="text-lg text-gray-600 font-medium">{risk.description}</p>
                <div className="flex items-center space-x-4 mt-3">
                  <div className="flex items-center space-x-2">
                    <Target className="h-5 w-5 text-gray-500" />
                    <span className="text-sm font-medium text-gray-600">{biasCategories.length} ocorrências</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <PieChart className="h-5 w-5 text-gray-500" />
                    <span className="text-sm font-medium text-gray-600">{Object.keys(biasDistribution).length} tipos diferentes</span>
                  </div>
                </div>
              </div>
            </div>
            <div className={`text-center p-8 rounded-3xl border-2 ${risk.bg} shadow-lg relative overflow-hidden`}>
              <div className="absolute inset-0 bg-gradient-to-br from-white/30 to-transparent"></div>
              <div className="relative">
                <div className={`text-6xl font-black ${risk.color} mb-2`}>
                  {(overallScore * 100).toFixed(0)}%
                </div>
                <div className="text-sm font-bold text-gray-600">Score Geral</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Bias Distribution Visualization */}
      <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8 animate-slide-up">
        <div className="flex items-center space-x-4 mb-8">
          <div className="bg-gradient-to-r from-blue-500 to-indigo-500 p-3 rounded-2xl shadow-lg">
            <BarChart3 className="h-8 w-8 text-white" />
          </div>
          <div>
            <h3 className="text-2xl font-black text-gray-900">Distribuição de Viéses</h3>
            <p className="text-gray-600 font-medium">Análise detalhada dos tipos de viés detectados</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Enhanced Visual Chart */}
          <div className="relative">
            <div className="bg-gradient-to-br from-gray-50 to-blue-50 rounded-3xl p-8 border-2 border-gray-100">
              <h4 className="text-lg font-bold text-gray-800 mb-6 text-center">Visão Geral</h4>
              
              {/* Simplified bar chart representation */}
              <div className="space-y-4">
                {chartData.map(([type, count], index) => {
                  const percentage = (count / total) * 100;
                  const colorSet = colors[index % colors.length];
                  
                  return (
                    <div key={type} className={`${colorSet.light} rounded-2xl p-4 border-2 ${colorSet.border} hover:shadow-md transition-shadow duration-300`}>
                      <div className="flex justify-between items-center mb-3">
                        <span className={`font-bold text-sm ${colorSet.text}`}>
                          {formatBiasType(type)}
                        </span>
                        <div className="flex items-center space-x-2">
                          <span className={`text-lg font-black ${colorSet.text}`}>{count}</span>
                          {count > 3 ? (
                            <TrendingUp className={`h-4 w-4 ${colorSet.text}`} />
                          ) : count === 1 ? (
                            <TrendingDown className="h-4 w-4 text-gray-400" />
                          ) : null}
                        </div>
                      </div>
                      
                      <div className="mb-2">
                        <div className="w-full bg-white rounded-full h-3 border border-gray-200">
                          <div 
                            className={`bg-gradient-to-r ${colorSet.bg} h-3 rounded-full transition-all duration-1000 shadow-sm`}
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <span className="text-sm font-bold text-gray-600">
                          {percentage.toFixed(1)}% do total
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Total summary */}
              <div className="mt-6 pt-6 border-t-2 border-gray-200">
                <div className="bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl p-4 text-white text-center">
                  <div className="text-2xl font-black mb-1">{total}</div>
                  <div className="text-sm font-medium opacity-90">Total de Ocorrências</div>
                </div>
              </div>
            </div>
          </div>

          {/* Enhanced Detailed Breakdown */}
          <div className="space-y-4">
            <h4 className="text-lg font-bold text-gray-800 mb-6">Detalhamento por Tipo</h4>
            
            {Object.entries(biasDistribution)
              .sort(([,a], [,b]) => b - a)
              .map(([type, count], index) => {
                const colorSet = colors[index % colors.length];
                const severity = count > 3 ? 'high' : count > 1 ? 'medium' : 'low';
                
                return (
                  <div key={type} className={`group ${colorSet.light} rounded-2xl p-6 border-2 ${colorSet.border} hover:shadow-lg transition-all duration-300 hover:scale-[1.02]`}>
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <div className={`bg-gradient-to-r ${colorSet.bg} p-2 rounded-xl shadow-sm`}>
                            <Target className="h-5 w-5 text-white" />
                          </div>
                          <span className={`font-black text-lg ${colorSet.text}`}>
                            {formatBiasType(type)}
                          </span>
                        </div>
                        
                        <div className="text-sm text-gray-600 mb-3">
                          {severity === 'high' && '🔴 Alta frequência - Requer atenção imediata'}
                          {severity === 'medium' && '🟡 Frequência moderada - Monitorar'}
                          {severity === 'low' && '🟢 Baixa frequência - Controle ok'}
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <div className={`text-3xl font-black ${colorSet.text} mb-1`}>{count}</div>
                        <div className="text-xs text-gray-500">ocorrências</div>
                      </div>
                    </div>
                    
                    {/* Progress indicator */}
                    <div className="bg-white rounded-full h-2 mb-3 border border-gray-200">
                      <div 
                        className={`bg-gradient-to-r ${colorSet.bg} h-2 rounded-full transition-all duration-1000 shadow-sm`}
                        style={{ width: `${Math.min((count / Math.max(...Object.values(biasDistribution))) * 100, 100)}%` }}
                      />
                    </div>
                    
                    <div className={`text-xs ${colorSet.text} font-medium`}>
                      {((count / total) * 100).toFixed(1)}% do total de viéses detectados
                    </div>
                  </div>
                );
              })}
          </div>
        </div>

        {/* Summary insights */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 rounded-2xl p-6 border-2 border-blue-100">
          <div className="flex items-start space-x-4">
            <div className="bg-blue-500 p-2 rounded-xl">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <div>
              <h4 className="text-lg font-bold text-blue-900 mb-2">💡 Insights da Análise</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div className="text-blue-800 font-medium">
                  • <strong>Tipo mais frequente:</strong> {formatBiasType(chartData[0]?.[0] || '')}
                </div>
                <div className="text-blue-800 font-medium">
                  • <strong>Diversidade de viéses:</strong> {Object.keys(biasDistribution).length} tipos diferentes
                </div>
                <div className="text-blue-800 font-medium">
                  • <strong>Concentração:</strong> {chartData.length > 0 ? ((chartData[0][1] / total) * 100).toFixed(0) : 0}% em um tipo principal
                </div>
                <div className="text-blue-800 font-medium">
                  • <strong>Recomendação:</strong> {overallScore >= 0.7 ? 'Revisão necessária' : overallScore >= 0.4 ? 'Melhorias pontuais' : 'Manutenção atual'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 