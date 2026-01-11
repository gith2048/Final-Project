/**
 * Centralized Threshold Configuration for Frontend
 * ===============================================
 * 
 * This module defines all threshold values used across the frontend components.
 * All components should import and use these values to ensure consistency.
 */

// STANDARD THRESHOLD VALUES (Updated to match backend industry standards)
// =========================

// Temperature Thresholds (°C) - Based on NEMA Class B Insulation Standards
export const TEMP_THRESHOLDS = {
  warning: 85.0,      // Unsatisfactory level - requires attention
  critical: 105.0,    // Unacceptable level - immediate action required
  emergency: 130.0    // Maximum safe operating temperature
};

// Vibration Thresholds (mm/s) - Based on ISO 10816-3 Standard
export const VIBRATION_THRESHOLDS = {
  warning: 4.5,       // Unsatisfactory level - restricted operation
  critical: 11.2,     // Unacceptable level - shutdown required
  emergency: 25.0     // Extreme danger level
};

// Speed Thresholds (RPM) - Based on industry standards for 4-pole motors
export const SPEED_THRESHOLDS = {
  warning: 1300.0,    // Unsatisfactory level - monitor closely
  critical: 1450.0,   // Unacceptable level - dangerous overspeed
  emergency: 1600.0   // Extreme overspeed - immediate shutdown
};

// COMBINED THRESHOLDS FOR EASY ACCESS
// ===================================

export const ALL_THRESHOLDS = {
  temperature: TEMP_THRESHOLDS,
  vibration: VIBRATION_THRESHOLDS,
  speed: SPEED_THRESHOLDS
};

// HELPER FUNCTIONS
// ================

/**
 * Get threshold value for a specific parameter and level.
 * 
 * @param {string} parameter - 'temperature', 'vibration', or 'speed'
 * @param {string} level - 'warning', 'critical', or 'emergency'
 * @returns {number} Threshold value
 * 
 * @example
 * getThreshold('temperature', 'warning') // returns 75.0
 */
export const getThreshold = (parameter, level) => {
  if (!ALL_THRESHOLDS[parameter]) {
    throw new Error(`Unknown parameter: ${parameter}`);
  }
  
  if (!ALL_THRESHOLDS[parameter][level]) {
    throw new Error(`Unknown level: ${level}`);
  }
  
  return ALL_THRESHOLDS[parameter][level];
};

/**
 * Check the status of a parameter value against thresholds.
 * 
 * @param {string} parameter - 'temperature', 'vibration', or 'speed'
 * @param {number} value - Current value to check
 * @returns {string} 'healthy', 'satisfactory', 'warning', 'critical', or 'emergency'
 * 
 * @example
 * checkThresholdStatus('temperature', 80.0) // returns 'satisfactory'
 */
export const checkThresholdStatus = (parameter, value) => {
  if (!ALL_THRESHOLDS[parameter]) {
    throw new Error(`Unknown parameter: ${parameter}`);
  }
  
  const thresholds = ALL_THRESHOLDS[parameter];
  
  if (value >= thresholds.emergency) {
    return 'emergency';
  } else if (value >= thresholds.critical) {
    return 'critical';
  } else if (value >= thresholds.warning) {
    return 'warning';
  } else if (parameter === 'temperature' && value >= 70.0) {
    return 'satisfactory';  // Temperature 70-85°C is satisfactory
  } else if (parameter === 'vibration' && value >= 1.8) {
    return 'satisfactory';  // Vibration 1.8-4.5 mm/s is satisfactory
  } else if (parameter === 'speed' && value >= 1200.0) {
    return 'satisfactory';  // Speed 1200-1300 RPM is satisfactory
  } else {
    return 'healthy';
  }
};

/**
 * Get overall machine status based on all parameters.
 * 
 * @param {number} temp - Temperature value
 * @param {number} vibration - Vibration value
 * @param {number} speed - Speed value
 * @returns {object} Status information with level, description, priority, colors, and icon
 * 
 * @example
 * getOverallStatus(80.0, 6.0, 1300.0)
 * // returns { level: 'warning', description: 'Monitor closely', priority: 'medium', ... }
 */
export const getOverallStatus = (temp, vibration, speed) => {
  const tempStatus = checkThresholdStatus('temperature', temp);
  const vibStatus = checkThresholdStatus('vibration', vibration);
  const speedStatus = checkThresholdStatus('speed', speed);
  
  // Get the highest severity level
  const statusPriority = { healthy: 0, satisfactory: 1, warning: 2, critical: 3, emergency: 4 };
  const statuses = [tempStatus, vibStatus, speedStatus];
  const highestStatus = statuses.reduce((prev, current) => 
    statusPriority[current] > statusPriority[prev] ? current : prev
  );
  
  // Map to user-friendly descriptions with UI styling
  const statusMap = {
    healthy: {
      level: 'healthy',
      status: 'Healthy',
      description: 'Operating normally',
      priority: 'low',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      icon: '✅'
    },
    satisfactory: {
      level: 'satisfactory',
      status: 'Satisfactory',
      description: 'Monitor closely',
      priority: 'low',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      icon: '📊'
    },
    warning: {
      level: 'warning',
      status: 'High Risk',
      description: 'Attention required',
      priority: 'medium',
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      icon: '⚠️'
    },
    critical: {
      level: 'critical',
      status: 'Critical',
      description: 'Immediate attention required',
      priority: 'high',
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      icon: '🚨'
    },
    emergency: {
      level: 'emergency',
      status: 'Emergency',
      description: 'Shutdown required',
      priority: 'urgent',
      color: 'text-red-800',
      bgColor: 'bg-red-100',
      borderColor: 'border-red-300',
      icon: '🛑'
    }
  };
  
  const result = { ...statusMap[highestStatus] };
  result.details = {
    temperature: { value: temp, status: tempStatus },
    vibration: { value: vibration, status: vibStatus },
    speed: { value: speed, status: speedStatus }
  };
  
  return result;
};

/**
 * Get machine condition with legacy status names for backward compatibility.
 * This function maintains the existing status names used in components.
 * 
 * @param {number} temp - Temperature value
 * @param {number} vibration - Vibration value  
 * @param {number} speed - Speed value
 * @returns {object} Status information with legacy naming
 */
export const getMachineCondition = (temp, vibration, speed) => {
  const status = getOverallStatus(temp, vibration, speed);
  
  // Map new status levels to legacy names for backward compatibility
  const legacyStatusMap = {
    'healthy': 'Healthy',
    'satisfactory': 'Satisfactory',
    'warning': 'High Risk',
    'critical': 'Critical',
    'emergency': 'Critical' // Emergency maps to Critical for UI simplicity
  };
  
  return {
    ...status,
    status: legacyStatusMap[status.level] || status.status
  };
};

// VALIDATION RANGES (for input validation)
// ========================================

export const VALID_RANGES = {
  temperature: { min: -50.0, max: 200.0 },  // °C
  vibration: { min: 0.0, max: 50.0 },       // mm/s
  speed: { min: 0.0, max: 5000.0 }          // RPM
};

/**
 * Validate if a parameter value is within acceptable range.
 * 
 * @param {string} parameter - 'temperature', 'vibration', or 'speed'
 * @param {number} value - Value to validate
 * @returns {boolean} True if valid, False otherwise
 * 
 * @example
 * validateParameter('temperature', 150.0) // returns true
 * validateParameter('temperature', 300.0) // returns false
 */
export const validateParameter = (parameter, value) => {
  if (!VALID_RANGES[parameter]) {
    return false;
  }
  
  const range = VALID_RANGES[parameter];
  return value >= range.min && value <= range.max;
};

// THRESHOLD CHECKING UTILITIES
// ============================

/**
 * Check if any parameter exceeds warning thresholds.
 * 
 * @param {number} temp - Temperature value
 * @param {number} vibration - Vibration value
 * @param {number} speed - Speed value
 * @returns {boolean} True if any parameter is at warning level or above
 */
export const hasWarnings = (temp, vibration, speed) => {
  return temp >= TEMP_THRESHOLDS.warning ||
         vibration >= VIBRATION_THRESHOLDS.warning ||
         speed >= SPEED_THRESHOLDS.warning;
};

/**
 * Check if any parameter exceeds critical thresholds.
 * 
 * @param {number} temp - Temperature value
 * @param {number} vibration - Vibration value
 * @param {number} speed - Speed value
 * @returns {boolean} True if any parameter is at critical level or above
 */
export const hasCriticalIssues = (temp, vibration, speed) => {
  return temp >= TEMP_THRESHOLDS.critical ||
         vibration >= VIBRATION_THRESHOLDS.critical ||
         speed >= SPEED_THRESHOLDS.critical;
};

/**
 * Get count of parameters exceeding each threshold level.
 * 
 * @param {number} temp - Temperature value
 * @param {number} vibration - Vibration value
 * @param {number} speed - Speed value
 * @returns {object} Counts for each threshold level
 */
export const getThresholdCounts = (temp, vibration, speed) => {
  const values = [
    { param: 'temperature', value: temp },
    { param: 'vibration', value: vibration },
    { param: 'speed', value: speed }
  ];
  
  const counts = {
    healthy: 0,
    satisfactory: 0,
    warning: 0,
    critical: 0,
    emergency: 0
  };
  
  values.forEach(({ param, value }) => {
    const status = checkThresholdStatus(param, value);
    counts[status]++;
  });
  
  return counts;
};