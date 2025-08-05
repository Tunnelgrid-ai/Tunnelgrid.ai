#!/usr/bin/env python3
"""
Performance Testing Script for AI Analysis

This script tests different performance configurations to find the optimal
settings for your OpenAI API rate limits and system capabilities.
"""

import asyncio
import time
import httpx
import uuid
from typing import Dict, List

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
ANALYSIS_API_BASE = f"{BASE_URL}/api/analysis"

class PerformanceTester:
    """Test different performance configurations"""
    
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.results = []
    
    async def close(self):
        await self.client.aclose()
    
    async def test_batch_size(self, batch_size: int, delay: float, queries_count: int = 30):
        """Test a specific batch size configuration"""
        
        print(f"\n🧪 Testing batch_size={batch_size}, delay={delay}s")
        
        # Create a test audit (you'll need to replace this with a real audit ID)
        test_audit_id = "your-test-audit-id-here"
        
        if test_audit_id == "your-test-audit-id-here":
            print("⚠️  Please set a real audit ID to test performance")
            return None
        
        start_time = time.time()
        
        try:
            # Start analysis
            response = await self.client.post(
                f"{ANALYSIS_API_BASE}/start",
                json={"audit_id": test_audit_id}
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to start analysis: {response.status_code}")
                return None
            
            data = response.json()
            job_id = data.get('job_id')
            
            if not job_id:
                print("❌ No job ID returned")
                return None
            
            print(f"✅ Analysis started with job ID: {job_id}")
            
            # Monitor progress
            completed = 0
            failed = 0
            last_progress = 0
            
            while True:
                await asyncio.sleep(2)  # Check every 2 seconds
                
                status_response = await self.client.get(f"{ANALYSIS_API_BASE}/status/{job_id}")
                
                if status_response.status_code != 200:
                    print(f"❌ Failed to get status: {status_response.status_code}")
                    break
                
                status_data = status_response.json()
                current_progress = status_data.get('progress_percentage', 0)
                completed = status_data.get('completed_queries', 0)
                failed = status_data.get('failed_queries', 0)
                status = status_data.get('status')
                
                if current_progress > last_progress:
                    print(f"📊 Progress: {current_progress:.1f}% ({completed}/{queries_count})")
                    last_progress = current_progress
                
                if status in ['completed', 'failed', 'partial_failure']:
                    break
            
            end_time = time.time()
            total_time = end_time - start_time
            
            result = {
                'batch_size': batch_size,
                'delay': delay,
                'total_time': total_time,
                'completed': completed,
                'failed': failed,
                'queries_per_minute': (completed / total_time) * 60 if total_time > 0 else 0,
                'success_rate': completed / (completed + failed) if (completed + failed) > 0 else 0
            }
            
            print(f"✅ Completed in {total_time:.1f}s")
            print(f"   Queries/min: {result['queries_per_minute']:.1f}")
            print(f"   Success rate: {result['success_rate']:.1%}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return None
    
    async def run_performance_tests(self):
        """Run comprehensive performance tests"""
        
        print("🚀 Performance Testing for AI Analysis")
        print("=" * 50)
        
        # Test configurations
        test_configs = [
            {'batch_size': 5, 'delay': 1.0},
            {'batch_size': 10, 'delay': 0.5},
            {'batch_size': 15, 'delay': 0.3},
            {'batch_size': 20, 'delay': 0.2},
            {'batch_size': 25, 'delay': 0.1},
        ]
        
        for config in test_configs:
            result = await self.test_batch_size(
                batch_size=config['batch_size'],
                delay=config['delay']
            )
            
            if result:
                self.results.append(result)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print performance test summary"""
        
        if not self.results:
            print("\n❌ No test results available")
            return
        
        print("\n" + "=" * 50)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("=" * 50)
        
        # Sort by queries per minute
        sorted_results = sorted(self.results, key=lambda x: x['queries_per_minute'], reverse=True)
        
        print(f"{'Batch Size':<12} {'Delay':<8} {'Time (s)':<10} {'Q/Min':<8} {'Success':<8}")
        print("-" * 50)
        
        for result in sorted_results:
            print(f"{result['batch_size']:<12} {result['delay']:<8.1f} "
                  f"{result['total_time']:<10.1f} {result['queries_per_minute']:<8.1f} "
                  f"{result['success_rate']:<8.1%}")
        
        # Recommendations
        best_result = sorted_results[0]
        print(f"\n🏆 Best Performance:")
        print(f"   Batch Size: {best_result['batch_size']}")
        print(f"   Delay: {best_result['delay']}s")
        print(f"   Queries/Min: {best_result['queries_per_minute']:.1f}")
        print(f"   Success Rate: {best_result['success_rate']:.1%}")
        
        print(f"\n💡 Recommended Environment Variables:")
        print(f"   export ANALYSIS_BATCH_SIZE={best_result['batch_size']}")
        print(f"   export BATCH_DELAY_SECONDS={best_result['delay']}")

async def main():
    """Run performance tests"""
    
    tester = PerformanceTester()
    
    try:
        await tester.run_performance_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Set a real audit ID in the script before running")
    print("💡 This script will test different batch sizes to find optimal performance")
    print("🔧 Make sure your backend server is running")
    
    # Uncomment to run tests
    # asyncio.run(main()) 