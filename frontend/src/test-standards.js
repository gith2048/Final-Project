// Test script for industrial standards integration
// This script tests the frontend industrial standards configuration

import industrialStandards from './config/industrialStandards.js';
import { 
  classifyValue, 
  calculateOverallCondition,
  getThresholdDisplayText,
  INDUSTRIAL_THRESHOLDS 
} from './constants/industrialStandards.js';

// Test data
const testSensorData = [
  { temperature: 45, vibration: 2.1, speed: 1000, expected: 'normal' },
  { temperature: 70, vibration: 4.5, speed: 1200, expected: 'warning' },
  { temperature: 90, vibration: 8.2, speed: 1400, expected: 'critical' },
  { temperature: 65, vibration: 3.0, speed: 1150, expected: 'normal' }, // Boundary values
  { temperature: 85, vibration: 7.0, speed: 1350, expected: 'warning' }  // Boundary values
];

async function testIndustrialStandards() {
  console.log('🧪 Testing Industrial Standards Integration');
  console.log('=' * 50);

  // Test 1: Fetch standards from backend
  console.log('\n📡 Test 1: Fetching standards from backend...');
  try {
    const standards = await industrialStandards.fetchStandards();
    console.log('✅ Standards fetched successfully');
    console.log('📊 Temperature thresholds:', standards.temperature);
    console.log('📊 Vibration thresholds:', standards.vibration);
    console.log('📊 Speed thresholds:', standards.speed);
  } catch (error) {
    console.error('❌ Failed to fetch standards:', error);
  }

  // Test 2: Classification accuracy
  console.log('\n🎯 Test 2: Classification accuracy...');
  let correctClassifications = 0;
  
  for (const testCase of testSensorData) {
    const { temperature, vibration, speed, expected } = testCase;
    
    // Test individual parameter classification
    const tempClass = classifyValue('temperature', temperature);
    const vibClass = classifyValue('vibration', vibration);
    const speedClass = classifyValue('speed', speed);
    
    // Test overall condition calculation
    const overallCondition = calculateOverallCondition(temperature, vibration, speed);
    
    console.log(`\n📋 Test case: T=${temperature}°C, V=${vibration}mm/s, S=${speed}RPM`);
    console.log(`   Temperature: ${tempClass}`);
    console.log(`   Vibration: ${vibClass}`);
    console.log(`   Speed: ${speedClass}`);
    console.log(`   Overall: ${overallCondition} (expected: ${expected})`);
    
    if (overallCondition === expected) {
      console.log('   ✅ Classification correct');
      correctClassifications++;
    } else {
      console.log('   ❌ Classification incorrect');
    }
  }
  
  const accuracy = (correctClassifications / testSensorData.length) * 100;
  console.log(`\n🎯 Classification accuracy: ${accuracy}% (${correctClassifications}/${testSensorData.length})`);

  // Test 3: Threshold display text
  console.log('\n📝 Test 3: Threshold display text...');
  const parameters = ['temperature', 'vibration', 'speed'];
  const conditions = ['normal', 'warning', 'critical'];
  
  for (const param of parameters) {
    console.log(`\n${param.toUpperCase()} thresholds:`);
    for (const condition of conditions) {
      const displayText = getThresholdDisplayText(param, condition);
      console.log(`   ${condition}: ${displayText}`);
    }
  }

  // Test 4: Color and icon mapping
  console.log('\n🎨 Test 4: Color and icon mapping...');
  for (const condition of conditions) {
    const color = industrialStandards.getConditionColor(condition);
    const icon = industrialStandards.getConditionIcon(condition);
    console.log(`   ${condition}: ${icon} ${color}`);
  }

  // Test 5: Boundary value testing
  console.log('\n🔍 Test 5: Boundary value testing...');
  const boundaryTests = [
    { param: 'temperature', value: 65, expected: 'normal' },
    { param: 'temperature', value: 65.1, expected: 'warning' },
    { param: 'temperature', value: 85, expected: 'warning' },
    { param: 'temperature', value: 85.1, expected: 'critical' },
    { param: 'vibration', value: 3.0, expected: 'normal' },
    { param: 'vibration', value: 3.1, expected: 'warning' },
    { param: 'vibration', value: 7.0, expected: 'warning' },
    { param: 'vibration', value: 7.1, expected: 'critical' },
    { param: 'speed', value: 1150, expected: 'normal' },
    { param: 'speed', value: 1151, expected: 'warning' },
    { param: 'speed', value: 1350, expected: 'warning' },
    { param: 'speed', value: 1351, expected: 'critical' }
  ];

  let boundaryCorrect = 0;
  for (const test of boundaryTests) {
    const { param, value, expected } = test;
    const actual = classifyValue(param, value);
    const isCorrect = actual === expected;
    
    console.log(`   ${param} ${value}: ${actual} (expected: ${expected}) ${isCorrect ? '✅' : '❌'}`);
    if (isCorrect) boundaryCorrect++;
  }
  
  const boundaryAccuracy = (boundaryCorrect / boundaryTests.length) * 100;
  console.log(`\n🎯 Boundary test accuracy: ${boundaryAccuracy}% (${boundaryCorrect}/${boundaryTests.length})`);

  // Test 6: Constants consistency
  console.log('\n🔄 Test 6: Constants consistency...');
  const constantsThresholds = INDUSTRIAL_THRESHOLDS;
  const fetchedThresholds = industrialStandards.getAllThresholds();
  
  let consistencyIssues = 0;
  for (const param of parameters) {
    for (const condition of conditions) {
      const constantValue = constantsThresholds[param][condition];
      const fetchedValue = fetchedThresholds[param][condition];
      
      if (JSON.stringify(constantValue) !== JSON.stringify(fetchedValue)) {
        console.log(`   ❌ Inconsistency in ${param}.${condition}:`);
        console.log(`      Constants: ${JSON.stringify(constantValue)}`);
        console.log(`      Fetched: ${JSON.stringify(fetchedValue)}`);
        consistencyIssues++;
      }
    }
  }
  
  if (consistencyIssues === 0) {
    console.log('   ✅ All thresholds are consistent between constants and fetched data');
  } else {
    console.log(`   ❌ Found ${consistencyIssues} consistency issues`);
  }

  // Final summary
  console.log('\n📊 TEST SUMMARY');
  console.log('=' * 30);
  console.log(`✅ Standards fetching: ${standards ? 'PASSED' : 'FAILED'}`);
  console.log(`✅ Classification accuracy: ${accuracy}% ${accuracy >= 80 ? 'PASSED' : 'FAILED'}`);
  console.log(`✅ Boundary testing: ${boundaryAccuracy}% ${boundaryAccuracy >= 90 ? 'PASSED' : 'FAILED'}`);
  console.log(`✅ Constants consistency: ${consistencyIssues === 0 ? 'PASSED' : 'FAILED'}`);
  
  const overallPass = standards && accuracy >= 80 && boundaryAccuracy >= 90 && consistencyIssues === 0;
  console.log(`\n🎯 OVERALL RESULT: ${overallPass ? '✅ PASSED' : '❌ FAILED'}`);
  
  return overallPass;
}

// Export for use in other modules
export default testIndustrialStandards;

// Run tests if this file is executed directly
if (typeof window !== 'undefined') {
  // Browser environment
  window.testIndustrialStandards = testIndustrialStandards;
  console.log('🧪 Industrial standards test function available as window.testIndustrialStandards()');
} else if (typeof module !== 'undefined' && module.exports) {
  // Node.js environment
  module.exports = testIndustrialStandards;
}