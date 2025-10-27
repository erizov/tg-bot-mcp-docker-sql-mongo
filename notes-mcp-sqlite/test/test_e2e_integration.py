#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-End Integration Test for Notes Bot Database Backends
Tests all database backends sequentially and generates performance reports.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Custom JSON encoder to handle ObjectId and other non-serializable objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Handle datetime objects
        if isinstance(obj, datetime):
            return obj.isoformat()
        # Handle MongoDB ObjectId
        if hasattr(obj, '__str__') and 'ObjectId' in str(type(obj)):
            return str(obj)
        # Handle other objects with __dict__
        if hasattr(obj, '__dict__'):
            return str(obj)
        return super().default(obj)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("e2e_test")

from db.database_selector import get_database
from db.database import NotesDatabase as NotesDatabaseSQLite
from db.database_progress import NotesDatabaseProgress
from db.database_mongo import NotesDatabaseMongo
from db.database_neo4j import NotesDatabaseNeo4j
from db.database_postgresql import NotesDatabasePostgreSQL

# Handle Cassandra import gracefully
try:
    from db.database_cassandra import NotesDatabaseCassandra
    CASSANDRA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Cassandra not available: {e}")
    NotesDatabaseCassandra = None
    CASSANDRA_AVAILABLE = False


class E2EIntegrationTest:
    """End-to-End Integration Test for all database backends."""
    
    def __init__(self):
        self.results = {}
        self.backends = {
            'sqlite': NotesDatabaseSQLite,
            'progress': NotesDatabaseProgress,
            'mongo': NotesDatabaseMongo,
            'neo4j': NotesDatabaseNeo4j,
            'postgresql': NotesDatabasePostgreSQL,
        }
        
        # Add Cassandra only if available
        if CASSANDRA_AVAILABLE:
            self.backends['cassandra'] = NotesDatabaseCassandra
        
        # Test configuration
        self.test_config = {
            'notes_count': 100,
            'search_queries': ['test', 'note', 'important'],
            'reminder_hours': 24,
            'performance_iterations': 3
        }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive E2E test across all backends."""
        logger.info("🚀 Starting E2E Integration Test")
        logger.info(f"Testing {len(self.backends)} database backends")
        logger.info(f"Configuration: {self.test_config}")
        
        overall_start_time = time.time()
        
        for backend_name, backend_class in self.backends.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 Testing {backend_name.upper()} Backend")
            logger.info(f"{'='*60}")
            
            try:
                backend_result = self._test_backend(backend_name, backend_class)
                self.results[backend_name] = backend_result
                logger.info(f"✅ {backend_name.upper()} test completed successfully")
            except Exception as e:
                logger.error(f"❌ {backend_name.upper()} test failed: {e}")
                self.results[backend_name] = {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        overall_end_time = time.time()
        total_time = overall_end_time - overall_start_time
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report(total_time)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 E2E Integration Test Completed")
        logger.info(f"Total execution time: {total_time:.2f} seconds")
        logger.info(f"Successful backends: {len([r for r in self.results.values() if r.get('status') == 'success'])}")
        logger.info(f"Failed backends: {len([r for r in self.results.values() if r.get('status') == 'failed'])}")
        logger.info(f"{'='*60}")
        
        return report
    
    def _test_backend(self, backend_name: str, backend_class) -> Dict[str, Any]:
        """Test a specific backend comprehensively."""
        start_time = time.time()
        
        # Initialize database
        logger.info(f"Initializing {backend_name} database...")
        if backend_name == 'sqlite':
            db = backend_class('test_notes.db')
        else:
            db = backend_class()
        
        # Clear existing data
        self._clear_database(db)
        
        # Run test suite
        test_results = {
            'backend': backend_name,
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # 1. Basic CRUD Operations
        logger.info("Testing basic CRUD operations...")
        crud_result = self._test_crud_operations(db)
        test_results['tests']['crud'] = crud_result
        
        # 2. Search Functionality
        logger.info("Testing search functionality...")
        search_result = self._test_search_functionality(db)
        test_results['tests']['search'] = search_result
        
        # 3. Reminders System
        logger.info("Testing reminders system...")
        reminders_result = self._test_reminders_system(db)
        test_results['tests']['reminders'] = reminders_result
        
        # 4. Performance Benchmark
        logger.info("Testing performance benchmark...")
        performance_result = self._test_performance_benchmark(db)
        test_results['tests']['performance'] = performance_result
        
        # 5. Statistics
        logger.info("Testing statistics...")
        stats_result = self._test_statistics(db)
        test_results['tests']['statistics'] = stats_result
        
        end_time = time.time()
        test_results['execution_time'] = end_time - start_time
        
        logger.info(f"✅ {backend_name.upper()} completed in {test_results['execution_time']:.2f}s")
        
        return test_results
    
    def _clear_database(self, db) -> None:
        """Clear database for clean testing."""
        try:
            # Get all notes and delete them
            notes = db.get_all_notes()
            for note in notes:
                db.delete_note(note['id'])
        except Exception as e:
            logger.warning(f"Could not clear database: {e}")
    
    def _test_crud_operations(self, db) -> Dict[str, Any]:
        """Test Create, Read, Update, Delete operations."""
        result = {'status': 'success', 'operations': {}}
        
        try:
            # Create
            note_id = db.add_note("E2E Test Note", "This is a test note for E2E testing")
            result['operations']['create'] = {'success': True, 'note_id': note_id}
            
            # Read
            note = db.get_note(note_id)
            result['operations']['read'] = {'success': note is not None, 'note': note}
            
            # Update
            update_success = db.update_note(note_id, title="Updated E2E Test Note", content="Updated content")
            result['operations']['update'] = {'success': update_success}
            
            # Delete
            delete_success = db.delete_note(note_id)
            result['operations']['delete'] = {'success': delete_success}
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
    def _test_search_functionality(self, db) -> Dict[str, Any]:
        """Test search functionality."""
        result = {'status': 'success', 'searches': {}}
        
        try:
            # Add test notes
            test_notes = [
                ("Important Meeting", "Meeting with client about project"),
                ("Shopping List", "Buy groceries and household items"),
                ("Important Deadline", "Project deadline approaching"),
                ("Personal Note", "Remember to call mom")
            ]
            
            note_ids = []
            for title, content in test_notes:
                note_id = db.add_note(title, content)
                note_ids.append(note_id)
            
            # Test searches
            for query in self.test_config['search_queries']:
                search_results = db.search_notes(query)
                result['searches'][query] = {
                    'success': True,
                    'results_count': len(search_results),
                    'results': search_results
                }
            
            # Cleanup
            for note_id in note_ids:
                db.delete_note(note_id)
                
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
    def _test_reminders_system(self, db) -> Dict[str, Any]:
        """Test reminders system."""
        result = {'status': 'success', 'reminders': {}}
        
        try:
            # Add notes with reminders
            now = datetime.now()
            future_time = now + timedelta(hours=1)
            
            reminder_note_id = db.add_note(
                "E2E Reminder Test",
                "This is a test reminder",
                due_at=future_time.isoformat()
            )
            
            # Test getting upcoming reminders
            upcoming_reminders = db.get_upcoming_reminders(self.test_config['reminder_hours'])
            result['reminders']['upcoming'] = {
                'success': True,
                'count': len(upcoming_reminders),
                'reminders': upcoming_reminders
            }
            
            # Cleanup
            db.delete_note(reminder_note_id)
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
    def _test_performance_benchmark(self, db) -> Dict[str, Any]:
        """Test performance benchmark."""
        result = {'status': 'success', 'benchmarks': {}}
        
        try:
            notes_count = self.test_config['notes_count']
            
            # Insert performance
            start_time = time.time()
            note_ids = []
            
            for i in range(notes_count):
                note_id = db.add_note(f"Perf Test {i}", f"Performance test note {i}")
                note_ids.append(note_id)
            
            insert_time = time.time() - start_time
            result['benchmarks']['insert'] = {
                'success': True,
                'time': insert_time,
                'notes_count': notes_count,
                'notes_per_second': notes_count / insert_time if insert_time > 0 else 0
            }
            
            # Lookup performance
            start_time = time.time()
            for note_id in note_ids[:10]:  # Test first 10 lookups
                note = db.get_note(note_id)
            
            lookup_time = time.time() - start_time
            result['benchmarks']['lookup'] = {
                'success': True,
                'time': lookup_time,
                'lookups_count': 10,
                'lookups_per_second': 10 / lookup_time if lookup_time > 0 else 0
            }
            
            # Search performance
            start_time = time.time()
            search_results = db.search_notes("Perf")
            search_time = time.time() - start_time
            result['benchmarks']['search'] = {
                'success': True,
                'time': search_time,
                'results_count': len(search_results),
                'searches_per_second': 1 / search_time if search_time > 0 else 0
            }
            
            # Cleanup
            for note_id in note_ids:
                db.delete_note(note_id)
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
    def _test_statistics(self, db) -> Dict[str, Any]:
        """Test statistics functionality."""
        result = {'status': 'success', 'stats': {}}
        
        try:
            # Add test data
            test_notes = [
                ("Stats Test 1", "Test note 1"),
                ("Stats Test 2", "Test note 2", (datetime.now() + timedelta(hours=1)).isoformat()),
                ("Stats Test 3", "Test note 3")
            ]
            
            note_ids = []
            for note_data in test_notes:
                if len(note_data) == 3:
                    note_id = db.add_note(note_data[0], note_data[1], due_at=note_data[2])
                else:
                    note_id = db.add_note(note_data[0], note_data[1])
                note_ids.append(note_id)
            
            # Get statistics
            stats = db.get_stats()
            result['stats'] = {
                'success': True,
                'statistics': stats
            }
            
            # Cleanup
            for note_id in note_ids:
                db.delete_note(note_id)
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
    def _generate_comprehensive_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        report = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'total_execution_time': total_time,
                'test_config': self.test_config,
                'backends_tested': list(self.results.keys())
            },
            'summary': {
                'total_backends': len(self.results),
                'successful_backends': len([r for r in self.results.values() if r.get('status') == 'success']),
                'failed_backends': len([r for r in self.results.values() if r.get('status') == 'failed'])
            },
            'performance_comparison': {},
            'detailed_results': self.results
        }
        
        # Generate performance comparison
        for backend_name, result in self.results.items():
            if result.get('status') == 'success' and 'tests' in result:
                perf_data = result['tests'].get('performance', {})
                if perf_data.get('status') == 'success':
                    benchmarks = perf_data.get('benchmarks', {})
                    report['performance_comparison'][backend_name] = {
                        'insert_time': benchmarks.get('insert', {}).get('time', 0),
                        'lookup_time': benchmarks.get('lookup', {}).get('time', 0),
                        'search_time': benchmarks.get('search', {}).get('time', 0),
                        'insert_rate': benchmarks.get('insert', {}).get('notes_per_second', 0),
                        'lookup_rate': benchmarks.get('lookup', {}).get('lookups_per_second', 0),
                        'search_rate': benchmarks.get('search', {}).get('searches_per_second', 0),
                        'total_execution_time': result.get('execution_time', 0)
                    }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save report to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"e2e_test_report_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)
        
        logger.info(f"📊 Report saved to: {filepath}")
        return filepath
    
    def generate_grafana_metrics(self, report: Dict[str, Any]) -> str:
        """Generate Grafana-compatible metrics."""
        metrics = []
        
        for backend_name, perf_data in report['performance_comparison'].items():
            timestamp = int(datetime.now().timestamp() * 1000)  # Milliseconds
            
            # Insert performance metrics
            metrics.append({
                'metric': f'notes_bot_insert_time_seconds',
                'value': perf_data['insert_time'],
                'tags': {'backend': backend_name},
                'timestamp': timestamp
            })
            
            metrics.append({
                'metric': f'notes_bot_insert_rate_per_second',
                'value': perf_data['insert_rate'],
                'tags': {'backend': backend_name},
                'timestamp': timestamp
            })
            
            # Lookup performance metrics
            metrics.append({
                'metric': f'notes_bot_lookup_time_seconds',
                'value': perf_data['lookup_time'],
                'tags': {'backend': backend_name},
                'timestamp': timestamp
            })
            
            metrics.append({
                'metric': f'notes_bot_lookup_rate_per_second',
                'value': perf_data['lookup_rate'],
                'tags': {'backend': backend_name},
                'timestamp': timestamp
            })
            
            # Search performance metrics
            metrics.append({
                'metric': f'notes_bot_search_time_seconds',
                'value': perf_data['search_time'],
                'tags': {'backend': backend_name},
                'timestamp': timestamp
            })
            
            metrics.append({
                'metric': f'notes_bot_search_rate_per_second',
                'value': perf_data['search_rate'],
                'tags': {'backend': backend_name},
                'timestamp': timestamp
            })
            
            # Total execution time
            metrics.append({
                'metric': f'notes_bot_total_execution_time_seconds',
                'value': perf_data['total_execution_time'],
                'tags': {'backend': backend_name},
                'timestamp': timestamp
            })
        
        # Save metrics to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metrics_filename = f"grafana_metrics_{timestamp}.json"
        metrics_filepath = os.path.join(os.path.dirname(__file__), metrics_filename)
        
        with open(metrics_filepath, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📈 Grafana metrics saved to: {metrics_filepath}")
        return metrics_filepath


def main():
    """Main function to run E2E integration test."""
    print("🚀 Starting End-to-End Integration Test")
    print("=" * 60)
    
    # Create and run test
    e2e_test = E2EIntegrationTest()
    report = e2e_test.run_comprehensive_test()
    
    # Save reports
    report_file = e2e_test.save_report(report)
    metrics_file = e2e_test.generate_grafana_metrics(report)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Backends Tested: {report['summary']['total_backends']}")
    print(f"Successful: {report['summary']['successful_backends']}")
    print(f"Failed: {report['summary']['failed_backends']}")
    print(f"Total Execution Time: {report['test_info']['total_execution_time']:.2f}s")
    print(f"\n📁 Reports Generated:")
    print(f"  - Detailed Report: {report_file}")
    print(f"  - Grafana Metrics: {metrics_file}")
    
    # Performance comparison
    if report['performance_comparison']:
        print(f"\n🏆 PERFORMANCE RANKING (by insert rate):")
        sorted_backends = sorted(
            report['performance_comparison'].items(),
            key=lambda x: x[1]['insert_rate'],
            reverse=True
        )
        
        for i, (backend, perf) in enumerate(sorted_backends, 1):
            print(f"  {i}. {backend.upper()}: {perf['insert_rate']:.2f} notes/sec")
    
    print("=" * 60)
    print("✅ E2E Integration Test Complete!")


if __name__ == "__main__":
    main()
