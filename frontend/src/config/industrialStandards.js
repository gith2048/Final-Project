// Industrial Standards Configuration
// This file fetches and manages industrial threshold standards from the backend API

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Default fallback thresholds (should match backend industrial_standards.py)
const DEFAULT_THRESHOLDS = {
  temperature: {
    normal: { min: 20, max: 65 },
    warning: { min: 65, max: 85 },
    critical: { min: 85, max: 120 }
  },
  vibration: {
    normal: { min: 0, max: 3.0 },
    warning: { min: 3.0, max: 7.0 },
    critical: { min: 7.0, max: 15.0 }
  },
  speed: {
    normal: { min: 800, max: 1150 },
    warning: { min: 1150, max: 1350 },
    critical: { min: 1350, max: 2000 }
  }
};

class IndustrialStandardsManager {
  constructor() {
    this.thresholds = DEFAULT_THRESHOLDS;
    this.lastFetch = null;
    this.fetchPromise = null;
  }

  /**
   * Fetch industrial standards from backend API
   */
  async fetchStandards() {
    // Prevent multiple simultaneous fetches
    if (this.fetchPromise) {
      return this.fetchPromise;
    }

    // Check if we need to refresh (cache for 5 minutes)
    const now = Date.now();
    if (this.lastFetch && (now - this.lastFetch) < 5 * 60 * 1000) {
      return this.thresholds;
    }

    this.fetchPromise = this._performFetch();
    
    try {
      const result = await this.fetchPromise;
      this.lastFetch = now;
      return result;
    } finally {
      this.fetchPromise = null;
    }
  }

  async _performFetch() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/industrial-standards`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 5000 // 5 second timeout
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Validate the response structure
      if (this._validateThresholds(data)) {
        this.thresholds = data;
        console.log('✅ Industrial standards fetched successfully from backend');
        return this.thresholds;
      } else {
        console.warn('⚠️ Invalid threshold data from backend, using defaults');
        return this.thresholds;
      }
    } catch (error) {
      console.error('❌ Failed to fetch industrial standards from backend:', error);
      console.log('🔄 Using default industrial standards');
      return this.thresholds;
    }
  }

  /**
   * Validate threshold data structure
   */
  _validateThresholds(data) {
    const requiredParams = ['temperature', 'vibration', 'speed'];
    const requiredLevels = ['normal', 'warning', 'critical'];
    const requiredKeys = ['min', 'max'];

    for (const param of requiredParams) {
      if (!data[param]) return false;
      
      for (const level of requiredLevels) {
        if (!data[param][level]) return false;
        
        for (const key of requiredKeys) {
          if (typeof data[param][level][key] !== 'number') return false;
        }
      }
    }
    
    return true;
  }

  /**
   * Get threshold for specific parameter and condition
   */
  getThreshold(parameter, condition) {
    return this.thresholds[parameter]?.[condition] || null;
  }

  /**
   * Get all thresholds
   */
  getAllThresholds() {
    return this.thresholds;
  }

  /**
   * Classify a sensor value based on thresholds
   */
  classifyValue(parameter, value) {
    const thresholds = this.thresholds[parameter];
    if (!thresholds) return 'unknown';

    if (value <= thresholds.normal.max) {
      return 'normal';
    } else if (value <= thresholds.warning.max) {
      return 'warning';
    } else {
      return 'critical';
    }
  }

  /**
   * Get condition color based on classification
   */
  getConditionColor(condition) {
    const colors = {
      normal: '#10B981',    // Green
      warning: '#F59E0B',   // Amber
      critical: '#EF4444',  // Red
      unknown: '#6B7280'    // Gray
    };
    return colors[condition] || colors.unknown;
  }

  /**
   * Get condition icon based on classification
   */
  getConditionIcon(condition) {
    const icons = {
      normal: '✅',
      warning: '⚠️',
      critical: '🚨',
      unknown: '❓'
    };
    return icons[condition] || icons.unknown;
  }

  /**
   * Calculate overall machine condition based on all parameters
   */
  calculateOverallCondition(temperature, vibration, speed) {
    const scores = { normal: 0, warning: 1, critical: 2 };
    
    const tempCondition = this.classifyValue('temperature', temperature);
    const vibCondition = this.classifyValue('vibration', vibration);
    const speedCondition = this.classifyValue('speed', speed);
    
    const totalScore = scores[tempCondition] + scores[vibCondition] + scores[speedCondition];
    
    if (totalScore >= 4) {
      return 'critical';
    } else if (totalScore >= 2) {
      return 'warning';
    } else {
      return 'normal';
    }
  }

  /**
   * Get threshold display text
   */
  getThresholdDisplayText(parameter, condition) {
    const threshold = this.getThreshold(parameter, condition);
    if (!threshold) return 'N/A';

    const units = {
      temperature: '°C',
      vibration: ' mm/s',
      speed: ' RPM'
    };

    const unit = units[parameter] || '';
    
    if (condition === 'normal') {
      return `≤ ${threshold.max}${unit}`;
    } else if (condition === 'critical') {
      return `> ${threshold.min}${unit}`;
    } else {
      return `${threshold.min} - ${threshold.max}${unit}`;
    }
  }
}

// Create singleton instance
const industrialStandards = new IndustrialStandardsManager();

// Initialize standards on module load
industrialStandards.fetchStandards().catch(console.error);

export default industrialStandards;

// Named exports for convenience
export const {
  fetchStandards,
  getThreshold,
  getAllThresholds,
  classifyValue,
  getConditionColor,
  getConditionIcon,
  calculateOverallCondition,
  getThresholdDisplayText
} = industrialStandards;