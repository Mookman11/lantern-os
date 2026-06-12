"""
Performance benchmarking suite for Dream Journal service
Tracks: response times, memory usage, throughput, and agent metrics
"""

import json
import time
import requests
import subprocess
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import warnings

warnings.filterwarnings('ignore')

API_BASE = "http://localhost:5000"
CONTAINER_NAME = "lantern-dream-journal"

class PerformanceBenchmark:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "service": "lantern-dream-journal",
            "endpoints": {},
            "system_metrics": {},
            "summary": {}
        }
        self.response_times = {}
        self.memory_samples = []
        
    def get_container_memory(self) -> float:
        """Get container memory usage in MB"""
        try:
            result = subprocess.run(
                ["docker", "stats", "--no-stream", CONTAINER_NAME, "--format", "{{.MemUsage}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                mem_str = result.stdout.strip().split("/")[0].replace("MiB", "").replace("B", "").strip()
                return float(mem_str)
        except Exception as e:
            print(f"Warning: Could not get container memory: {e}")
        return 0.0
    
    def benchmark_health_check(self, iterations: int = 100) -> Dict:
        """Benchmark /health endpoint"""
        print("\n[TEST 1/5] /health endpoint (100 requests)")
        times = []
        
        for i in range(iterations):
            start = time.time()
            try:
                resp = requests.get(f"{API_BASE}/health", timeout=5)
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
                if resp.status_code != 200:
                    print(f"  Warning: Non-200 status {resp.status_code}")
            except Exception as e:
                print(f"  Error on iteration {i}: {e}")
        
        stats = self._compute_stats(times)
        self.response_times["health"] = times
        print(f"  Result: {iterations} reqs - avg {stats['mean']:.2f}ms, p95 {stats['p95']:.2f}ms")
        return stats
    
    def benchmark_log_dream(self, iterations: int = 50) -> Dict:
        """Benchmark /dreams/log endpoint"""
        print("\n[TEST 2/5] /dreams/log endpoint (50 requests)")
        times = []
        memory_before = self.get_container_memory()
        
        for i in range(iterations):
            dream_data = {
                "content": f"Test dream iteration {i}: flying through digital landscapes",
                "lucidity": 0.5 + (i % 10) * 0.05,
                "emotions": ["wonder", "curiosity"],
                "tags": ["test", f"iter_{i}"],
                "linked_goals": ["lantern-revenue"]
            }
            
            start = time.time()
            try:
                resp = requests.post(
                    f"{API_BASE}/dreams/log",
                    json=dream_data,
                    timeout=5
                )
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
                
                if resp.status_code != 201:
                    print(f"  Warning: Expected 201, got {resp.status_code}")
            except Exception as e:
                print(f"  Error on iteration {i}: {e}")
        
        memory_after = self.get_container_memory()
        stats = self._compute_stats(times)
        stats["memory_delta_mb"] = memory_after - memory_before
        self.response_times["log_dream"] = times
        
        print(f"  Result: {iterations} reqs - avg {stats['mean']:.2f}ms, p95 {stats['p95']:.2f}ms, +{stats['memory_delta_mb']:.2f}MB")
        return stats
    
    def benchmark_get_recent(self, iterations: int = 100) -> Dict:
        """Benchmark /dreams/recent endpoint"""
        print("\n[TEST 3/5] /dreams/recent endpoint (100 requests)")
        times = []
        
        for i in range(iterations):
            start = time.time()
            try:
                resp = requests.get(
                    f"{API_BASE}/dreams/recent?limit=10",
                    timeout=5
                )
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
                
                if resp.status_code != 200:
                    print(f"  Warning: Non-200 status {resp.status_code}")
                    
                if i % 10 == 0:
                    self.memory_samples.append(self.get_container_memory())
                    
            except Exception as e:
                print(f"  Error on iteration {i}: {e}")
        
        stats = self._compute_stats(times)
        stats["avg_memory_mb"] = statistics.mean(self.memory_samples) if self.memory_samples else 0
        self.response_times["get_recent"] = times
        
        print(f"  Result: {iterations} reqs - avg {stats['mean']:.2f}ms, p95 {stats['p95']:.2f}ms, memory {stats['avg_memory_mb']:.2f}MB")
        return stats
    
    def benchmark_mirror_prompt(self, iterations: int = 50) -> Dict:
        """Benchmark /dreams/mirror-prompt endpoint"""
        print("\n[TEST 4/5] /dreams/mirror-prompt endpoint (50 requests)")
        times = []
        
        for i in range(iterations):
            try:
                recent = requests.get(f"{API_BASE}/dreams/recent?limit=1", timeout=5).json()
                if recent.get("dreams"):
                    dream_id = recent["dreams"][0]["id"]
                else:
                    continue
            except Exception as e:
                print(f"  Error fetching dream: {e}")
                continue
            
            start = time.time()
            try:
                resp = requests.post(
                    f"{API_BASE}/dreams/mirror-prompt",
                    json={"dream_id": dream_id},
                    timeout=5
                )
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
                
                if resp.status_code != 200:
                    print(f"  Warning: Non-200 status {resp.status_code}")
                    
            except Exception as e:
                print(f"  Error on iteration {i}: {e}")
        
        stats = self._compute_stats(times)
        self.response_times["mirror_prompt"] = times
        
        print(f"  Result: {iterations} reqs - avg {stats['mean']:.2f}ms, p95 {stats['p95']:.2f}ms")
        return stats
    
    def benchmark_stats(self, iterations: int = 100) -> Dict:
        """Benchmark /dreams/stats endpoint"""
        print("\n[TEST 5/5] /dreams/stats endpoint (100 requests)")
        times = []
        
        for i in range(iterations):
            start = time.time()
            try:
                resp = requests.get(f"{API_BASE}/dreams/stats", timeout=5)
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
                
                if resp.status_code != 200:
                    print(f"  Warning: Non-200 status {resp.status_code}")
                    
            except Exception as e:
                print(f"  Error on iteration {i}: {e}")
        
        stats = self._compute_stats(times)
        self.response_times["stats"] = times
        
        print(f"  Result: {iterations} reqs - avg {stats['mean']:.2f}ms, p95 {stats['p95']:.2f}ms")
        return stats
    
    def _compute_stats(self, times: List[float]) -> Dict:
        """Compute statistics from response times"""
        if not times:
            return {"mean": 0, "min": 0, "max": 0, "p95": 0, "p99": 0, "count": 0}
        
        sorted_times = sorted(times)
        return {
            "count": len(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "p95": sorted_times[int(len(times) * 0.95)],
            "p99": sorted_times[int(len(times) * 0.99)],
            "stdev": statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def run_all_benchmarks(self):
        """Run complete benchmark suite"""
        print("=" * 70)
        print("[BENCHMARK] Dream Journal Performance Test Suite")
        print("=" * 70)
        
        print("\n[METRICS] Container Status:")
        memory = self.get_container_memory()
        self.results["system_metrics"]["container_memory_mb"] = memory
        print(f"  Memory: {memory:.2f}MB")
        
        self.results["endpoints"]["health"] = self.benchmark_health_check(100)
        self.results["endpoints"]["log_dream"] = self.benchmark_log_dream(50)
        self.results["endpoints"]["get_recent"] = self.benchmark_get_recent(100)
        self.results["endpoints"]["mirror_prompt"] = self.benchmark_mirror_prompt(50)
        self.results["endpoints"]["stats"] = self.benchmark_stats(100)
        
        self._compute_summary()
        self._print_summary()
        
        return self.results
    
    def _compute_summary(self):
        """Compute overall summary statistics"""
        all_times = []
        
        for endpoint, metrics in self.results["endpoints"].items():
            times = self.response_times.get(endpoint, [])
            all_times.extend(times)
        
        if all_times:
            summary_stats = self._compute_stats(all_times)
            self.results["summary"] = {
                "total_requests": len(all_times),
                "overall_avg_response_time_ms": summary_stats["mean"],
                "overall_p95_ms": summary_stats["p95"],
                "overall_p99_ms": summary_stats["p99"],
                "final_memory_usage_mb": self.get_container_memory()
            }
    
    def _print_summary(self):
        """Print human-readable summary"""
        print("\n" + "=" * 70)
        print("[RESULTS] Performance Summary")
        print("=" * 70)
        
        summary = self.results["summary"]
        print(f"\nTotal Requests: {summary['total_requests']}")
        print(f"Overall Response Times:")
        print(f"  Average:  {summary['overall_avg_response_time_ms']:.2f}ms")
        print(f"  P95:      {summary['overall_p95_ms']:.2f}ms")
        print(f"  P99:      {summary['overall_p99_ms']:.2f}ms")
        print(f"\nMemory Usage:")
        print(f"  Final:    {summary['final_memory_usage_mb']:.2f}MB")
        
        print("\nEndpoint Breakdown:")
        for endpoint, metrics in self.results["endpoints"].items():
            print(f"\n  {endpoint.upper()}:")
            print(f"    Avg: {metrics.get('mean', 0):.2f}ms")
            print(f"    P95: {metrics.get('p95', 0):.2f}ms")
            print(f"    Count: {metrics.get('count', 0)}")
        
        print("\n" + "=" * 70)
    
    def save_report(self, filename: str = "performance_report.json"):
        """Save detailed report to file"""
        report_path = Path(filename)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n[SAVED] Report: {report_path}")
        return report_path

if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    results = benchmark.run_all_benchmarks()
    benchmark.save_report("lantern-os/tests/perf_results_dream_journal.json")
