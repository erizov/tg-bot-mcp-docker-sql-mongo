#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E Test Runner and Grafana Report Generator
Runs comprehensive E2E tests and generates Grafana-compatible reports.
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("e2e_runner")


class E2ERunner:
    """E2E Test Runner with Grafana Integration."""
    
    def __init__(self):
        self.test_dir = os.path.dirname(__file__)
        self.reports_dir = os.path.join(self.test_dir, "reports")
        self.ensure_reports_dir()
    
    def ensure_reports_dir(self):
        """Ensure reports directory exists."""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def run_e2e_test(self) -> str:
        """Run the E2E integration test."""
        logger.info("🚀 Running E2E Integration Test...")
        
        # Run the E2E test
        test_script = os.path.join(self.test_dir, "test_e2e_integration.py")
        result = subprocess.run([sys.executable, test_script], 
                              capture_output=True, text=True, cwd=self.test_dir)
        
        if result.returncode != 0:
            logger.error(f"E2E test failed: {result.stderr}")
            return None
        
        logger.info("✅ E2E test completed successfully")
        return result.stdout
    
    def generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML report for Grafana integration."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E2E Test Report - {timestamp}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #007bff;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #007bff;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .chart-container h3 {{
            margin-top: 0;
            color: #333;
        }}
        .performance-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .performance-table th,
        .performance-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .performance-table th {{
            background-color: #007bff;
            color: white;
        }}
        .performance-table tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .status-success {{
            color: #28a745;
            font-weight: bold;
        }}
        .status-failed {{
            color: #dc3545;
            font-weight: bold;
        }}
        .backend-section {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .backend-section h3 {{
            margin-top: 0;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 E2E Integration Test Report</h1>
            <p>Generated on: {timestamp}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Backends</h3>
                <div class="value">{report_data['summary']['total_backends']}</div>
            </div>
            <div class="summary-card">
                <h3>Successful</h3>
                <div class="value status-success">{report_data['summary']['successful_backends']}</div>
            </div>
            <div class="summary-card">
                <h3>Failed</h3>
                <div class="value status-failed">{report_data['summary']['failed_backends']}</div>
            </div>
            <div class="summary-card">
                <h3>Total Time</h3>
                <div class="value">{report_data['test_info']['total_execution_time']:.2f}s</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>📊 Performance Comparison - Insert Rate</h3>
            <canvas id="insertRateChart" width="400" height="200"></canvas>
        </div>
        
        <div class="chart-container">
            <h3>📊 Performance Comparison - Lookup Rate</h3>
            <canvas id="lookupRateChart" width="400" height="200"></canvas>
        </div>
        
        <div class="chart-container">
            <h3>📊 Performance Comparison - Search Rate</h3>
            <canvas id="searchRateChart" width="400" height="200"></canvas>
        </div>
        
        <h2>📋 Performance Summary</h2>
        <table class="performance-table">
            <thead>
                <tr>
                    <th>Backend</th>
                    <th>Insert Rate (notes/sec)</th>
                    <th>Lookup Rate (ops/sec)</th>
                    <th>Search Rate (ops/sec)</th>
                    <th>Total Time (s)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add performance data rows
        for backend_name, perf_data in report_data['performance_comparison'].items():
            backend_result = report_data['detailed_results'].get(backend_name, {})
            status = backend_result.get('status', 'unknown')
            status_class = 'status-success' if status == 'success' else 'status-failed'
            
            html_content += f"""
                <tr>
                    <td><strong>{backend_name.upper()}</strong></td>
                    <td>{perf_data['insert_rate']:.2f}</td>
                    <td>{perf_data['lookup_rate']:.2f}</td>
                    <td>{perf_data['search_rate']:.2f}</td>
                    <td>{perf_data['total_execution_time']:.2f}</td>
                    <td class="{status_class}">{status.upper()}</td>
                </tr>
"""
        
        html_content += """
            </tbody>
        </table>
        
        <h2>🔍 Detailed Results</h2>
"""
        
        # Add detailed results for each backend
        for backend_name, result in report_data['detailed_results'].items():
            status_class = 'status-success' if result.get('status') == 'success' else 'status-failed'
            html_content += f"""
        <div class="backend-section">
            <h3>{backend_name.upper()} - <span class="{status_class}">{result.get('status', 'unknown').upper()}</span></h3>
            <p><strong>Execution Time:</strong> {result.get('execution_time', 0):.2f}s</p>
            <p><strong>Timestamp:</strong> {result.get('timestamp', 'N/A')}</p>
"""
            
            if result.get('status') == 'success' and 'tests' in result:
                html_content += "<h4>Test Results:</h4><ul>"
                for test_name, test_result in result['tests'].items():
                    test_status = test_result.get('status', 'unknown')
                    test_status_class = 'status-success' if test_status == 'success' else 'status-failed'
                    html_content += f"<li><span class='{test_status_class}'>{test_name.upper()}</span>: {test_status}</li>"
                html_content += "</ul>"
            elif result.get('status') == 'failed':
                html_content += f"<p><strong>Error:</strong> {result.get('error', 'Unknown error')}</p>"
            
            html_content += "</div>"
        
        # Add JavaScript for charts
        html_content += f"""
        <script>
            // Performance data
            const performanceData = {json.dumps(report_data['performance_comparison'])};
            
            // Chart colors
            const colors = ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1', '#20c997'];
            
            // Insert Rate Chart
            const insertCtx = document.getElementById('insertRateChart').getContext('2d');
            new Chart(insertCtx, {{
                type: 'bar',
                data: {{
                    labels: Object.keys(performanceData),
                    datasets: [{{
                        label: 'Insert Rate (notes/sec)',
                        data: Object.values(performanceData).map(d => d.insert_rate),
                        backgroundColor: colors.slice(0, Object.keys(performanceData).length),
                        borderColor: colors.slice(0, Object.keys(performanceData).length),
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Notes per Second'
                            }}
                        }}
                    }}
                }}
            }});
            
            // Lookup Rate Chart
            const lookupCtx = document.getElementById('lookupRateChart').getContext('2d');
            new Chart(lookupCtx, {{
                type: 'bar',
                data: {{
                    labels: Object.keys(performanceData),
                    datasets: [{{
                        label: 'Lookup Rate (ops/sec)',
                        data: Object.values(performanceData).map(d => d.lookup_rate),
                        backgroundColor: colors.slice(0, Object.keys(performanceData).length),
                        borderColor: colors.slice(0, Object.keys(performanceData).length),
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Operations per Second'
                            }}
                        }}
                    }}
                }}
            }});
            
            // Search Rate Chart
            const searchCtx = document.getElementById('searchRateChart').getContext('2d');
            new Chart(searchCtx, {{
                type: 'bar',
                data: {{
                    labels: Object.keys(performanceData),
                    datasets: [{{
                        label: 'Search Rate (ops/sec)',
                        data: Object.values(performanceData).map(d => d.search_rate),
                        backgroundColor: colors.slice(0, Object.keys(performanceData).length),
                        borderColor: colors.slice(0, Object.keys(performanceData).length),
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Operations per Second'
                            }}
                        }}
                    }}
                }}
            }});
        </script>
    </div>
</body>
</html>
"""
        
        # Save HTML report
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f"e2e_report_{timestamp_str}.html"
        html_filepath = os.path.join(self.reports_dir, html_filename)
        
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"📊 HTML report generated: {html_filepath}")
        return html_filepath
    
    def generate_prometheus_metrics(self, report_data: Dict[str, Any]) -> str:
        """Generate Prometheus-compatible metrics."""
        timestamp = int(datetime.now().timestamp())
        
        metrics_lines = []
        metrics_lines.append("# HELP notes_bot_e2e_test_duration_seconds Total E2E test execution time")
        metrics_lines.append("# TYPE notes_bot_e2e_test_duration_seconds gauge")
        metrics_lines.append(f"notes_bot_e2e_test_duration_seconds {report_data['test_info']['total_execution_time']} {timestamp}")
        metrics_lines.append("")
        
        metrics_lines.append("# HELP notes_bot_e2e_test_backends_total Total number of backends tested")
        metrics_lines.append("# TYPE notes_bot_e2e_test_backends_total gauge")
        metrics_lines.append(f"notes_bot_e2e_test_backends_total {report_data['summary']['total_backends']} {timestamp}")
        metrics_lines.append("")
        
        metrics_lines.append("# HELP notes_bot_e2e_test_successful_backends_total Number of successful backends")
        metrics_lines.append("# TYPE notes_bot_e2e_test_successful_backends_total gauge")
        metrics_lines.append(f"notes_bot_e2e_test_successful_backends_total {report_data['summary']['successful_backends']} {timestamp}")
        metrics_lines.append("")
        
        # Performance metrics for each backend
        for backend_name, perf_data in report_data['performance_comparison'].items():
            metrics_lines.append(f"# HELP notes_bot_insert_rate_per_second Insert rate for {backend_name}")
            metrics_lines.append(f"# TYPE notes_bot_insert_rate_per_second gauge")
            metrics_lines.append(f"notes_bot_insert_rate_per_second{{backend=\"{backend_name}\"}} {perf_data['insert_rate']} {timestamp}")
            metrics_lines.append("")
            
            metrics_lines.append(f"# HELP notes_bot_lookup_rate_per_second Lookup rate for {backend_name}")
            metrics_lines.append(f"# TYPE notes_bot_lookup_rate_per_second gauge")
            metrics_lines.append(f"notes_bot_lookup_rate_per_second{{backend=\"{backend_name}\"}} {perf_data['lookup_rate']} {timestamp}")
            metrics_lines.append("")
            
            metrics_lines.append(f"# HELP notes_bot_search_rate_per_second Search rate for {backend_name}")
            metrics_lines.append(f"# TYPE notes_bot_search_rate_per_second gauge")
            metrics_lines.append(f"notes_bot_search_rate_per_second{{backend=\"{backend_name}\"}} {perf_data['search_rate']} {timestamp}")
            metrics_lines.append("")
            
            metrics_lines.append(f"# HELP notes_bot_backend_execution_time_seconds Execution time for {backend_name}")
            metrics_lines.append(f"# TYPE notes_bot_backend_execution_time_seconds gauge")
            metrics_lines.append(f"notes_bot_backend_execution_time_seconds{{backend=\"{backend_name}\"}} {perf_data['total_execution_time']} {timestamp}")
            metrics_lines.append("")
        
        # Save Prometheus metrics
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        prometheus_filename = f"prometheus_metrics_{timestamp_str}.txt"
        prometheus_filepath = os.path.join(self.reports_dir, prometheus_filename)
        
        with open(prometheus_filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(metrics_lines))
        
        logger.info(f"📈 Prometheus metrics generated: {prometheus_filepath}")
        return prometheus_filepath
    
    def run_full_e2e_suite(self):
        """Run the complete E2E test suite with all reports."""
        logger.info("🚀 Starting Full E2E Test Suite")
        
        # Run E2E test
        test_output = self.run_e2e_test()
        if not test_output:
            logger.error("❌ E2E test failed")
            return
        
        # Find the generated report file
        report_files = [f for f in os.listdir(self.test_dir) if f.startswith('e2e_test_report_') and f.endswith('.json')]
        if not report_files:
            logger.error("❌ No report file found")
            return
        
        # Load the latest report
        latest_report = max(report_files, key=lambda x: os.path.getctime(os.path.join(self.test_dir, x)))
        report_path = os.path.join(self.test_dir, latest_report)
        
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        logger.info(f"📊 Loaded report: {report_path}")
        
        # Generate all report formats
        html_report = self.generate_html_report(report_data)
        prometheus_metrics = self.generate_prometheus_metrics(report_data)
        
        # Summary
        logger.info("✅ Full E2E Test Suite Complete!")
        logger.info(f"📁 Reports generated:")
        logger.info(f"  - JSON Report: {report_path}")
        logger.info(f"  - HTML Report: {html_report}")
        logger.info(f"  - Prometheus Metrics: {prometheus_metrics}")
        
        return {
            'json_report': report_path,
            'html_report': html_report,
            'prometheus_metrics': prometheus_metrics
        }


def main():
    """Main function."""
    runner = E2ERunner()
    results = runner.run_full_e2e_suite()
    
    if results:
        print("\n" + "="*60)
        print("🎯 E2E Test Suite Complete!")
        print("="*60)
        print(f"📊 Reports available:")
        print(f"  - Detailed JSON: {results['json_report']}")
        print(f"  - HTML Dashboard: {results['html_report']}")
        print(f"  - Prometheus Metrics: {results['prometheus_metrics']}")
        print("="*60)


if __name__ == "__main__":
    main()
