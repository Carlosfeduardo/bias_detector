import React from 'react';
import { Brain, Sparkles, Zap, Target, Activity } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
  showProgress?: boolean;
  progress?: number;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  message = "Analisando...", 
  showProgress = false, 
  progress = 0 
}) => {
  const steps = [
    { icon: Brain, label: "Processando texto", delay: "0s" },
    { icon: Target, label: "Detectando viés", delay: "0.2s" },
    { icon: Activity, label: "Analisando padrões", delay: "0.4s" },
    { icon: Sparkles, label: "Gerando relatório", delay: "0.6s" },
    { icon: Zap, label: "Finalizando", delay: "0.8s" }
  ];

  return (
    <div className="flex items-center justify-center min-h-[400px] p-8">
      <div className="text-center">
        {/* Main Loading Animation */}
        <div className="relative mb-8">
          {/* Outer ring */}
          <div className="w-32 h-32 mx-auto relative">
            <div className="absolute inset-0 rounded-full border-4 border-blue-100"></div>
            <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-500 animate-spin"></div>
            <div className="absolute inset-2 rounded-full border-4 border-transparent border-t-purple-500 animate-spin" style={{animationDirection: 'reverse', animationDuration: '2s'}}></div>
            
            {/* Center brain icon */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-4 rounded-2xl shadow-2xl animate-pulse">
                <Brain className="h-8 w-8 text-white" />
              </div>
            </div>
            
            {/* Floating particles */}
            <div className="absolute -inset-4">
              {[...Array(6)].map((_, i) => (
                <div
                  key={i}
                  className="absolute w-2 h-2 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full animate-ping"
                  style={{
                    top: `${20 + Math.sin(i * 60 * Math.PI / 180) * 40}%`,
                    left: `${50 + Math.cos(i * 60 * Math.PI / 180) * 40}%`,
                    animationDelay: `${i * 0.3}s`,
                    animationDuration: '2s'
                  }}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Loading Message */}
        <div className="mb-8">
          <h3 className="text-2xl font-black text-gray-800 mb-2 animate-pulse">
            {message}
          </h3>
          <p className="text-gray-600 max-w-md mx-auto">
            Nossa IA está processando o artigo com tecnologia avançada de detecção de viés
          </p>
        </div>

        {/* Progress Bar (if enabled) */}
        {showProgress && (
          <div className="mb-8 max-w-md mx-auto">
            <div className="bg-gray-200 rounded-full h-3 mb-2">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500 ease-out shadow-sm"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="text-sm text-gray-600 font-medium">
              {progress}% completo
            </div>
          </div>
        )}

        {/* Processing Steps */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 max-w-4xl mx-auto">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isActive = !showProgress || progress > (index * 20);
            
            return (
              <div
                key={index}
                className={`p-4 rounded-2xl border-2 transition-all duration-500 ${
                  isActive 
                    ? 'bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200 shadow-md' 
                    : 'bg-gray-50 border-gray-200'
                }`}
                style={{ animationDelay: step.delay }}
              >
                <div className={`${isActive ? 'animate-bounce' : ''} mb-3`}>
                  <div className={`mx-auto w-fit p-3 rounded-xl ${
                    isActive 
                      ? 'bg-gradient-to-r from-blue-500 to-purple-500 shadow-lg' 
                      : 'bg-gray-300'
                  }`}>
                    <Icon className={`h-6 w-6 ${isActive ? 'text-white' : 'text-gray-500'}`} />
                  </div>
                </div>
                <div className={`text-sm font-bold ${isActive ? 'text-gray-800' : 'text-gray-500'}`}>
                  {step.label}
                </div>
              </div>
            );
          })}
        </div>

        {/* Animated Dots */}
        <div className="flex justify-center space-x-2 mt-8">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-bounce"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
        </div>

        {/* Technical Details */}
        <div className="mt-8 text-xs text-gray-500 max-w-lg mx-auto">
          <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-2xl p-4 border border-gray-200">
            <div className="grid grid-cols-2 gap-4">
              <div className="text-left">
                <div className="font-semibold text-gray-700">🔍 Análise NLP</div>
                <div>Processamento semântico</div>
              </div>
              <div className="text-left">
                <div className="font-semibold text-gray-700">🧠 IA Avançada</div>
                <div>Detecção de padrões</div>
              </div>
              <div className="text-left">
                <div className="font-semibold text-gray-700">📊 Métricas</div>
                <div>Análise quantitativa</div>
              </div>
              <div className="text-left">
                <div className="font-semibold text-gray-700">✨ Reformulação</div>
                <div>Sugestões neutras</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Variant for inline loading
export const InlineLoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6', 
    lg: 'w-8 h-8'
  };

  return (
    <div className={`${sizeClasses[size]} relative`}>
      <div className="absolute inset-0 rounded-full border-2 border-blue-200"></div>
      <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-blue-500 animate-spin"></div>
    </div>
  );
};

// Variant for button loading
export const ButtonLoadingSpinner: React.FC = () => (
  <div className="flex items-center space-x-3">
    <div className="relative w-5 h-5">
      <div className="absolute inset-0 rounded-full border-2 border-white/30"></div>
      <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-white animate-spin"></div>
    </div>
    <span>Processando...</span>
    <div className="flex space-x-1">
      {[...Array(3)].map((_, i) => (
        <div
          key={i}
          className="w-1.5 h-1.5 bg-white rounded-full animate-bounce"
          style={{ animationDelay: `${i * 0.1}s` }}
        />
      ))}
    </div>
  </div>
); 