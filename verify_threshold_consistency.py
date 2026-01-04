#!/usr/bin/env python3
"""
Threshold Consistency Verification Script
=========================================

This script verifies that all threshold values are consistent across the system
and generates a comprehensive report of threshold usage.
"""

import os
import json
import re
from pathlib import Path

def extract_thresholds_from_file(file_path, file_type):
    """Extract threshold values from a file"""
    thresholds = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return thresholds
    
    # Temperature thresholds
    temp_patterns = [
        r'temp.*?>\s*(\d+)',
        r'temperature.*?>\s*(\d+)',
        r'TEMP.*?>\s*(\d+)',
        r'(\d+).*?°C',
        r'temp.*?threshold.*?(\d+)',
        r'critical.*?temp.*?(\d+)',
        r'warning.*?temp.*?(\d+)'
    ]
    
    # Vibration thresholds
    vib_patterns = [
        r'vib.*?>\s*(\d+\.?\d*)',
        r'vibration.*?>\s*(\d+\.?\d*)',
        r'VIB.*?>\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*mm/s',
        r'vib.*?threshold.*?(\d+\.?\d*)',
        r'critical.*?vib.*?(\d+\.?\d*)',
        r'warning.*?vib.*?(\d+\.?\d*)'
    ]
    
    # Speed thresholds
    speed_patterns = [
        r'speed.*?>\s*(\d+)',
        r'rpm.*?>\s*(\d+)',
        r'RPM.*?>\s*(\d+)',
        r'(\d+)\s*RPM',
        r'speed.*?threshold.*?(\d+)',
        r'critical.*?speed.*?(\d+)',
        r'warning.*?speed.*?(\d+)'
    ]
    
    # Extract temperature thresholds
    temp_values = []
    for pattern in temp_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        temp_values.extend([float(m) for m in matches if m.isdigit() or '.' in m])
    
    # Extract vibration thresholds
    vib_values = []
    for pattern in vib_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        vib_values.extend([float(m) for m in matches if m.replace('.', '').isdigit()])
    
    # Extract speed thresholds
    speed_values = []
    for pattern in speed_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        speed_values.extend([float(m) for m in matches if m.isdigit()])
    
    # Filter reasonable values
    temp_values = [v for v in temp_values if 50 <= v <= 200]  # Reasonable temp range
    vib_values = [v for v in vib_values if 0.1 <= v <= 50]    # Reasonable vibration range
    speed_values = [v for v in speed_values if 100 <= v <= 5000]  # Reasonable speed range
    
    if temp_values:
        thresholds['temperature'] = sorted(set(temp_values))
    if vib_values:
        thresholds['vibration'] = sorted(set(vib_values))
    if speed_values:
        thresholds['speed'] = sorted(set(speed_values))
    
    return thresholds

def scan_directory(directory):
    """Scan directory for files and extract thresholds"""
    results = {}
    
    # File extensions to scan
    extensions = ['.py', '.js', '.jsx', '.md', '.json', '.txt']
    
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = ['node_modules', '__pycache__', '.git', 'dist', 'build']
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = Path(root) / file
                relative_path = file_path.relative_to(directory)
                
                # Determine file type
                if file.endswith('.py'):
                    file_type = 'Python'
                elif file.endswith(('.js', '.jsx')):
                    file_type = 'JavaScript'
                elif file.endswith('.md'):
                    file_type = 'Markdown'
                elif file.endswith('.json'):
                    file_type = 'JSON'
                else:
                    file_type = 'Text'
                
                thresholds = extract_thresholds_from_file(file_path, file_type)
                if thresholds:
                    results[str(relative_path)] = {
                        'type': file_type,
                        'thresholds': thresholds
                    }
    
    return results

def analyze_consistency(all_thresholds):
    """Analyze threshold consistency across files"""
    # Collect all unique threshold values by parameter
    temp_thresholds = set()
    vib_thresholds = set()
    speed_thresholds = set()
    
    for file_path, data in all_thresholds.items():
        thresholds = data['thresholds']
        if 'temperature' in thresholds:
            temp_thresholds.update(thresholds['temperature'])
        if 'vibration' in thresholds:
            vib_thresholds.update(thresholds['vibration'])
        if 'speed' in thresholds:
            speed_thresholds.update(thresholds['speed'])
    
    # Define expected standard thresholds
    standard_thresholds = {
        'temperature': {
            'warning': 75.0,
            'critical': 85.0,
            'emergency': 95.0
        },
        'vibration': {
            'warning': 5.0,
            'critical': 7.0,
            'emergency': 10.0
        },
        'speed': {
            'warning': 1200.0,
            'critical': 1350.0,
            'emergency': 1500.0
        }
    }
    
    # Check consistency
    consistency_report = {
        'temperature': {
            'found_values': sorted(temp_thresholds),
            'standard_values': list(standard_thresholds['temperature'].values()),
            'consistent': True,
            'issues': []
        },
        'vibration': {
            'found_values': sorted(vib_thresholds),
            'standard_values': list(standard_thresholds['vibration'].values()),
            'consistent': True,
            'issues': []
        },
        'speed': {
            'found_values': sorted(speed_thresholds),
            'standard_values': list(standard_thresholds['speed'].values()),
            'consistent': True,
            'issues': []
        }
    }
    
    # Check each parameter
    for param in ['temperature', 'vibration', 'speed']:
        found = set(consistency_report[param]['found_values'])
        standard = set(consistency_report[param]['standard_values'])
        
        # Check for missing standard values
        missing = standard - found
        if missing:
            consistency_report[param]['consistent'] = False
            consistency_report[param]['issues'].append(f"Missing standard values: {sorted(missing)}")
        
        # Check for extra values
        extra = found - standard
        if extra:
            consistency_report[param]['consistent'] = False
            consistency_report[param]['issues'].append(f"Non-standard values found: {sorted(extra)}")
    
    return consistency_report, standard_thresholds

def generate_report(all_thresholds, consistency_report, standard_thresholds):
    """Generate comprehensive threshold report"""
    report = []
    
    report.append("# THRESHOLD CONSISTENCY VERIFICATION REPORT")
    report.append("=" * 50)
    report.append("")
    
    # Summary
    total_files = len(all_thresholds)
    files_with_temp = sum(1 for data in all_thresholds.values() if 'temperature' in data['thresholds'])
    files_with_vib = sum(1 for data in all_thresholds.values() if 'vibration' in data['thresholds'])
    files_with_speed = sum(1 for data in all_thresholds.values() if 'speed' in data['thresholds'])
    
    report.append("## SUMMARY")
    report.append(f"- Total files scanned: {total_files}")
    report.append(f"- Files with temperature thresholds: {files_with_temp}")
    report.append(f"- Files with vibration thresholds: {files_with_vib}")
    report.append(f"- Files with speed thresholds: {files_with_speed}")
    report.append("")
    
    # Standard thresholds
    report.append("## STANDARD THRESHOLDS")
    report.append("These are the expected threshold values across the system:")
    report.append("")
    
    for param, thresholds in standard_thresholds.items():
        report.append(f"### {param.title()}")
        for level, value in thresholds.items():
            unit = "°C" if param == "temperature" else "mm/s" if param == "vibration" else "RPM"
            report.append(f"- {level.title()}: {value} {unit}")
        report.append("")
    
    # Consistency analysis
    report.append("## CONSISTENCY ANALYSIS")
    report.append("")
    
    overall_consistent = True
    for param, data in consistency_report.items():
        status = "✅ CONSISTENT" if data['consistent'] else "❌ INCONSISTENT"
        report.append(f"### {param.title()}: {status}")
        
        if not data['consistent']:
            overall_consistent = False
            report.append("**Issues found:**")
            for issue in data['issues']:
                report.append(f"- {issue}")
        
        report.append(f"**Found values:** {data['found_values']}")
        report.append(f"**Standard values:** {data['standard_values']}")
        report.append("")
    
    # Overall status
    overall_status = "✅ SYSTEM CONSISTENT" if overall_consistent else "❌ INCONSISTENCIES FOUND"
    report.append(f"## OVERALL STATUS: {overall_status}")
    report.append("")
    
    # Detailed file analysis
    report.append("## DETAILED FILE ANALYSIS")
    report.append("")
    
    for file_path, data in sorted(all_thresholds.items()):
        report.append(f"### {file_path} ({data['type']})")
        
        for param, values in data['thresholds'].items():
            unit = "°C" if param == "temperature" else "mm/s" if param == "vibration" else "RPM"
            report.append(f"- {param.title()}: {values} {unit}")
        
        report.append("")
    
    # Recommendations
    report.append("## RECOMMENDATIONS")
    report.append("")
    
    if overall_consistent:
        report.append("✅ All threshold values are consistent across the system.")
        report.append("- Continue monitoring for any future changes")
        report.append("- Run this verification after any threshold updates")
    else:
        report.append("❌ Threshold inconsistencies detected. Recommended actions:")
        report.append("- Update all files to use standard threshold values")
        report.append("- Create a centralized threshold configuration file")
        report.append("- Implement automated threshold consistency checks")
        report.append("- Review and standardize all threshold-related code")
    
    report.append("")
    report.append("## NEXT STEPS")
    report.append("1. Review all inconsistent files identified above")
    report.append("2. Update threshold values to match standards")
    report.append("3. Test system functionality after changes")
    report.append("4. Re-run this verification script")
    report.append("5. Consider implementing centralized threshold management")
    
    return "\n".join(report)

def main():
    """Main verification function"""
    print("🔍 THRESHOLD CONSISTENCY VERIFICATION")
    print("=" * 40)
    print()
    
    # Scan current directory
    current_dir = Path(".")
    print(f"📁 Scanning directory: {current_dir.absolute()}")
    
    all_thresholds = scan_directory(current_dir)
    
    if not all_thresholds:
        print("❌ No threshold values found in any files")
        return
    
    print(f"✅ Found threshold values in {len(all_thresholds)} files")
    
    # Analyze consistency
    print("🔍 Analyzing threshold consistency...")
    consistency_report, standard_thresholds = analyze_consistency(all_thresholds)
    
    # Generate report
    print("📝 Generating report...")
    report_content = generate_report(all_thresholds, consistency_report, standard_thresholds)
    
    # Save report
    report_file = "THRESHOLD_CONSISTENCY_SUMMARY.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ Report saved to: {report_file}")
    
    # Print summary
    print("\n📊 SUMMARY:")
    overall_consistent = all(data['consistent'] for data in consistency_report.values())
    
    if overall_consistent:
        print("✅ All thresholds are consistent!")
    else:
        print("❌ Inconsistencies found:")
        for param, data in consistency_report.items():
            if not data['consistent']:
                print(f"   - {param.title()}: {len(data['issues'])} issue(s)")
    
    print(f"\n📄 Full report available in: {report_file}")

if __name__ == "__main__":
    main()