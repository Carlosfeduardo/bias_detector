import React from 'react';
import { BiasTypeLabels, BiasTypeColors } from '../types';
import { Target, AlertTriangle, Shield, Eye, TrendingUp, TrendingDown } from 'lucide-react';

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
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-8 text-center">
        <div className="flex justify-center mb-4">
          <div className="bg-green-100 p-4 rounded-full">
            <Shield className="h-12 w-12 text-green-600" />
          </div>
        </div>
        <h3 className="text-green-800 font-bold text-xl mb-2">✅ Análise Limpa</h3>
        <p className="text-green-600 mb-4">Nenhum viés significativo detectado</p>
        <div className="inline-block bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-semibold">
          Baixo Risco de Viés
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
      icon: AlertTriangle,
      label: 'ALTO RISCO',
      description: 'Múltiplos viéses detectados com alta confiança'
    };
    if (score >= 0.4) return {
      color: 'text-yellow-600', 
      bg: 'bg-yellow-50 border-yellow-200',
      icon: Eye,
      label: 'MÉDIO RISCO',
      description: 'Alguns viéses detectados, requer atenção'
    };
    return {
      color: 'text-green-600',
      bg: 'bg-green-50 border-green-200', 
      icon: Shield,
      label: 'BAIXO RISCO',
      description: 'Poucos viéses detectados com baixa confiança'
    };
  };

  const risk = getRiskStyling(overallScore);
  const RiskIcon = risk.icon;

  // Create simple pie chart data
  const chartData = Object.entries(biasDistribution)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5); // Top 5 most common

  const total = Object.values(biasDistribution).reduce((sum, count) => sum + count, 0);

  // Generate pie chart segments
  let cumulativePercentage = 0;
  const segments = chartData.map(([type, count], index) => {
    const percentage = (count / total) * 100;
    const startAngle = cumulativePercentage * 3.6; // Convert to degrees
    const endAngle = (cumulativePercentage + percentage) * 3.6;
    cumulativePercentage += percentage;

    const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6'];
    const color = colors[index % colors.length];

    return {
      type,
      count,
      percentage,
      startAngle,
      endAngle,
      color
    };
  });

  const formatBiasType = (biasType: string): string => {
    return BiasTypeLabels[biasType] || biasType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getBiasTypeColor = (biasType: string): string => {
    return BiasTypeColors[biasType] || "bg-gray-100 text-gray-800 border-gray-200";
  };

  return (
    <div className="space-y-6">
      {/* Risk Level Header */}
      <div className={`rounded-xl border-2 ${risk.bg} p-6`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="bg-white p-3 rounded-full shadow-sm">
              <RiskIcon className={`h-8 w-8 ${risk.color}`} />
            </div>
            <div>
              <h3 className={`text-xl font-bold ${risk.color}`}>{risk.label}</h3>
              <p className="text-sm text-gray-600 mt-1">{risk.description}</p>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-4xl font-bold ${risk.color}`}>
              {(overallScore * 100).toFixed(0)}%
            </div>
            <div className="text-sm text-gray-600">Score Geral</div>
          </div>
        </div>
      </div>

      {/* Bias Distribution Visualization */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="bg-red-100 p-2 rounded-lg">
            <Target className="h-5 w-5 text-red-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Distribuição de Viéses</h3>
            <p className="text-sm text-gray-600">{biasCategories.length} ocorrências em {Object.keys(biasDistribution).length} tipos diferentes</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Simple Pie Chart Representation */}
          <div className="relative">
            <div className="w-48 h-48 mx-auto relative">
              {/* Chart background */}
              <div className="w-full h-full rounded-full bg-gray-100 relative overflow-hidden">
                {segments.map((segment, index) => (
                  <div
                    key={segment.type}
                    className="absolute inset-0 rounded-full"
                    style={{
                      background: `conic-gradient(from ${segment.startAngle}deg, ${segment.color} 0deg, ${segment.color} ${segment.endAngle - segment.startAngle}deg, transparent ${segment.endAngle - segment.startAngle}deg)`
                    }}
                  />
                ))}
              </div>
              
              {/* Center label */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="bg-white rounded-full p-4 shadow-lg text-center">
                  <div className="text-lg font-bold text-gray-800">{total}</div>
                  <div className="text-xs text-gray-600">Total</div>
                </div>
              </div>
            </div>

            {/* Legend */}
            <div className="mt-4 space-y-2">
              {segments.map((segment, index) => (
                <div key={segment.type} className="flex items-center space-x-2 text-sm">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: segment.color }}
                  />
                  <span className="flex-1">{formatBiasType(segment.type)}</span>
                  <span className="font-medium">{segment.count}</span>
                  <span className="text-gray-500">({segment.percentage.toFixed(0)}%)</span>
                </div>
              ))}
            </div>
          </div>

          {/* Detailed Breakdown */}
          <div className="space-y-3">
            {Object.entries(biasDistribution)
              .sort(([,a], [,b]) => b - a)
              .map(([type, count], index) => (
                <div key={type} className={`p-4 rounded-lg border-2 ${getBiasTypeColor(type)} transition-all hover:shadow-md`}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-semibold text-sm">{formatBiasType(type)}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-lg font-bold">{count}</span>
                      {count > 2 ? (
                        <TrendingUp className="h-4 w-4 text-red-500" />
                      ) : count === 1 ? (
                        <TrendingDown className="h-4 w-4 text-green-500" />
                      ) : null}
                    </div>
                  </div>
                  
                  {/* Progress bar */}
                  <div className="mb-2">
                    <div className="w-full bg-current bg-opacity-20 rounded-full h-2">
                      <div 
                        className="bg-current h-2 rounded-full transition-all duration-500"
                        style={{ width: `${(count / Math.max(...Object.values(biasDistribution))) * 100}%` }}
                      />
                    </div>
                  </div>
                  
                  <div className="flex justify-between text-xs opacity-75">
                    <span>{((count / total) * 100).toFixed(1)}% do total</span>
                    <span>
                      {count === 1 ? 'Ocorrência única' : 
                       count <= 2 ? 'Poucas ocorrências' : 
                       count <= 4 ? 'Várias ocorrências' : 'Muitas ocorrências'}
                    </span>
                  </div>
                </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}; 