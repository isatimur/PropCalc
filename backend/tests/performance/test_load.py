"""
Performance and Load Testing for PropCalc Platform
"""

import asyncio
import logging
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import aiohttp
import pytest

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance test metrics"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    requests_per_second: float
    error_rate: float
    test_duration: float

class LoadTester:
    """Load testing utility for PropCalc APIs"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.results = []

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def make_request(self, endpoint: str, method: str = "GET",
                          data: dict | None = None, headers: dict | None = None) -> dict[str, Any]:
        """Make a single request and measure performance"""
        start_time = time.time()

        try:
            url = f"{self.base_url}{endpoint}"

            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    response_data = await response.text()
                    status_code = response.status
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    response_data = await response.text()
                    status_code = response.status
            else:
                raise ValueError(f"Unsupported method: {method}")

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            return {
                "success": 200 <= status_code < 400,
                "status_code": status_code,
                "response_time": response_time,
                "response_data": response_data,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            return {
                "success": False,
                "status_code": 0,
                "response_time": response_time,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def load_test(self, endpoint: str, num_requests: int,
                       concurrent_users: int = 10, method: str = "GET",
                       data: dict | None = None, headers: dict | None = None) -> PerformanceMetrics:
        """Run load test on specific endpoint"""
        logger.info(f"Starting load test: {num_requests} requests, {concurrent_users} concurrent users")

        start_time = time.time()
        results = []

        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(concurrent_users)

        async def make_request_with_semaphore():
            async with semaphore:
                return await self.make_request(endpoint, method, data, headers)

        # Create tasks
        tasks = [make_request_with_semaphore() for _ in range(num_requests)]

        # Execute all requests
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        test_duration = end_time - start_time

        # Calculate metrics
        return self._calculate_metrics(results, test_duration)

    def _calculate_metrics(self, results: list[dict], test_duration: float) -> PerformanceMetrics:
        """Calculate performance metrics from results"""
        total_requests = len(results)
        successful_requests = len([r for r in results if r.get("success", False)])
        failed_requests = total_requests - successful_requests

        response_times = [r.get("response_time", 0) for r in results if r.get("response_time")]

        if response_times:
            average_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)

            # Calculate percentiles
            sorted_times = sorted(response_times)
            p95_index = int(0.95 * len(sorted_times))
            p99_index = int(0.99 * len(sorted_times))

            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
            p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time
        else:
            average_response_time = median_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0

        requests_per_second = total_requests / test_duration if test_duration > 0 else 0
        error_rate = (failed_requests / total_requests) * 100 if total_requests > 0 else 0

        return PerformanceMetrics(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=average_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            test_duration=test_duration
        )

    def print_metrics(self, metrics: PerformanceMetrics, test_name: str):
        """Print performance metrics in a formatted way"""
        print(f"\n{'='*60}")
        print(f"PERFORMANCE TEST RESULTS: {test_name}")
        print(f"{'='*60}")
        print(f"Total Requests: {metrics.total_requests}")
        print(f"Successful Requests: {metrics.successful_requests}")
        print(f"Failed Requests: {metrics.failed_requests}")
        print(f"Error Rate: {metrics.error_rate:.2f}%")
        print(f"Test Duration: {metrics.test_duration:.2f} seconds")
        print(f"Requests per Second: {metrics.requests_per_second:.2f}")
        print("\nResponse Times (ms):")
        print(f"  Average: {metrics.average_response_time:.2f}")
        print(f"  Median: {metrics.median_response_time:.2f}")
        print(f"  95th Percentile: {metrics.p95_response_time:.2f}")
        print(f"  99th Percentile: {metrics.p99_response_time:.2f}")
        print(f"  Min: {metrics.min_response_time:.2f}")
        print(f"  Max: {metrics.max_response_time:.2f}")
        print(f"{'='*60}\n")

class PerformanceTestSuite:
    """Comprehensive performance test suite for PropCalc"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}

    async def run_health_check_test(self) -> PerformanceMetrics:
        """Test health check endpoint performance"""
        async with LoadTester(self.base_url) as tester:
            metrics = await tester.load_test(
                endpoint="/",
                num_requests=1000,
                concurrent_users=50
            )
            tester.print_metrics(metrics, "Health Check Endpoint")
            return metrics

    async def run_dld_api_test(self) -> PerformanceMetrics:
        """Test DLD API endpoints performance"""
        async with LoadTester(self.base_url) as tester:
            metrics = await tester.load_test(
                endpoint="/api/dld/projects",
                num_requests=500,
                concurrent_users=25
            )
            tester.print_metrics(metrics, "DLD Projects API")
            return metrics

    async def run_real_dld_api_test(self) -> PerformanceMetrics:
        """Test Real DLD API endpoints performance"""
        async with LoadTester(self.base_url) as tester:
            metrics = await tester.load_test(
                endpoint="/api/real-dld/health",
                num_requests=300,
                concurrent_users=20
            )
            tester.print_metrics(metrics, "Real DLD Health API")
            return metrics

    async def run_analytics_api_test(self) -> PerformanceMetrics:
        """Test analytics API endpoints performance"""
        async with LoadTester(self.base_url) as tester:
            metrics = await tester.load_test(
                endpoint="/api/comprehensive-dld/analytics/overview",
                num_requests=200,
                concurrent_users=15
            )
            tester.print_metrics(metrics, "Analytics API")
            return metrics

    async def run_pipeline_api_test(self) -> PerformanceMetrics:
        """Test pipeline API endpoints performance"""
        async with LoadTester(self.base_url) as tester:
            metrics = await tester.load_test(
                endpoint="/api/pipeline/status",
                num_requests=400,
                concurrent_users=20
            )
            tester.print_metrics(metrics, "Pipeline Status API")
            return metrics

    async def run_stress_test(self) -> PerformanceMetrics:
        """Run stress test with high load"""
        async with LoadTester(self.base_url) as tester:
            metrics = await tester.load_test(
                endpoint="/",
                num_requests=2000,
                concurrent_users=100
            )
            tester.print_metrics(metrics, "Stress Test (High Load)")
            return metrics

    async def run_endurance_test(self) -> PerformanceMetrics:
        """Run endurance test over longer period"""
        async with LoadTester(self.base_url) as tester:
            metrics = await tester.load_test(
                endpoint="/api/dld/projects",
                num_requests=5000,
                concurrent_users=50
            )
            tester.print_metrics(metrics, "Endurance Test (Long Duration)")
            return metrics

    async def run_concurrent_api_test(self) -> dict[str, PerformanceMetrics]:
        """Test multiple API endpoints concurrently"""
        endpoints = [
            ("/", "Health Check"),
            ("/api/dld/projects", "DLD Projects"),
            ("/api/real-dld/health", "Real DLD Health"),
            ("/api/comprehensive-dld/analytics/overview", "Analytics"),
            ("/api/pipeline/status", "Pipeline Status")
        ]

        async with LoadTester(self.base_url) as tester:
            tasks = []
            for endpoint, name in endpoints:
                task = tester.load_test(
                    endpoint=endpoint,
                    num_requests=200,
                    concurrent_users=10
                )
                tasks.append((name, task))

            results = {}
            for name, task in tasks:
                metrics = await task
                tester.print_metrics(metrics, f"Concurrent {name}")
                results[name] = metrics

            return results

    async def run_all_tests(self) -> dict[str, Any]:
        """Run all performance tests"""
        logger.info("Starting comprehensive performance test suite...")

        test_results = {}

        # Individual endpoint tests
        test_results["health_check"] = await self.run_health_check_test()
        test_results["dld_api"] = await self.run_dld_api_test()
        test_results["real_dld_api"] = await self.run_real_dld_api_test()
        test_results["analytics_api"] = await self.run_analytics_api_test()
        test_results["pipeline_api"] = await self.run_pipeline_api_test()

        # Stress and endurance tests
        test_results["stress_test"] = await self.run_stress_test()
        test_results["endurance_test"] = await self.run_endurance_test()

        # Concurrent API test
        test_results["concurrent_apis"] = await self.run_concurrent_api_test()

        # Generate summary report
        summary = self._generate_summary_report(test_results)
        test_results["summary"] = summary

        return test_results

    def _generate_summary_report(self, test_results: dict[str, Any]) -> dict[str, Any]:
        """Generate summary report of all test results"""
        summary = {
            "total_tests": len(test_results) - 1,  # Exclude summary itself
            "timestamp": datetime.now().isoformat(),
            "overall_performance": {},
            "recommendations": []
        }

        # Calculate overall performance metrics
        all_response_times = []
        all_error_rates = []
        all_rps = []

        for test_name, result in test_results.items():
            if test_name == "summary" or test_name == "concurrent_apis":
                continue

            if hasattr(result, 'average_response_time'):
                all_response_times.append(result.average_response_time)
                all_error_rates.append(result.error_rate)
                all_rps.append(result.requests_per_second)

        if all_response_times:
            summary["overall_performance"] = {
                "average_response_time": statistics.mean(all_response_times),
                "average_error_rate": statistics.mean(all_error_rates),
                "average_rps": statistics.mean(all_rps),
                "best_performing_endpoint": min(test_results.items(),
                    key=lambda x: x[1].average_response_time if hasattr(x[1], 'average_response_time') else float('inf'))[0],
                "worst_performing_endpoint": max(test_results.items(),
                    key=lambda x: x[1].average_response_time if hasattr(x[1], 'average_response_time') else float('inf'))[0]
            }

        # Generate recommendations
        recommendations = []

        if summary["overall_performance"].get("average_response_time", 0) > 1000:
            recommendations.append("Consider optimizing API response times - target should be < 1000ms")

        if summary["overall_performance"].get("average_error_rate", 0) > 5:
            recommendations.append("High error rate detected - investigate API stability")

        if summary["overall_performance"].get("average_rps", 0) < 10:
            recommendations.append("Low throughput detected - consider scaling infrastructure")

        summary["recommendations"] = recommendations

        return summary

@pytest.mark.asyncio
async def test_health_check_performance():
    """Test health check endpoint performance"""
    suite = PerformanceTestSuite()
    metrics = await suite.run_health_check_test()

    # Assertions for health check
    assert metrics.total_requests > 0
    assert metrics.error_rate < 5.0  # Less than 5% error rate
    assert metrics.average_response_time < 1000  # Less than 1 second
    assert metrics.requests_per_second > 10  # At least 10 RPS

@pytest.mark.asyncio
async def test_dld_api_performance():
    """Test DLD API performance"""
    suite = PerformanceTestSuite()
    metrics = await suite.run_dld_api_test()

    # Assertions for DLD API
    assert metrics.total_requests > 0
    assert metrics.error_rate < 10.0  # Less than 10% error rate
    assert metrics.average_response_time < 2000  # Less than 2 seconds
    assert metrics.requests_per_second > 5  # At least 5 RPS

@pytest.mark.asyncio
async def test_stress_test():
    """Test system under stress"""
    suite = PerformanceTestSuite()
    metrics = await suite.run_stress_test()

    # Assertions for stress test
    assert metrics.total_requests > 0
    assert metrics.error_rate < 20.0  # Less than 20% error rate under stress
    assert metrics.average_response_time < 5000  # Less than 5 seconds under stress

@pytest.mark.asyncio
async def test_endurance_test():
    """Test system endurance"""
    suite = PerformanceTestSuite()
    metrics = await suite.run_endurance_test()

    # Assertions for endurance test
    assert metrics.total_requests > 0
    assert metrics.error_rate < 15.0  # Less than 15% error rate over time
    assert metrics.average_response_time < 3000  # Less than 3 seconds over time

async def main():
    """Run comprehensive performance tests"""
    print("🚀 Starting PropCalc Performance Test Suite")
    print("=" * 60)

    suite = PerformanceTestSuite()
    results = await suite.run_all_tests()

    # Print summary
    if "summary" in results:
        summary = results["summary"]
        print("\n📊 PERFORMANCE TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Timestamp: {summary['timestamp']}")

        if "overall_performance" in summary:
            perf = summary["overall_performance"]
            print(f"Average Response Time: {perf.get('average_response_time', 0):.2f}ms")
            print(f"Average Error Rate: {perf.get('average_error_rate', 0):.2f}%")
            print(f"Average RPS: {perf.get('average_rps', 0):.2f}")
            print(f"Best Performing: {perf.get('best_performing_endpoint', 'N/A')}")
            print(f"Worst Performing: {perf.get('worst_performing_endpoint', 'N/A')}")

        if "recommendations" in summary:
            print("\n💡 RECOMMENDATIONS:")
            for rec in summary["recommendations"]:
                print(f"  • {rec}")

    print("\n✅ Performance test suite completed!")

if __name__ == "__main__":
    asyncio.run(main())
