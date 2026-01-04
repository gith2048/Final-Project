// Industrial Standards Constants
// Static constants for industrial thresholds - these should match backend/industrial_standards.py

// Temperature thresholds (Celsius)
export const TEMPERATURE_THRESHOLDS = {
  NORMAL: { MIN: 20, MAX: 65 },
  WARNING: { MIN: 65, MAX: 85 },
  CRITICAL: { MIN: 85, MAX: 120 }
};

// Vibration thresholds (mm/s RMS)
export const VIBRATION_THRESHOLDS = {
  NORMAL: { MIN: 0, MAX: 3.0 },
  WARNING: { MIN: 3.0, MAX: 7.0 },
  CRITICAL: { MIN: 7.0, MAX: 15.0 }
};

// Speed thresholds (RPM)
export const SPEED_THRESHOLDS = {
  NORMAL: { MIN: 800, MAX: 1150 },
  WARNING: { MIN: 1150, MAX: 1350 },
  CRITICAL: { MIN: 1350, MAX: 2000 }
};

// Combined thresholds object
export const INDUSTRIAL_THRESHOLDS = {
  temperature: {
    normal: TEMPERATURE_THRESHOLDS.NORMAL,
    warning: TEMPERATURE_THRESHOLDS.WARNING,
    critical: TEMPERATURE_THRESHOLDS.CRITICAL
  },
  vibration: {
    normal: VIBRATION_THRESHOLDS.NORMAL,
    warning: VIBRATION_THRESHOLDS.WARNING,
    critical: VIBRATION_THRESHOLDS.CRITICAL
  },
  speed: {
    normal: SPEED_THRESHOLDS.NORMAL,
    warning: SPEED_THRESHOLDS.WARNING,
    critical: SPEED_THRESHOLDS.CRITICAL
  }
};

// Condition severity levels
export const CONDITION_LEVELS = {
  NORMAL: 'normal',
  WARNING: 'warning',
  CRITICAL: 'critical',
  UNKNOWN: 'unknown'
};

// Condition colors for UI
export const CONDITION_COLORS = {
  [CONDITION_LEVELS.NORMAL]: '#10B981',    // Green
  [CONDITION_LEVELS.WARNING]: '#F59E0B',   // Amber
  [CONDITION_LEVELS.CRITICAL]: '#EF4444',  // Red
  [CONDITION_LEVELS.UNKNOWN]: '#6B7280'    // Gray
};

// Condition icons
export const CONDITION_ICONS = {
  [CONDITION_LEVELS.NORMAL]: '✅',
  [CONDITION_LEVELS.WARNING]: '⚠️',
  [CONDITION_LEVELS.CRITICAL]: '🚨',
  [CONDITION_LEVELS.UNKNOWN]: '❓'
};

// Parameter units
export const PARAMETER_UNITS = {
  temperature: '°C',
  vibration: 'mm/s',
  speed: 'RPM'
};

// Parameter display names
export const PARAMETER_NAMES = {
  temperature: 'Temperature',
  vibration: 'Vibration',
  speed: 'Speed'
};

// Utility functions
export const classifyValue = (parameter, value) => {
  const thresholds = INDUSTRIAL_THRESHOLDS[parameter];
  if (!thresholds) return CONDITION_LEVELS.UNKNOWN;

  if (value <= thresholds.normal.max) {
    return CONDITION_LEVELS.NORMAL;
  } else if (value <= thresholds.warning.max) {
    return CONDITION_LEVELS.WARNING;
  } else {
    return CONDITION_LEVELS.CRITICAL;
  }
};

export const getConditionColor = (condition) => {
  return CONDITION_COLORS[condition] || CONDITION_COLORS[CONDITION_LEVELS.UNKNOWN];
};

export const getConditionIcon = (condition) => {
  return CONDITION_ICONS[condition] || CONDITION_ICONS[CONDITION_LEVELS.UNKNOWN];
};

export const calculateOverallCondition = (temperature, vibration, speed) => {
  const scores = {
    [CONDITION_LEVELS.NORMAL]: 0,
    [CONDITION_LEVELS.WARNING]: 1,
    [CONDITION_LEVELS.CRITICAL]: 2
  };
  
  const tempCondition = classifyValue('temperature', temperature);
  const vibCondition = classifyValue('vibration', vibration);
  const speedCondition = classifyValue('speed', speed);
  
  const totalScore = scores[tempCondition] + scores[vibCondition] + scores[speedCondition];
  
  if (totalScore >= 4) {
    return CONDITION_LEVELS.CRITICAL;
  } else if (totalScore >= 2) {
    return CONDITION_LEVELS.WARNING;
  } else {
    return CONDITION_LEVELS.NORMAL;
  }
};

export const getThresholdDisplayText = (parameter, condition) => {
  const threshold = INDUSTRIAL_THRESHOLDS[parameter]?.[condition];
  if (!threshold) return 'N/A';

  const unit = PARAMETER_UNITS[parameter] || '';
  
  if (condition === CONDITION_LEVELS.NORMAL) {
    return `≤ ${threshold.max}${unit}`;
  } else if (condition === CONDITION_LEVELS.CRITICAL) {
    return `> ${threshold.min}${unit}`;
  } else {
    return `${threshold.min} - ${threshold.max}${unit}`;
  }
};

// Export default object with all constants
export default {
  TEMPERATURE_THRESHOLDS,
  VIBRATION_THRESHOLDS,
  SPEED_THRESHOLDS,
  INDUSTRIAL_THRESHOLDS,
  CONDITION_LEVELS,
  CONDITION_COLORS,
  CONDITION_ICONS,
  PARAMETER_UNITS,
  PARAMETER_NAMES,
  classifyValue,
  getConditionColor,
  getConditionIcon,
  calculateOverallCondition,
  getThresholdDisplayText
};