import React from 'react';
import { Clock, CheckCircle, AlertCircle, Loader2, Search, Brain, FileText, Zap, Settings } from 'lucide-react';

export interface AnalysisStep {
  id: string;
  title: string;
  description: string;
  status: 'waiting' | 'running' | 'completed' | 'error';
  startTime?: number;
  endTime?: number;
  details?: string[];
  metrics?: { [key: string]: any };
  icon?: React.ReactNode;
}

interface AnalysisProgressProps {
  steps: AnalysisStep[];
  currentStep?: string;
  isAnalyzing: boolean;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({
  steps,
  currentStep,
  isAnalyzing
}) => {
  const getStepIcon = (step: AnalysisStep) => {
    if (step.icon) return step.icon;
    
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'running':
        return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getDuration = (step: AnalysisStep) => {
    if (step.startTime && step.endTime) {
      return `${((step.endTime - step.startTime) / 1000).toFixed(1)}s`;
    }
    return null;
  };

  const getStatusColor = (step: AnalysisStep) => {
    switch (step.status) {
      case 'completed':
        return 'border-green-200 bg-green-50';
      case 'error':
        return 'border-red-200 bg-red-50';
      case 'running':
        return 'border-blue-200 bg-blue-50 shadow-md';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const completedSteps = steps.filter(step => step.status === 'completed').length;
  const totalSteps = steps.length;
  const progressPercentage = (completedSteps / totalSteps) * 100;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-800">
          🔍 Processo de Análise
        </h3>
        {isAnalyzing && (
          <div className="flex items-center text-blue-600">
            <Loader2 className="w-4 h-4 animate-spin mr-2" />
            Analisando...
          </div>
        )}
      </div>

      <div className="space-y-3">
        {steps.map((step, index) => (
          <div
            key={step.id}
            className={`relative border rounded-lg p-4 transition-all duration-300 ${getStatusColor(step)}`}
          >
            {/* Linha conectora */}
            {index < steps.length - 1 && (
              <div className="absolute left-7 top-16 w-0.5 h-4 bg-gray-300"></div>
            )}

            <div className="flex items-start space-x-3">
              {/* Ícone */}
              <div className="flex-shrink-0 mt-1">
                {getStepIcon(step)}
              </div>

              {/* Conteúdo */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium text-gray-900">
                    {step.title}
                  </h4>
                  <div className="flex items-center space-x-2 text-xs text-gray-500">
                    {getDuration(step) && (
                      <span className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {getDuration(step)}
                      </span>
                    )}
                    <span className="capitalize font-medium">
                      {step.status === 'running' ? 'executando' : 
                       step.status === 'completed' ? 'concluído' :
                       step.status === 'error' ? 'erro' : 'aguardando'}
                    </span>
                  </div>
                </div>

                <p className="text-sm text-gray-600 mt-1">
                  {step.description}
                </p>

                {/* Detalhes expandidos */}
                {step.status === 'running' && step.details && (
                  <div className="mt-3 space-y-1">
                    {step.details.map((detail, i) => (
                      <div key={i} className="text-xs text-gray-600 flex items-center">
                        <div className="w-1 h-1 bg-blue-400 rounded-full mr-2"></div>
                        {detail}
                      </div>
                    ))}
                  </div>
                )}

                {/* Métricas */}
                {step.status === 'completed' && step.metrics && (
                  <div className="mt-3 grid grid-cols-2 gap-3">
                    {Object.entries(step.metrics).map(([key, value]) => (
                      <div key={key} className="text-xs">
                        <span className="text-gray-500">{key}:</span>
                        <span className="ml-1 font-medium text-gray-700">
                          {typeof value === 'number' ? value.toFixed(2) : value}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Barra de progresso para etapa atual */}
                {step.status === 'running' && (
                  <div className="mt-3">
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div className="bg-blue-500 h-1.5 rounded-full animate-pulse" style={{width: '60%'}}></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Resumo final */}
      {!isAnalyzing && steps.some(s => s.status === 'completed') && (
        <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg">
          <h4 className="text-sm font-medium text-gray-800 mb-2">
            ✅ Análise Concluída
          </h4>
          <div className="grid grid-cols-3 gap-4 text-xs">
            <div>
              <span className="text-gray-500">Total de etapas:</span>
              <span className="ml-1 font-medium">{totalSteps}</span>
            </div>
            <div>
              <span className="text-gray-500">Concluídas:</span>
              <span className="ml-1 font-medium text-green-600">
                {completedSteps}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Tempo total:</span>
              <span className="ml-1 font-medium">
                {steps.reduce((total, step) => {
                  if (step.startTime && step.endTime) {
                    return total + (step.endTime - step.startTime);
                  }
                  return total;
                }, 0) / 1000}s
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Função helper para criar os passos padrão da análise
export const createAnalysisSteps = (): AnalysisStep[] => [
  {
    id: 'validation',
    title: '1. Validação de Entrada',
    description: 'Verificando título do artigo e parâmetros',
    status: 'waiting',
    icon: <Settings className="w-6 h-6 text-gray-400" />,
  },
  {
    id: 'wikipedia-search',
    title: '2. Busca na Wikipedia',
    description: 'Procurando artigo na Wikipedia portuguesa',
    status: 'waiting',
    icon: <Search className="w-6 h-6 text-gray-400" />,
  },
  {
    id: 'content-extraction',
    title: '3. Extração de Conteúdo',
    description: 'Baixando e limpando conteúdo do artigo',
    status: 'waiting',
    icon: <FileText className="w-6 h-6 text-gray-400" />,
  },
  {
    id: 'ai-relevance',
    title: '4. Verificação de Relevância IA',
    description: 'Verificando se artigo é relacionado à IA',
    status: 'waiting',
    icon: <Brain className="w-6 h-6 text-gray-400" />,
  },
  {
    id: 'bias-detection',
    title: '5. Detecção de Viés',
    description: 'Analisando texto em busca de viés',
    status: 'waiting',
    icon: <Zap className="w-6 h-6 text-gray-400" />,
  },
  {
    id: 'reformulation',
    title: '6. Reformulação com IA',
    description: 'Gerando sugestões de reformulação',
    status: 'waiting',
    icon: <Brain className="w-6 h-6 text-gray-400" />,
  },
  {
    id: 'summary-generation',
    title: '7. Geração de Resumo',
    description: 'Criando resumo final da análise',
    status: 'waiting',
    icon: <FileText className="w-6 h-6 text-gray-400" />,
  }
]; 