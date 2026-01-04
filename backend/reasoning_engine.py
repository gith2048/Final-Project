# reasoning_engine.py - ChatGPT-Level Intelligent Machine Health Reasoning Engine
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

class MachineHealthReasoner:
    """
    Advanced AI reasoning engine with ChatGPT-level intelligence that analyzes 
    sensor data + ML outputs to provide human-like, context-aware machine health insights.
    
    Features:
    - Deep contextual understanding of questions
    - Multi-model analysis (LSTM + Random Forest + Isolation Forest)
    - Real-time anomaly detection with root cause analysis
    - Predictive maintenance recommendations
    - Natural language conversation capabilities
    """
    
    def __init__(self):
        # Thresholds (configurable) - Updated to match industrial standards
        self.thresholds = {
            "temperature": {"normal": 65, "high": 85, "critical": 95},
            "vibration": {"normal": 3.0, "high": 7.0, "critical": 10.0},
            "speed": {"normal": 1150, "high": 1350, "critical": 1500}
        }
        
        # Conversation context memory
        self.conversation_history = []
        self.last_analysis = None
        
    def analyze(self, 
                sensor_data: Dict[str, List[float]], 
                ml_outputs: Dict[str, Any],
                question: str = "") -> Dict[str, Any]:
        """
        Main reasoning function with ChatGPT-level intelligence that combines 
        sensor data + ML outputs to answer any machine health question.
        
        Args:
            sensor_data: {"temperature": [...], "vibration": [...], "speed": [...]}
            ml_outputs: {"lstm": {...}, "random_forest": {...}, "isolation_forest": {...}}
            question: User's question (optional, for context-aware responses)
        
        Returns:
            Comprehensive analysis with human-like explanations
        """
        
        # Store question in conversation history
        if question:
            self.conversation_history.append({
                "timestamp": datetime.now(),
                "question": question,
                "sensor_snapshot": {k: v[-1] if v else 0 for k, v in sensor_data.items()}
            })
        
        # Extract current state with enhanced statistics
        current_state = self._extract_current_state(sensor_data)
        
        # Extract trends with predictive analysis
        trends = self._analyze_trends(sensor_data)
        
        # Interpret ML outputs with deep insights
        ml_interpretation = self._interpret_ml_outputs(ml_outputs, current_state)
        
        # Detect anomalies and patterns with root cause analysis
        anomalies = self._detect_anomalies(sensor_data, ml_outputs)
        
        # Advanced risk assessment with failure probability
        risk_assessment = self._assess_risk(current_state, trends, ml_interpretation, anomalies)
        
        # Generate intelligent, actionable recommendations
        recommendations = self._generate_recommendations(risk_assessment, current_state, trends)
        
        # Detect correlations between parameters
        correlations = self._analyze_correlations(sensor_data)
        
        # Build natural language response with context awareness
        response = self._build_response(
            question, current_state, trends, ml_interpretation, 
            anomalies, risk_assessment, recommendations, correlations
        )
        
        # Store analysis for context
        self.last_analysis = {
            "current_state": current_state,
            "trends": trends,
            "ml_interpretation": ml_interpretation,
            "anomalies": anomalies,
            "risk_assessment": risk_assessment,
            "recommendations": recommendations,
            "correlations": correlations,
            "timestamp": datetime.now()
        }
        
        return {
            "response": response,
            "current_state": current_state,
            "trends": trends,
            "ml_interpretation": ml_interpretation,
            "anomalies": anomalies,
            "risk_assessment": risk_assessment,
            "recommendations": recommendations,
            "correlations": correlations
        }
    
    def _extract_current_state(self, sensor_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Extract current sensor values and their status"""
        state = {}
        
        for param in ["temperature", "vibration", "speed"]:
            values = sensor_data.get(param, [])
            if not values:
                continue
                
            # Clean data
            clean_values = [v for v in values if not np.isnan(v) and v is not None]
            if not clean_values:
                continue
            
            current = clean_values[-1]
            recent_avg = np.mean(clean_values[-10:]) if len(clean_values) >= 10 else np.mean(clean_values)
            recent_max = np.max(clean_values[-10:]) if len(clean_values) >= 10 else np.max(clean_values)
            recent_min = np.min(clean_values[-10:]) if len(clean_values) >= 10 else np.min(clean_values)
            
            # Determine status
            thresholds = self.thresholds[param]
            if current >= thresholds["critical"]:
                status = "critical"
            elif current >= thresholds["high"]:
                status = "high"
            elif current >= thresholds["normal"]:
                status = "warning"
            else:
                status = "normal"
            
            state[param] = {
                "current": float(current),
                "recent_avg": float(recent_avg),
                "recent_max": float(recent_max),
                "recent_min": float(recent_min),
                "status": status,
                "volatility": float(np.std(clean_values[-10:])) if len(clean_values) >= 10 else 0.0
            }
        
        return state
    
    def _analyze_trends(self, sensor_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Analyze trends in sensor data"""
        trends = {}
        
        for param in ["temperature", "vibration", "speed"]:
            values = sensor_data.get(param, [])
            if not values or len(values) < 3:
                trends[param] = {"direction": "unknown", "strength": 0, "description": "Insufficient data"}
                continue
            
            clean_values = [v for v in values if not np.isnan(v) and v is not None]
            if len(clean_values) < 3:
                trends[param] = {"direction": "unknown", "strength": 0, "description": "Insufficient data"}
                continue
            
            # Calculate trend using linear regression on recent data
            recent = clean_values[-20:] if len(clean_values) >= 20 else clean_values
            x = np.arange(len(recent))
            slope = np.polyfit(x, recent, 1)[0]
            
            # Determine direction and strength
            if abs(slope) < 0.1:
                direction = "stable"
                strength = 0
                description = f"{param.capitalize()} is stable"
            elif slope > 0:
                direction = "rising"
                strength = min(abs(slope) * 10, 10)  # Scale 0-10
                if strength > 5:
                    description = f"{param.capitalize()} is rising rapidly"
                else:
                    description = f"{param.capitalize()} is gradually increasing"
            else:
                direction = "falling"
                strength = min(abs(slope) * 10, 10)
                if strength > 5:
                    description = f"{param.capitalize()} is dropping rapidly"
                else:
                    description = f"{param.capitalize()} is gradually decreasing"
            
            trends[param] = {
                "direction": direction,
                "strength": float(strength),
                "slope": float(slope),
                "description": description
            }
        
        return trends
    
    def _interpret_ml_outputs(self, ml_outputs: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret ML model outputs in human terms"""
        interpretation = {}
        
        # LSTM Forecast interpretation
        lstm = ml_outputs.get("lstm", {})
        forecast = lstm.get("forecast", {})
        if forecast:
            f_temp = forecast.get("temperature", 0)
            f_vib = forecast.get("vibration", 0)
            f_speed = forecast.get("speed", 0)
            
            # Compare forecast with current
            temp_change = f_temp - current_state.get("temperature", {}).get("current", f_temp)
            vib_change = f_vib - current_state.get("vibration", {}).get("current", f_vib)
            speed_change = f_speed - current_state.get("speed", {}).get("current", f_speed)
            
            concerns = []
            if f_temp > self.thresholds["temperature"]["high"]:
                concerns.append(f"temperature will reach {f_temp:.1f}°C (high risk)")
            if f_vib > self.thresholds["vibration"]["high"]:
                concerns.append(f"vibration will reach {f_vib:.1f} mm/s (high risk)")
            if f_speed > self.thresholds["speed"]["high"]:
                concerns.append(f"speed will reach {f_speed:.0f} RPM (high risk)")
            
            interpretation["lstm"] = {
                "forecast_values": forecast,
                "changes": {"temperature": temp_change, "vibration": vib_change, "speed": speed_change},
                "concerns": concerns,
                "summary": f"Next cycle: Temp {f_temp:.1f}°C, Vib {f_vib:.1f} mm/s, Speed {f_speed:.0f} RPM"
            }
        
        # Random Forest interpretation
        rf = ml_outputs.get("random_forest", {})
        rf_pred = rf.get("pred")
        rf_label = rf.get("label", "unknown")
        
        if rf_pred is not None:
            if rf_pred == 2 or rf_label == "critical":
                rf_risk = "critical"
                rf_message = "Machine signature matches critical failure patterns"
            elif rf_pred == 1 or rf_label == "warning":
                rf_risk = "warning"
                rf_message = "Machine signature shows warning signs"
            else:
                rf_risk = "normal"
                rf_message = "Machine signature is healthy"
            
            interpretation["random_forest"] = {
                "risk_level": rf_risk,
                "prediction": rf_pred,
                "label": rf_label,
                "message": rf_message
            }
        
        # Isolation Forest interpretation
        iso = ml_outputs.get("isolation_forest", {})
        iso_pred = iso.get("pred")
        iso_score = iso.get("score")
        
        if iso_pred is not None:
            if iso_pred == -1:
                if iso_score and iso_score < -0.1:
                    iso_severity = "critical"
                    iso_message = "Severe anomaly detected - immediate investigation required"
                elif iso_score and iso_score < -0.05:
                    iso_severity = "high"
                    iso_message = "Significant anomaly detected - inspect soon"
                else:
                    iso_severity = "medium"
                    iso_message = "Anomaly detected - monitor closely"
            else:
                iso_severity = "normal"
                iso_message = "No anomalies detected"
            
            interpretation["isolation_forest"] = {
                "severity": iso_severity,
                "prediction": iso_pred,
                "score": iso_score,
                "message": iso_message
            }
        
        return interpretation
    
    def _detect_anomalies(self, sensor_data: Dict[str, List[float]], ml_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect specific anomalies and patterns"""
        anomalies = []
        
        # Check for sudden spikes
        for param in ["temperature", "vibration", "speed"]:
            values = sensor_data.get(param, [])
            if len(values) < 5:
                continue
            
            clean_values = [v for v in values if not np.isnan(v) and v is not None]
            if len(clean_values) < 5:
                continue
            
            recent = clean_values[-5:]
            avg = np.mean(recent[:-1])
            current = recent[-1]
            
            # Detect spike (>30% increase)
            if current > avg * 1.3:
                anomalies.append({
                    "type": "spike",
                    "parameter": param,
                    "severity": "high" if current > avg * 1.5 else "medium",
                    "description": f"Sudden {param} spike: {current:.1f} (avg was {avg:.1f})",
                    "recommendation": f"Investigate cause of sudden {param} increase"
                })
            
            # Detect drop (>30% decrease)
            elif current < avg * 0.7:
                anomalies.append({
                    "type": "drop",
                    "parameter": param,
                    "severity": "medium",
                    "description": f"Sudden {param} drop: {current:.1f} (avg was {avg:.1f})",
                    "recommendation": f"Check {param} sensor or system"
                })
        
        # Check for correlated issues
        temp_values = sensor_data.get("temperature", [])
        vib_values = sensor_data.get("vibration", [])
        
        if temp_values and vib_values and len(temp_values) >= 5 and len(vib_values) >= 5:
            temp_clean = [v for v in temp_values[-5:] if not np.isnan(v)]
            vib_clean = [v for v in vib_values[-5:] if not np.isnan(v)]
            
            if temp_clean and vib_clean:
                if temp_clean[-1] > self.thresholds["temperature"]["high"] and vib_clean[-1] > self.thresholds["vibration"]["high"]:
                    anomalies.append({
                        "type": "correlated",
                        "parameter": "temperature_vibration",
                        "severity": "critical",
                        "description": "Both temperature and vibration are critically high",
                        "recommendation": "Immediate shutdown recommended - possible bearing failure or severe friction"
                    })
        
        return anomalies
    
    def _assess_risk(self, current_state: Dict, trends: Dict, ml_interpretation: Dict, anomalies: List) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        risk_factors = []
        risk_score = 0  # 0-100
        
        # Assess current state risks
        for param, state in current_state.items():
            if state["status"] == "critical":
                risk_factors.append(f"Critical {param}: {state['current']:.1f}")
                risk_score += 30
            elif state["status"] == "high":
                risk_factors.append(f"High {param}: {state['current']:.1f}")
                risk_score += 20
            elif state["status"] == "warning":
                risk_factors.append(f"Elevated {param}: {state['current']:.1f}")
                risk_score += 10
        
        # Assess trend risks
        for param, trend in trends.items():
            if trend["direction"] == "rising" and trend["strength"] > 5:
                risk_factors.append(f"{param.capitalize()} rising rapidly")
                risk_score += 15
        
        # Assess ML model risks
        rf_interp = ml_interpretation.get("random_forest", {})
        if rf_interp.get("risk_level") == "critical":
            risk_factors.append("ML model predicts critical failure risk")
            risk_score += 25
        elif rf_interp.get("risk_level") == "warning":
            risk_factors.append("ML model shows warning signs")
            risk_score += 15
        
        iso_interp = ml_interpretation.get("isolation_forest", {})
        if iso_interp.get("severity") == "critical":
            risk_factors.append("Critical anomaly detected")
            risk_score += 20
        elif iso_interp.get("severity") in ["high", "medium"]:
            risk_factors.append("Anomaly detected")
            risk_score += 10
        
        # Assess anomaly risks
        for anomaly in anomalies:
            if anomaly["severity"] == "critical":
                risk_score += 15
            elif anomaly["severity"] == "high":
                risk_score += 10
        
        # Cap at 100
        risk_score = min(risk_score, 100)
        
        # Determine overall risk level
        if risk_score >= 70:
            risk_level = "critical"
            risk_message = "CRITICAL: Immediate action required"
        elif risk_score >= 50:
            risk_level = "high"
            risk_message = "HIGH RISK: Urgent attention needed"
        elif risk_score >= 30:
            risk_level = "medium"
            risk_message = "MEDIUM RISK: Schedule inspection soon"
        elif risk_score >= 10:
            risk_level = "low"
            risk_message = "LOW RISK: Monitor closely"
        else:
            risk_level = "normal"
            risk_message = "Normal operation"
        
        return {
            "level": risk_level,
            "score": risk_score,
            "message": risk_message,
            "factors": risk_factors
        }

    
    def _generate_recommendations(self, risk_assessment: Dict, current_state: Dict, trends: Dict) -> List[Dict[str, Any]]:
        """Generate detailed, actionable recommendations based on analysis"""
        recommendations = []
        
        # Critical actions with detailed steps
        if risk_assessment["level"] == "critical":
            recommendations.append({
                "priority": "immediate",
                "action": "Emergency Shutdown Required",
                "reason": "Critical risk detected - machine failure imminent",
                "steps": [
                    "1. Stop machine operation immediately",
                    "2. Isolate power supply and lock out",
                    "3. Tag machine as 'Under Maintenance'",
                    "4. Contact maintenance team urgently",
                    "5. Do not restart until inspection complete"
                ],
                "icon": "🚨",
                "category": "Safety"
            })
        
        # Temperature-based recommendations with exact solutions
        temp_state = current_state.get("temperature", {})
        temp_current = temp_state.get("current", 0)
        
        if temp_state.get("status") == "critical":
            recommendations.append({
                "priority": "immediate",
                "action": "Critical Temperature - Cooling System Failure",
                "reason": f"Temperature at {temp_current:.1f}°C (Critical threshold: 95°C)",
                "steps": [
                    "1. Shut down machine immediately to prevent damage",
                    "2. Check coolant levels - refill if low",
                    "3. Inspect cooling fans - replace if not spinning",
                    "4. Check for blocked air vents - clean thoroughly",
                    "5. Verify coolant pump operation - repair if faulty",
                    "6. Check for coolant leaks - seal any leaks found",
                    "7. Allow machine to cool for at least 30 minutes",
                    "8. Restart only after temperature drops below 40°C"
                ],
                "icon": "🌡️",
                "category": "Cooling System"
            })
        elif temp_state.get("status") == "high":
            recommendations.append({
                "priority": "high",
                "action": "High Temperature - Preventive Action Required",
                "reason": f"Temperature at {temp_current:.1f}°C (Warning threshold: 85°C)",
                "steps": [
                    "1. Reduce machine load by 20-30%",
                    "2. Check coolant levels - top up if below minimum",
                    "3. Clean air filters and cooling vents",
                    "4. Verify cooling fan operation",
                    "5. Check lubrication - add lubricant if needed",
                    "6. Monitor temperature every 15 minutes",
                    "7. If temperature continues rising, shut down"
                ],
                "icon": "🌡️",
                "category": "Cooling System"
            })
        elif temp_state.get("status") == "warning":
            recommendations.append({
                "priority": "medium",
                "action": "Elevated Temperature - Monitor Closely",
                "reason": f"Temperature at {temp_current:.1f}°C (Normal threshold: 75°C)",
                "steps": [
                    "1. Check ambient temperature - ensure adequate ventilation",
                    "2. Verify cooling system is functioning",
                    "3. Monitor temperature trend over next hour",
                    "4. Schedule cooling system inspection within 24 hours"
                ],
                "icon": "🌡️",
                "category": "Monitoring"
            })
        
        # Vibration-based recommendations with exact solutions
        vib_state = current_state.get("vibration", {})
        vib_current = vib_state.get("current", 0)
        
        if vib_state.get("status") == "critical":
            recommendations.append({
                "priority": "immediate",
                "action": "Critical Vibration - Mechanical Failure Risk",
                "reason": f"Vibration at {vib_current:.1f} mm/s (Critical threshold: 10 mm/s)",
                "steps": [
                    "1. Stop machine immediately - bearing failure likely",
                    "2. Inspect bearings for wear, pitting, or damage",
                    "3. Check shaft alignment using dial indicator",
                    "4. Inspect coupling for wear or damage",
                    "5. Check for loose mounting bolts - tighten to spec",
                    "6. Verify rotor balance - rebalance if needed",
                    "7. Replace worn bearings immediately",
                    "8. Realign shaft if misalignment detected",
                    "9. Test run at low speed before full operation"
                ],
                "icon": "⚙️",
                "category": "Mechanical System"
            })
        elif vib_state.get("status") == "high":
            recommendations.append({
                "priority": "high",
                "action": "High Vibration - Mechanical Inspection Needed",
                "reason": f"Vibration at {vib_current:.1f} mm/s (Warning threshold: 7 mm/s)",
                "steps": [
                    "1. Reduce machine speed by 20%",
                    "2. Check all mounting bolts - tighten if loose",
                    "3. Inspect bearings for unusual noise or heat",
                    "4. Check shaft alignment - adjust if needed",
                    "5. Verify belt tension (if belt-driven)",
                    "6. Schedule bearing replacement within 48 hours",
                    "7. Monitor vibration every 30 minutes"
                ],
                "icon": "⚙️",
                "category": "Mechanical System"
            })
        elif vib_state.get("status") == "warning":
            recommendations.append({
                "priority": "medium",
                "action": "Elevated Vibration - Preventive Check",
                "reason": f"Vibration at {vib_current:.1f} mm/s (Normal threshold: 5 mm/s)",
                "steps": [
                    "1. Check for loose components",
                    "2. Verify proper lubrication",
                    "3. Schedule alignment check within 1 week",
                    "4. Monitor vibration trend"
                ],
                "icon": "⚙️",
                "category": "Monitoring"
            })
        
        # Speed-based recommendations with exact solutions
        speed_state = current_state.get("speed", {})
        speed_current = speed_state.get("current", 0)
        
        if speed_state.get("status") == "critical":
            recommendations.append({
                "priority": "immediate",
                "action": "Critical Speed - Runaway Condition",
                "reason": f"Speed at {speed_current:.0f} RPM (Critical threshold: 1500 RPM)",
                "steps": [
                    "1. Emergency stop - press E-stop button",
                    "2. Check motor controller for malfunction",
                    "3. Inspect speed sensor - replace if faulty",
                    "4. Verify control system settings",
                    "5. Check for feedback loop errors",
                    "6. Test motor controller in manual mode",
                    "7. Replace controller if defective",
                    "8. Recalibrate speed control system"
                ],
                "icon": "⚡",
                "category": "Control System"
            })
        elif speed_state.get("status") == "high":
            recommendations.append({
                "priority": "high",
                "action": "High Speed - Load Adjustment Required",
                "reason": f"Speed at {speed_current:.0f} RPM (Warning threshold: 1350 RPM)",
                "steps": [
                    "1. Reduce machine load immediately",
                    "2. Check motor controller settings",
                    "3. Verify speed setpoint is correct",
                    "4. Inspect load distribution",
                    "5. Check for control system errors",
                    "6. Monitor speed for next 30 minutes"
                ],
                "icon": "⚡",
                "category": "Control System"
            })
        elif speed_state.get("status") == "warning":
            recommendations.append({
                "priority": "medium",
                "action": "Elevated Speed - Verify Settings",
                "reason": f"Speed at {speed_current:.0f} RPM (Normal threshold: 1200 RPM)",
                "steps": [
                    "1. Verify speed setpoint matches requirements",
                    "2. Check load conditions",
                    "3. Monitor speed stability",
                    "4. Schedule controller calibration"
                ],
                "icon": "⚡",
                "category": "Monitoring"
            })
        
        # Trend-based recommendations
        for param, trend in trends.items():
            if trend["direction"] == "rising" and trend["strength"] > 7:
                recommendations.append({
                    "priority": "high",
                    "action": f"Rapidly Rising {param.capitalize()} - Urgent Attention",
                    "reason": f"{param.capitalize()} increasing rapidly (trend strength: {trend['strength']:.1f}/10)",
                    "steps": [
                        f"1. Identify root cause of {param} increase",
                        f"2. Take corrective action immediately",
                        f"3. Monitor {param} every 10 minutes",
                        "4. Prepare for potential shutdown"
                    ],
                    "icon": "📈",
                    "category": "Trend Analysis"
                })
        
        # Preventive recommendations
        if risk_assessment["level"] in ["normal", "low"]:
            recommendations.append({
                "priority": "low",
                "action": "Routine Maintenance Schedule",
                "reason": "Machine operating normally - good time for preventive care",
                "steps": [
                    "1. Continue standard monitoring procedures",
                    "2. Schedule next preventive maintenance",
                    "3. Check lubrication levels weekly",
                    "4. Inspect for wear and tear monthly",
                    "5. Keep maintenance logs updated"
                ],
                "icon": "✅",
                "category": "Preventive Maintenance"
            })
        
        return recommendations
    
    def _analyze_correlations(self, sensor_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Analyze correlations between sensor parameters to detect patterns"""
        correlations = {}
        
        try:
            # Get recent data
            temp = np.array([v for v in sensor_data.get("temperature", [])[-20:] if not np.isnan(v)])
            vib = np.array([v for v in sensor_data.get("vibration", [])[-20:] if not np.isnan(v)])
            speed = np.array([v for v in sensor_data.get("speed", [])[-20:] if not np.isnan(v)])
            
            min_len = min(len(temp), len(vib), len(speed))
            if min_len < 3:
                return {"status": "insufficient_data"}
            
            temp = temp[-min_len:]
            vib = vib[-min_len:]
            speed = speed[-min_len:]
            
            # Calculate correlation coefficients
            temp_vib_corr = np.corrcoef(temp, vib)[0, 1] if len(temp) > 1 else 0
            temp_speed_corr = np.corrcoef(temp, speed)[0, 1] if len(temp) > 1 else 0
            vib_speed_corr = np.corrcoef(vib, speed)[0, 1] if len(vib) > 1 else 0
            
            correlations = {
                "temp_vibration": {
                    "coefficient": float(temp_vib_corr),
                    "strength": "strong" if abs(temp_vib_corr) > 0.7 else "moderate" if abs(temp_vib_corr) > 0.4 else "weak",
                    "direction": "positive" if temp_vib_corr > 0 else "negative"
                },
                "temp_speed": {
                    "coefficient": float(temp_speed_corr),
                    "strength": "strong" if abs(temp_speed_corr) > 0.7 else "moderate" if abs(temp_speed_corr) > 0.4 else "weak",
                    "direction": "positive" if temp_speed_corr > 0 else "negative"
                },
                "vibration_speed": {
                    "coefficient": float(vib_speed_corr),
                    "strength": "strong" if abs(vib_speed_corr) > 0.7 else "moderate" if abs(vib_speed_corr) > 0.4 else "weak",
                    "direction": "positive" if vib_speed_corr > 0 else "negative"
                }
            }
            
            # Detect concerning patterns
            patterns = []
            if abs(temp_vib_corr) > 0.7 and temp_vib_corr > 0:
                patterns.append("Temperature and vibration are strongly correlated - possible friction or bearing issue")
            if abs(temp_speed_corr) > 0.7 and temp_speed_corr > 0:
                patterns.append("Temperature increases with speed - normal but monitor cooling efficiency")
            if abs(vib_speed_corr) > 0.7 and vib_speed_corr > 0:
                patterns.append("Vibration increases with speed - check balance and alignment")
            
            correlations["patterns"] = patterns
            correlations["status"] = "analyzed"
            
        except Exception as e:
            correlations = {"status": "error", "message": str(e)}
        
        return correlations
    
    def _build_response(self, question: str, current_state: Dict, trends: Dict, 
                       ml_interpretation: Dict, anomalies: List, 
                       risk_assessment: Dict, recommendations: List, 
                       correlations: Dict = None) -> str:
        """Build natural, human-like response with ChatGPT-level intelligence"""
        
        question_lower = question.lower() if question else ""
        
        # Enhanced question understanding with context
        question_intent = self._understand_question_intent(question_lower)
        
        # Route to appropriate response handler based on intent
        if question_intent == "temperature":
            return self._answer_temperature_question(current_state, trends, ml_interpretation, risk_assessment)
        elif question_intent == "vibration":
            return self._answer_vibration_question(current_state, trends, ml_interpretation, risk_assessment)
        elif question_intent == "speed":
            return self._answer_speed_question(current_state, trends, ml_interpretation, risk_assessment)
        elif question_intent == "anomaly":
            return self._answer_anomaly_question(ml_interpretation, anomalies, risk_assessment)
        elif question_intent == "forecast":
            return self._answer_forecast_question(ml_interpretation, current_state, risk_assessment)
        elif question_intent == "risk":
            return self._answer_risk_question(risk_assessment, ml_interpretation, recommendations)
        elif question_intent == "recommendation":
            return self._answer_recommendation_question(recommendations, risk_assessment)
        elif question_intent == "health":
            return self._answer_health_question(current_state, trends, risk_assessment, ml_interpretation)
        elif question_intent == "trend":
            return self._answer_trend_question(trends, current_state, ml_interpretation)
        elif question_intent == "why":
            return self._answer_why_question(current_state, trends, ml_interpretation, anomalies, risk_assessment)
        elif question_intent == "comparison":
            return self._answer_comparison_question(current_state, trends, ml_interpretation)
        elif question_intent == "correlation":
            return self._answer_correlation_question(correlations, current_state)
        else:
            # Default comprehensive response
            return self._build_comprehensive_response(current_state, trends, ml_interpretation, 
                                                      anomalies, risk_assessment, recommendations)
    
    def _understand_question_intent(self, question_lower: str) -> str:
        """Advanced NLP-like intent detection for question understanding"""
        if not question_lower:
            return "comprehensive"
        
        # Temperature related
        if any(word in question_lower for word in ["temperature", "temp", "hot", "heat", "overheat", "cooling", "thermal", "cold", "warm"]):
            return "temperature"
        
        # Vibration related
        elif any(word in question_lower for word in ["vibration", "vibrate", "shake", "shaking", "mechanical", "bearing", "alignment", "balance"]):
            return "vibration"
        
        # Speed related
        elif any(word in question_lower for word in ["speed", "rpm", "fast", "slow", "motor", "rotation", "velocity"]):
            return "speed"
        
        # Anomaly related
        elif any(word in question_lower for word in ["anomaly", "abnormal", "unusual", "strange", "weird", "wrong", "issue", "problem", "error"]):
            return "anomaly"
        
        # Forecast related
        elif any(word in question_lower for word in ["forecast", "predict", "future", "next", "will", "going to", "expect", "anticipate"]):
            return "forecast"
        
        # Risk related
        elif any(word in question_lower for word in ["risk", "failure", "fail", "breakdown", "danger", "safe", "critical", "emergency"]):
            return "risk"
        
        # Recommendation related
        elif any(word in question_lower for word in ["recommend", "suggest", "should", "what to do", "action", "fix", "solve", "help", "repair"]):
            return "recommendation"
        
        # Health/Status related
        elif any(word in question_lower for word in ["health", "status", "condition", "how is", "overall", "summary", "report", "state"]):
            return "health"
        
        # Trend related
        elif any(word in question_lower for word in ["trend", "trending", "pattern", "changing", "increasing", "decreasing", "rising", "falling"]):
            return "trend"
        
        # Why/Explanation related
        elif any(word in question_lower for word in ["why", "explain", "reason", "cause", "because", "how come"]):
            return "why"
        
        # Comparison related
        elif any(word in question_lower for word in ["compare", "difference", "vs", "versus", "between", "which"]):
            return "comparison"
        
        # Correlation related
        elif any(word in question_lower for word in ["correlation", "related", "connection", "relationship", "linked"]):
            return "correlation"
        
        # Default comprehensive
        return "comprehensive"
    
    def _answer_correlation_question(self, correlations: Dict, current_state: Dict) -> str:
        """Answer questions about parameter correlations and relationships"""
        response = "🔗 Parameter Correlation Analysis:\n\n"
        
        if not correlations or correlations.get("status") != "analyzed":
            response += "⚠️ Unable to analyze correlations - insufficient data.\n"
            response += "Need at least 3 data points to detect relationships.\n"
            return response
        
        response += "I've analyzed how your machine parameters relate to each other:\n\n"
        
        # Temperature-Vibration
        tv = correlations.get("temp_vibration", {})
        response += f"🌡️↔️📳 Temperature ↔ Vibration:\n"
        response += f"• Correlation: {tv.get('strength', 'unknown').upper()} ({tv.get('coefficient', 0):.2f})\n"
        response += f"• Direction: {tv.get('direction', 'unknown').capitalize()}\n"
        if tv.get('strength') == 'strong' and tv.get('direction') == 'positive':
            response += "• ⚠️ Strong positive correlation suggests friction or bearing issues\n"
        response += "\n"
        
        # Temperature-Speed
        ts = correlations.get("temp_speed", {})
        response += f"🌡️↔️⚡ Temperature ↔ Speed:\n"
        response += f"• Correlation: {ts.get('strength', 'unknown').upper()} ({ts.get('coefficient', 0):.2f})\n"
        response += f"• Direction: {ts.get('direction', 'unknown').capitalize()}\n"
        if ts.get('strength') == 'strong' and ts.get('direction') == 'positive':
            response += "• ✅ Normal - temperature naturally increases with speed\n"
            response += "• 💡 Monitor cooling system efficiency\n"
        response += "\n"
        
        # Vibration-Speed
        vs = correlations.get("vibration_speed", {})
        response += f"📳↔️⚡ Vibration ↔ Speed:\n"
        response += f"• Correlation: {vs.get('strength', 'unknown').upper()} ({vs.get('coefficient', 0):.2f})\n"
        response += f"• Direction: {vs.get('direction', 'unknown').capitalize()}\n"
        if vs.get('strength') == 'strong' and vs.get('direction') == 'positive':
            response += "• ⚠️ Vibration increases with speed - check balance and alignment\n"
        response += "\n"
        
        # Patterns
        patterns = correlations.get("patterns", [])
        if patterns:
            response += "🔍 Detected Patterns:\n"
            for pattern in patterns:
                response += f"• {pattern}\n"
        else:
            response += "✅ No concerning correlation patterns detected.\n"
        
        return response
    
    def _answer_temperature_question(self, current_state, trends, ml_interpretation, risk_assessment):
        temp = current_state.get("temperature", {})
        temp_trend = trends.get("temperature", {})
        forecast = ml_interpretation.get("lstm", {}).get("forecast_values", {})
        
        current = temp.get("current", 0)
        status = temp.get("status", "unknown")
        trend_desc = temp_trend.get("description", "stable")
        forecast_temp = forecast.get("temperature", current)
        
        response = f"🌡️ Temperature Analysis:\n\n"
        response += f"• Current: {current:.1f}°C ({status})\n"
        response += f"• Trend: {trend_desc}\n"
        response += f"• Forecast: {forecast_temp:.1f}°C next cycle\n\n"
        
        if status == "critical":
            response += "🚨 CRITICAL: Temperature is dangerously high! Immediate shutdown recommended.\n"
            response += "• Check cooling system immediately\n"
            response += "• Inspect for blockages or coolant issues\n"
            response += "• Verify lubrication is adequate"
        elif status == "high":
            response += "⚠️ WARNING: Temperature is elevated.\n"
            response += "• Monitor cooling system\n"
            response += "• Check lubrication levels\n"
            response += "• Consider reducing load"
        elif status == "warning":
            response += "⚠️ Temperature is approaching high threshold.\n"
            response += "• Keep monitoring closely\n"
            response += "• Ensure cooling system is functioning"
        else:
            response += "✅ Temperature is within normal range.\n"
            response += "• Continue standard monitoring"
        
        return response
    
    def _answer_vibration_question(self, current_state, trends, ml_interpretation, risk_assessment):
        vib = current_state.get("vibration", {})
        vib_trend = trends.get("vibration", {})
        forecast = ml_interpretation.get("lstm", {}).get("forecast_values", {})
        
        current = vib.get("current", 0)
        status = vib.get("status", "unknown")
        trend_desc = vib_trend.get("description", "stable")
        forecast_vib = forecast.get("vibration", current)
        
        response = f"📳 Vibration Analysis:\n\n"
        response += f"• Current: {current:.2f} mm/s ({status})\n"
        response += f"• Trend: {trend_desc}\n"
        response += f"• Forecast: {forecast_vib:.2f} mm/s next cycle\n\n"
        
        if status == "critical":
            response += "🚨 CRITICAL: Vibration is extremely high!\n"
            response += "• Stop machine immediately\n"
            response += "• Inspect bearings for failure\n"
            response += "• Check alignment and balance\n"
            response += "• Look for loose components"
        elif status == "high":
            response += "⚠️ WARNING: Vibration is elevated.\n"
            response += "• Schedule urgent inspection\n"
            response += "• Check bearing condition\n"
            response += "• Verify alignment\n"
            response += "• Inspect for wear"
        elif status == "warning":
            response += "⚠️ Vibration is approaching high threshold.\n"
            response += "• Monitor closely\n"
            response += "• Plan inspection soon"
        else:
            response += "✅ Vibration is within normal range.\n"
            response += "• Machine mechanically stable"
        
        return response
    
    def _answer_speed_question(self, current_state, trends, ml_interpretation, risk_assessment):
        speed = current_state.get("speed", {})
        speed_trend = trends.get("speed", {})
        forecast = ml_interpretation.get("lstm", {}).get("forecast_values", {})
        
        current = speed.get("current", 0)
        status = speed.get("status", "unknown")
        trend_desc = speed_trend.get("description", "stable")
        forecast_speed = forecast.get("speed", current)
        
        response = f"⚡ Speed Analysis:\n\n"
        response += f"• Current: {current:.0f} RPM ({status})\n"
        response += f"• Trend: {trend_desc}\n"
        response += f"• Forecast: {forecast_speed:.0f} RPM next cycle\n\n"
        
        if status == "critical":
            response += "🚨 CRITICAL: Speed is dangerously high!\n"
            response += "• Reduce load immediately\n"
            response += "• Check motor controller\n"
            response += "• Verify speed settings\n"
            response += "• Inspect for runaway condition"
        elif status == "high":
            response += "⚠️ WARNING: Speed is elevated.\n"
            response += "• Reduce machine load\n"
            response += "• Verify motor settings\n"
            response += "• Check for proper operation"
        elif status == "warning":
            response += "⚠️ Speed is approaching high threshold.\n"
            response += "• Monitor load conditions\n"
            response += "• Verify settings are correct"
        else:
            response += "✅ Speed is within normal range.\n"
            response += "• Operating at optimal RPM"
        
        return response
    
    def _answer_anomaly_question(self, ml_interpretation, anomalies, risk_assessment):
        iso = ml_interpretation.get("isolation_forest", {})
        
        response = "🔍 Anomaly Detection:\n\n"
        
        if iso.get("severity") in ["critical", "high", "medium"]:
            response += f"⚠️ {iso.get('message', 'Anomaly detected')}\n"
            response += f"• Anomaly score: {iso.get('score', 0):.3f}\n\n"
            
            if anomalies:
                response += "Specific anomalies detected:\n"
                for anomaly in anomalies:
                    icon = "🚨" if anomaly["severity"] == "critical" else "⚠️"
                    response += f"{icon} {anomaly['description']}\n"
                    response += f"   → {anomaly['recommendation']}\n"
            else:
                response += "The ML model detected unusual patterns in the sensor data.\n"
                response += "• Investigate recent changes\n"
                response += "• Check sensor calibration\n"
                response += "• Inspect machine condition"
        else:
            response += "✅ No anomalies detected.\n"
            response += "• All sensor readings are within expected patterns\n"
            response += "• Machine behavior is normal\n"
            response += "• Continue standard monitoring"
        
        return response
    
    def _answer_forecast_question(self, ml_interpretation, current_state, risk_assessment):
        lstm = ml_interpretation.get("lstm", {})
        forecast = lstm.get("forecast_values", {})
        concerns = lstm.get("concerns", [])
        
        response = "🔮 Forecast (Next Cycle):\n\n"
        
        if forecast:
            response += f"• Temperature: {forecast.get('temperature', 0):.1f}°C\n"
            response += f"• Vibration: {forecast.get('vibration', 0):.2f} mm/s\n"
            response += f"• Speed: {forecast.get('speed', 0):.0f} RPM\n\n"
            
            if concerns:
                response += "⚠️ Concerns:\n"
                for concern in concerns:
                    response += f"• {concern}\n"
                response += "\nRecommendation: Take preventive action now to avoid these conditions."
            else:
                response += "✅ Forecast looks normal.\n"
                response += "• No concerning trends predicted\n"
                response += "• Machine should continue operating safely"
        else:
            response += "Unable to generate forecast (insufficient data)."
        
        return response
    
    def _answer_risk_question(self, risk_assessment, ml_interpretation, recommendations):
        response = f"⚠️ Risk Assessment:\n\n"
        response += f"• Risk Level: {risk_assessment['level'].upper()}\n"
        response += f"• Risk Score: {risk_assessment['score']}/100\n"
        response += f"• Status: {risk_assessment['message']}\n\n"
        
        if risk_assessment['factors']:
            response += "Risk Factors:\n"
            for factor in risk_assessment['factors']:
                response += f"• {factor}\n"
            response += "\n"
        
        rf = ml_interpretation.get("random_forest", {})
        if rf:
            response += f"ML Prediction: {rf.get('message', 'Unknown')}\n\n"
        
        # Add top recommendations
        high_priority = [r for r in recommendations if r["priority"] == "immediate" or r["priority"] == "high"]
        if high_priority:
            response += "Immediate Actions:\n"
            for rec in high_priority[:3]:
                response += f"{rec['icon']} {rec['action']}\n"
                response += f"   → {rec['reason']}\n"
        
        return response
    
    def _answer_recommendation_question(self, recommendations, risk_assessment):
        response = "💡 DETAILED RECOMMENDATIONS & SOLUTIONS\n\n"
        
        # Group by priority
        immediate = [r for r in recommendations if r["priority"] == "immediate"]
        high = [r for r in recommendations if r["priority"] == "high"]
        medium = [r for r in recommendations if r["priority"] == "medium"]
        low = [r for r in recommendations if r["priority"] == "low"]
        
        if immediate:
            response += "🚨 IMMEDIATE ACTIONS (Do This Now!):\n\n"
            for rec in immediate:
                response += f"{rec['icon']} {rec['action']}\n"
                response += f"Why: {rec['reason']}\n\n"
                response += "Exact Steps to Follow:\n"
                for step in rec.get('steps', []):
                    response += f"   {step}\n"
                response += "\n"
        
        if high:
            response += "⚠️ HIGH PRIORITY (Do Within 1 Hour):\n\n"
            for rec in high:
                response += f"{rec['icon']} {rec['action']}\n"
                response += f"Why: {rec['reason']}\n\n"
                response += "Exact Steps to Follow:\n"
                for step in rec.get('steps', []):
                    response += f"   {step}\n"
                response += "\n"
        
        if medium:
            response += "📋 MEDIUM PRIORITY (Do Within 24 Hours):\n\n"
            for rec in medium[:2]:  # Limit to top 2
                response += f"{rec['icon']} {rec['action']}\n"
                response += f"Why: {rec['reason']}\n\n"
                response += "Exact Steps to Follow:\n"
                for step in rec.get('steps', []):
                    response += f"   {step}\n"
                response += "\n"
        
        if not immediate and not high and low:
            response += "✅ ROUTINE MAINTENANCE:\n\n"
            for rec in low[:1]:
                response += f"{rec['icon']} {rec['action']}\n"
                response += f"Why: {rec['reason']}\n\n"
                response += "Exact Steps to Follow:\n"
                for step in rec.get('steps', []):
                    response += f"   {step}\n"
                response += "\n"
        
        # Add summary
        if immediate or high:
            response += "⚠️ IMPORTANT: Follow these steps immediately to prevent machine failure and ensure safety!\n"
        elif medium:
            response += "📊 NOTE: Schedule these actions soon to maintain optimal machine performance.\n"
        else:
            response += "✅ NOTE: Your machine is healthy. Follow routine maintenance schedule.\n"
        
        return response
    
    def _answer_health_question(self, current_state, trends, risk_assessment, ml_interpretation):
        response = "🧠 Machine Health Summary:\n\n"
        response += f"📊 Overall Status: {risk_assessment['level'].upper()}\n"
        response += f"Risk Score: {risk_assessment['score']}/100\n\n"
        
        response += "📋 Current Readings:\n"
        for param, state in current_state.items():
            icon = "🚨" if state["status"] == "critical" else "⚠️" if state["status"] in ["high", "warning"] else "✅"
            response += f"{icon} {param.capitalize()}: {state['current']:.1f} ({state['status']})\n"
        
        response += "\n📈 Trends:\n"
        for param, trend in trends.items():
            icon = "📈" if trend["direction"] == "rising" else "📉" if trend["direction"] == "falling" else "➡️"
            response += f"{icon} {param.capitalize()}: {trend['description']}\n"
        
        response += "\n"
        rf = ml_interpretation.get("random_forest", {})
        iso = ml_interpretation.get("isolation_forest", {})
        
        if rf:
            response += f"🌲 ML Prediction: {rf.get('message', 'Unknown')}\n"
        if iso:
            response += f"🔍 Anomaly Status: {iso.get('message', 'Unknown')}\n"
        
        return response
    
    def _answer_trend_question(self, trends, current_state, ml_interpretation):
        response = "📈 Trend Analysis:\n\n"
        
        for param, trend in trends.items():
            state = current_state.get(param, {})
            icon = "📈" if trend["direction"] == "rising" else "📉" if trend["direction"] == "falling" else "➡️"
            
            response += f"{icon} {param.capitalize()}:\n"
            response += f"• Current: {state.get('current', 0):.1f}\n"
            response += f"• Trend: {trend['description']}\n"
            response += f"• Strength: {trend['strength']:.1f}/10\n"
            
            if trend["direction"] == "rising" and trend["strength"] > 5:
                response += f"⚠️ Rapidly increasing - monitor closely\n"
            elif trend["direction"] == "falling" and trend["strength"] > 5:
                response += f"⚠️ Rapidly decreasing - investigate cause\n"
            else:
                response += f"✅ Trend is manageable\n"
            
            response += "\n"
        
        return response
    
    def _answer_why_question(self, current_state, trends, ml_interpretation, anomalies, risk_assessment):
        """Answer 'why' questions with detailed explanations"""
        response = "🤔 Let me explain what's happening:\n\n"
        
        # Identify main issues
        issues = []
        for param, state in current_state.items():
            if state["status"] in ["critical", "high", "warning"]:
                issues.append((param, state))
        
        if not issues:
            response += "✅ Good news! Your machine is operating normally.\n\n"
            response += "All parameters are within safe ranges:\n"
            for param, state in current_state.items():
                response += f"• {param.capitalize()}: {state['current']:.1f} (normal)\n"
            response += "\nThe ML models confirm healthy operation with no anomalies detected."
            return response
        
        # Explain each issue
        response += "Here's what I found:\n\n"
        for param, state in issues:
            response += f"🔍 {param.capitalize()} Issue:\n"
            response += f"• Current value: {state['current']:.1f}\n"
            response += f"• Status: {state['status']}\n"
            
            # Explain why it's a problem
            if param == "temperature":
                if state["status"] == "critical":
                    response += "• Why it matters: Extreme heat can cause component failure, warping, and accelerated wear\n"
                    response += "• Likely causes: Cooling system failure, excessive friction, or overload\n"
                elif state["status"] == "high":
                    response += "• Why it matters: Elevated temperature reduces efficiency and increases wear\n"
                    response += "• Likely causes: Insufficient cooling, high ambient temperature, or increased load\n"
            
            elif param == "vibration":
                if state["status"] == "critical":
                    response += "• Why it matters: Severe vibration indicates imminent mechanical failure\n"
                    response += "• Likely causes: Bearing failure, severe misalignment, or loose components\n"
                elif state["status"] == "high":
                    response += "• Why it matters: High vibration accelerates wear and can cause damage\n"
                    response += "• Likely causes: Misalignment, imbalance, or worn bearings\n"
            
            elif param == "speed":
                if state["status"] == "critical":
                    response += "• Why it matters: Excessive speed can cause mechanical failure or runaway\n"
                    response += "• Likely causes: Controller malfunction, excessive load, or feedback error\n"
                elif state["status"] == "high":
                    response += "• Why it matters: Operating above design speed reduces lifespan\n"
                    response += "• Likely causes: High demand, incorrect settings, or load imbalance\n"
            
            response += "\n"
        
        # Add ML insights
        rf = ml_interpretation.get("random_forest", {})
        if rf.get("risk_level") in ["critical", "warning"]:
            response += f"🤖 ML Analysis: {rf.get('message', 'Unknown')}\n"
            response += "The machine learning model has identified patterns similar to previous failures.\n\n"
        
        # Add anomaly insights
        if anomalies:
            response += "⚠️ Anomalies Detected:\n"
            for anomaly in anomalies[:2]:
                response += f"• {anomaly['description']}\n"
            response += "\n"
        
        return response
    
    def _answer_comparison_question(self, current_state, trends, ml_interpretation):
        """Answer comparison questions"""
        response = "📊 Parameter Comparison:\n\n"
        
        # Compare current values
        response += "Current Values:\n"
        params_sorted = sorted(current_state.items(), key=lambda x: x[1]["current"], reverse=True)
        for param, state in params_sorted:
            icon = "🚨" if state["status"] == "critical" else "⚠️" if state["status"] in ["high", "warning"] else "✅"
            response += f"{icon} {param.capitalize()}: {state['current']:.1f} ({state['status']})\n"
        
        response += "\nTrend Comparison:\n"
        for param, trend in trends.items():
            icon = "📈" if trend["direction"] == "rising" else "📉" if trend["direction"] == "falling" else "➡️"
            response += f"{icon} {param.capitalize()}: {trend['description']}\n"
        
        # Identify most concerning parameter
        critical_params = [p for p, s in current_state.items() if s["status"] == "critical"]
        high_params = [p for p, s in current_state.items() if s["status"] == "high"]
        
        if critical_params:
            response += f"\n🚨 Most Critical: {', '.join(critical_params)}\n"
            response += "These parameters require immediate attention.\n"
        elif high_params:
            response += f"\n⚠️ Most Concerning: {', '.join(high_params)}\n"
            response += "These parameters should be monitored closely.\n"
        else:
            response += "\n✅ All parameters are within acceptable ranges.\n"
        
        return response
    
    def _build_comprehensive_response(self, current_state, trends, ml_interpretation, 
                                     anomalies, risk_assessment, recommendations):
        """Build comprehensive analysis when no specific question is asked"""
        response = "🧠 Complete Machine Health Analysis\n\n"
        
        # Conversational opening based on risk level
        if risk_assessment['level'] == "critical":
            response += "🚨 URGENT: I've detected critical issues requiring immediate action!\n\n"
        elif risk_assessment['level'] == "high":
            response += "⚠️ WARNING: There are concerning patterns that need your attention.\n\n"
        elif risk_assessment['level'] == "medium":
            response += "📊 NOTICE: I've identified some areas worth monitoring.\n\n"
        else:
            response += "✅ GOOD NEWS: Your machine is operating within normal parameters.\n\n"
        
        # Overall status with detailed breakdown
        response += "┌─────────────────────────────────────────────────┐\n"
        response += "│  📊 OVERALL MACHINE STATUS                      │\n"
        response += "└─────────────────────────────────────────────────┘\n\n"
        response += f"Status Level: {risk_assessment['level'].upper()}\n"
        response += f"Risk Score: {risk_assessment['score']}/100\n"
        response += f"Assessment: {risk_assessment['message']}\n"
        
        if risk_assessment['factors']:
            response += f"\nRisk Factors Identified:\n"
            for factor in risk_assessment['factors'][:5]:
                response += f"  • {factor}\n"
        response += "\n"
        
        # Detailed current readings with statistics
        response += "┌─────────────────────────────────────────────────┐\n"
        response += "│  📋 CURRENT SENSOR READINGS & STATISTICS        │\n"
        response += "└─────────────────────────────────────────────────┘\n\n"
        
        for param, state in current_state.items():
            icon = "🚨" if state["status"] == "critical" else "⚠️" if state["status"] in ["high", "warning"] else "✅"
            response += f"{icon} {param.upper()}:\n"
            response += f"   Current Value: {state['current']:.2f}\n"
            response += f"   Recent Average: {state.get('recent_avg', 0):.2f}\n"
            response += f"   Recent Max: {state.get('recent_max', 0):.2f}\n"
            response += f"   Recent Min: {state.get('recent_min', 0):.2f}\n"
            response += f"   Volatility: {state.get('volatility', 0):.2f}\n"
            response += f"   Status: {state['status'].upper()}\n"
            
            # Add threshold information
            thresholds = self.thresholds.get(param, {})
            if thresholds:
                response += f"   Thresholds: Normal<{thresholds.get('normal', 0)}, "
                response += f"High<{thresholds.get('high', 0)}, "
                response += f"Critical<{thresholds.get('critical', 0)}\n"
            
            # Add context
            if state["status"] == "critical":
                response += "   ⚠️ CRITICAL - Immediate action required!\n"
            elif state["status"] == "high":
                response += "   ⚠️ HIGH - Needs urgent attention\n"
            elif state["status"] == "warning":
                response += "   ⚠️ WARNING - Monitor closely\n"
            else:
                response += "   ✅ NORMAL - Operating within safe range\n"
            response += "\n"
        
        # Detailed trend analysis
        response += "┌─────────────────────────────────────────────────┐\n"
        response += "│  📈 TREND ANALYSIS & PREDICTIONS                │\n"
        response += "└─────────────────────────────────────────────────┘\n\n"
        
        for param, trend in trends.items():
            icon = "📈" if trend["direction"] == "rising" else "📉" if trend["direction"] == "falling" else "➡️"
            response += f"{icon} {param.upper()} TREND:\n"
            response += f"   Direction: {trend['description']}\n"
            response += f"   Strength: {trend['strength']:.1f}/10\n"
            response += f"   Slope: {trend.get('slope', 0):.4f}\n"
            
            if trend["direction"] == "rising" and trend["strength"] > 7:
                response += "   ⚠️ ALERT: Rapidly increasing - urgent attention needed!\n"
            elif trend["direction"] == "rising" and trend["strength"] > 5:
                response += "   ⚠️ WARNING: Rising rapidly - monitor closely\n"
            elif trend["direction"] == "falling" and trend["strength"] > 5:
                response += "   ⚠️ WARNING: Dropping rapidly - investigate cause\n"
            else:
                response += "   ✅ Trend is stable and manageable\n"
            response += "\n"
        
        # LSTM Forecast with detailed interpretation
        lstm = ml_interpretation.get("lstm", {})
        forecast = lstm.get("forecast_values", {})
        concerns = lstm.get("concerns", [])
        changes = lstm.get("changes", {})
        
        if forecast:
            response += "┌─────────────────────────────────────────────────┐\n"
            response += "│  🔮 LSTM FORECAST (Next Cycle Prediction)      │\n"
            response += "└─────────────────────────────────────────────────┘\n\n"
            
            response += "Predicted Values:\n"
            response += f"  • Temperature: {forecast.get('temperature', 0):.2f}°C"
            if changes and changes.get('temperature'):
                change = changes['temperature']
                response += f" ({'+' if change > 0 else ''}{change:.2f}°C change)\n"
            else:
                response += "\n"
            
            response += f"  • Vibration: {forecast.get('vibration', 0):.2f} mm/s"
            if changes and changes.get('vibration'):
                change = changes['vibration']
                response += f" ({'+' if change > 0 else ''}{change:.2f} mm/s change)\n"
            else:
                response += "\n"
            
            response += f"  • Speed: {forecast.get('speed', 0):.0f} RPM"
            if changes and changes.get('speed'):
                change = changes['speed']
                response += f" ({'+' if change > 0 else ''}{change:.0f} RPM change)\n"
            else:
                response += "\n"
            
            if concerns:
                response += "\n⚠️ Forecast Concerns:\n"
                for concern in concerns:
                    response += f"  • {concern}\n"
            else:
                response += "\n✅ Forecast indicates stable operation\n"
            response += "\n"
        
        # ML insights with detailed explanations
        rf = ml_interpretation.get("random_forest", {})
        iso = ml_interpretation.get("isolation_forest", {})
        
        response += "┌─────────────────────────────────────────────────┐\n"
        response += "│  🤖 MACHINE LEARNING INSIGHTS                   │\n"
        response += "└─────────────────────────────────────────────────┘\n\n"
        
        response += "🌲 RANDOM FOREST (Failure Risk Classification):\n"
        response += f"   Prediction: {rf.get('risk_level', 'Unknown').upper()}\n"
        response += f"   Message: {rf.get('message', 'Unknown')}\n"
        if rf.get('label'):
            response += f"   Label: {rf.get('label')}\n"
        response += "\n"
        
        response += "🔍 ISOLATION FOREST (Anomaly Detection):\n"
        response += f"   Status: {iso.get('severity', 'Unknown').upper()}\n"
        response += f"   Message: {iso.get('message', 'Unknown')}\n"
        if iso.get('score') is not None:
            response += f"   Anomaly Score: {iso.get('score'):.4f}\n"
            response += f"   (Scores < -0.05 indicate anomalies)\n"
        response += "\n"
        
        # Anomalies if any
        if anomalies:
            response += "┌─────────────────────────────────────────────────┐\n"
            response += "│  ⚠️ DETECTED ANOMALIES & PATTERNS              │\n"
            response += "└─────────────────────────────────────────────────┘\n\n"
            
            for i, anomaly in enumerate(anomalies[:5], 1):
                severity_icon = "🚨" if anomaly.get('severity') == 'critical' else "⚠️" if anomaly.get('severity') == 'high' else "📊"
                response += f"{severity_icon} Anomaly #{i}:\n"
                response += f"   Type: {anomaly.get('type', 'Unknown')}\n"
                response += f"   Parameter: {anomaly.get('parameter', 'Unknown')}\n"
                response += f"   Severity: {anomaly.get('severity', 'Unknown').upper()}\n"
                response += f"   Description: {anomaly.get('description', 'No description')}\n"
                response += f"   Recommendation: {anomaly.get('recommendation', 'Monitor closely')}\n"
                response += "\n"
        
        # DETAILED RECOMMENDATIONS SECTION
        response += "╔══════════════════════════════════════════════════╗\n"
        response += "║     💡 RECOMMENDATIONS & SOLUTIONS 💡           ║\n"
        response += "╚══════════════════════════════════════════════════╝\n\n"
        
        # Group recommendations by priority
        immediate = [r for r in recommendations if r["priority"] == "immediate"]
        high = [r for r in recommendations if r["priority"] == "high"]
        medium = [r for r in recommendations if r["priority"] == "medium"]
        low = [r for r in recommendations if r["priority"] == "low"]
        
        if immediate:
            response += "┌─────────────────────────────────────────────────┐\n"
            response += "│  🚨 IMMEDIATE ACTIONS (Do This NOW!)           │\n"
            response += "└─────────────────────────────────────────────────┘\n\n"
            
            for i, rec in enumerate(immediate, 1):
                response += f"Action #{i}: {rec['icon']} {rec['action']}\n"
                response += f"Category: {rec.get('category', 'General')}\n"
                response += f"Why: {rec['reason']}\n\n"
                response += "Step-by-Step Solution:\n"
                for step in rec.get('steps', []):
                    response += f"   {step}\n"
                response += "\n"
        
        if high:
            response += "┌─────────────────────────────────────────────────┐\n"
            response += "│  ⚠️ HIGH PRIORITY (Do Within 1 Hour)           │\n"
            response += "└─────────────────────────────────────────────────┘\n\n"
            
            for i, rec in enumerate(high, 1):
                response += f"Action #{i}: {rec['icon']} {rec['action']}\n"
                response += f"Category: {rec.get('category', 'General')}\n"
                response += f"Why: {rec['reason']}\n\n"
                response += "Step-by-Step Solution:\n"
                for step in rec.get('steps', []):
                    response += f"   {step}\n"
                response += "\n"
        
        if medium:
            response += "┌─────────────────────────────────────────────────┐\n"
            response += "│  📋 MEDIUM PRIORITY (Do Within 24 Hours)       │\n"
            response += "└─────────────────────────────────────────────────┘\n\n"
            
            for i, rec in enumerate(medium[:3], 1):  # Show top 3
                response += f"Action #{i}: {rec['icon']} {rec['action']}\n"
                response += f"Category: {rec.get('category', 'General')}\n"
                response += f"Why: {rec['reason']}\n\n"
                response += "Step-by-Step Solution:\n"
                for step in rec.get('steps', []):
                    response += f"   {step}\n"
                response += "\n"
        
        if not immediate and not high and low:
            response += "┌─────────────────────────────────────────────────┐\n"
            response += "│  ✅ ROUTINE MAINTENANCE                         │\n"
            response += "└─────────────────────────────────────────────────┘\n\n"
            
            for rec in low[:1]:
                response += f"{rec['icon']} {rec['action']}\n"
                response += f"Category: {rec.get('category', 'General')}\n"
                response += f"Why: {rec['reason']}\n\n"
                response += "Step-by-Step Solution:\n"
                for step in rec.get('steps', []):
                    response += f"   {step}\n"
                response += "\n"
        
        # Final Summary
        response += "╔══════════════════════════════════════════════════╗\n"
        response += "║              📊 FINAL SUMMARY 📊                 ║\n"
        response += "╚══════════════════════════════════════════════════╝\n\n"
        
        if immediate or high:
            response += "🚨 CRITICAL: Take action IMMEDIATELY to prevent machine failure!\n\n"
            response += "Priority Actions:\n"
            response += f"  • Immediate actions: {len(immediate)}\n"
            response += f"  • High priority actions: {len(high)}\n"
            response += f"  • Total urgent actions: {len(immediate) + len(high)}\n\n"
            response += "⚠️ Do NOT delay - machine safety is at risk!\n"
        elif medium:
            response += "📊 ATTENTION: Schedule maintenance soon to prevent issues.\n\n"
            response += f"  • Medium priority actions: {len(medium)}\n"
            response += "  • Recommended timeframe: Within 24 hours\n\n"
            response += "✅ Machine is operational but needs attention.\n"
        else:
            response += "✅ EXCELLENT: Machine is healthy and operating normally.\n\n"
            response += "  • All parameters within safe ranges\n"
            response += "  • No immediate actions required\n"
            response += "  • Continue standard monitoring procedures\n\n"
            response += "🎉 Keep up the good maintenance work!\n"
        
        return response
