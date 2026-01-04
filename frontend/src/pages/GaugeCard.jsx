const GaugeCard = ({ label, value, unit = "%" }) => {
  // Format the display value to 2 decimal places
  const displayValue = typeof value === 'number' ? value.toFixed(2) : parseFloat(value || 0).toFixed(2);

  // Get parameter icon
  const getParameterIcon = (paramLabel) => {
    switch (paramLabel.toLowerCase()) {
      case 'temperature':
        return '🌡️';
      case 'vibration':
        return '📳';
      case 'speed':
        return '⚡';
      default:
        return '📊';
    }
  };

  // Determine status level with enhanced styling
  const getStatusLevel = (paramLabel, val) => {
    const numValue = Number(val);
    
    switch (paramLabel.toLowerCase()) {
      case 'temperature':
        if (numValue >= 85) return { 
          level: 'Critical', 
          color: 'from-red-500 to-red-600', 
          textColor: 'text-red-700',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          progress: 100
        };
        if (numValue >= 75) return { 
          level: 'High', 
          color: 'from-orange-400 to-red-500', 
          textColor: 'text-orange-700',
          bgColor: 'bg-orange-50',
          borderColor: 'border-orange-200',
          progress: 75
        };
        if (numValue >= 65) return { 
          level: 'Medium', 
          color: 'from-yellow-400 to-orange-400', 
          textColor: 'text-yellow-700',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          progress: 50
        };
        return { 
          level: 'Low', 
          color: 'from-green-400 to-emerald-500', 
          textColor: 'text-green-700',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          progress: 25
        };
        
      case 'vibration':
        if (numValue >= 7) return { 
          level: 'Critical', 
          color: 'from-red-500 to-red-600', 
          textColor: 'text-red-700',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          progress: 100
        };
        if (numValue >= 5) return { 
          level: 'High', 
          color: 'from-orange-400 to-red-500', 
          textColor: 'text-orange-700',
          bgColor: 'bg-orange-50',
          borderColor: 'border-orange-200',
          progress: 75
        };
        if (numValue >= 3) return { 
          level: 'Medium', 
          color: 'from-yellow-400 to-orange-400', 
          textColor: 'text-yellow-700',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          progress: 50
        };
        return { 
          level: 'Low', 
          color: 'from-green-400 to-emerald-500', 
          textColor: 'text-green-700',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          progress: 25
        };
        
      case 'speed':
        if (numValue >= 1350) return { 
          level: 'Critical', 
          color: 'from-red-500 to-red-600', 
          textColor: 'text-red-700',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          progress: 100
        };
        if (numValue >= 1250) return { 
          level: 'High', 
          color: 'from-orange-400 to-red-500', 
          textColor: 'text-orange-700',
          bgColor: 'bg-orange-50',
          borderColor: 'border-orange-200',
          progress: 75
        };
        if (numValue >= 1150) return { 
          level: 'Medium', 
          color: 'from-yellow-400 to-orange-400', 
          textColor: 'text-yellow-700',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          progress: 50
        };
        return { 
          level: 'Low', 
          color: 'from-green-400 to-emerald-500', 
          textColor: 'text-green-700',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          progress: 25
        };
        
      default:
        return { 
          level: 'Normal', 
          color: 'from-gray-400 to-gray-500', 
          textColor: 'text-gray-700',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          progress: 50
        };
    }
  };

  const status = getStatusLevel(label, value);
  const icon = getParameterIcon(label);

  return (
    <div className={`relative overflow-hidden rounded-2xl ${status.bgColor} ${status.borderColor} border-2 transition-all duration-300 hover:shadow-lg hover:scale-105 group`}>
      {/* Background Gradient Overlay */}
      <div className={`absolute inset-0 bg-gradient-to-br ${status.color} opacity-5 group-hover:opacity-10 transition-opacity duration-300`}></div>
      
      {/* Content */}
      <div className="relative p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${status.color} flex items-center justify-center text-white shadow-lg`}>
              <span className="text-lg">{icon}</span>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-600 uppercase tracking-wide">{label}</h4>
              <div className={`text-xs font-semibold ${status.textColor} flex items-center gap-1`}>
                <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${status.color}`}></div>
                {status.level}
              </div>
            </div>
          </div>
        </div>
        
        {/* Value Display */}
        <div className="mb-4">
          <div className="flex items-baseline gap-1">
            <span className="text-4xl font-bold text-gray-900 tracking-tight">
              {displayValue}
            </span>
            <span className="text-lg font-medium text-gray-500">{unit}</span>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div 
              className={`h-full bg-gradient-to-r ${status.color} transition-all duration-500 ease-out rounded-full shadow-sm`}
              style={{ width: `${status.progress}%` }}
            ></div>
          </div>
        </div>
        
        {/* Status Levels */}
        <div className="flex justify-between items-center text-xs">
          {[
            { name: 'Low', color: 'text-green-600' },
            { name: 'Medium', color: 'text-yellow-600' },
            { name: 'High', color: 'text-orange-600' },
            { name: 'Critical', color: 'text-red-600' }
          ].map((level) => (
            <span 
              key={level.name}
              className={`font-medium ${
                status.level === level.name 
                  ? `${level.color} font-bold` 
                  : 'text-gray-400'
              } transition-colors duration-200`}
            >
              {level.name}
            </span>
          ))}
        </div>
      </div>
      
      {/* Decorative Elements */}
      <div className="absolute top-0 right-0 w-20 h-20 transform translate-x-10 -translate-y-10">
        <div className={`w-full h-full rounded-full bg-gradient-to-br ${status.color} opacity-10`}></div>
      </div>
    </div>
  );
};

export default GaugeCard;