#!/usr/bin/env python3
"""
Test script for document-lens batch processing functionality
"""

import asyncio
import json
import requests
import time
from typing import Dict, List

class BatchProcessingTest:
    """Test suite for batch processing endpoints"""

    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.job_id = None

    def test_health_check(self) -> bool:
        """Test if document-lens service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            health_data = response.json()
            print(f"✅ Service health: {health_data['status']} (version {health_data['version']})")
            return True
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

    def test_batch_health_check(self) -> bool:
        """Test batch processing health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/batch/health")
            response.raise_for_status()
            health_data = response.json()
            print(f"✅ Batch system health: {health_data['status']} - {health_data['active_jobs']} active jobs")
            return True
        except Exception as e:
            print(f"❌ Batch health check failed: {e}")
            return False

    def test_create_job(self) -> bool:
        """Test creating a new batch job"""
        try:
            job_data = {
                "name": "Test Batch Job",
                "description": "Testing batch processing functionality",
                "analysis_type": "text",
                "analysis_options": {
                    "citation_style": "apa"
                },
                "priority": "normal",
                "max_retries": 2
            }

            response = requests.post(f"{self.base_url}/batch/jobs", json=job_data)
            response.raise_for_status()
            job_info = response.json()

            self.job_id = job_info["id"]
            print(f"✅ Created batch job: {self.job_id}")
            print(f"   Status: {job_info['status']['current_status']}")
            return True

        except Exception as e:
            print(f"❌ Failed to create batch job: {e}")
            return False

    def test_add_items(self) -> bool:
        """Test adding items to the batch job"""
        if not self.job_id:
            print("❌ No job ID available - create job first")
            return False

        try:
            # Sample documents for testing
            test_documents = [
                {
                    "text": "This is a sample document for testing batch processing. It contains multiple sentences to analyze readability. The document should be processed successfully.",
                    "filename": "test_doc_1.txt",
                    "metadata": {
                        "author": "Test Author 1",
                        "category": "test",
                        "year": "2024"
                    }
                },
                {
                    "text": "Another test document with different content. This document focuses on academic writing style and contains references. According to Smith (2023), batch processing improves efficiency significantly.",
                    "filename": "test_doc_2.txt",
                    "metadata": {
                        "author": "Test Author 2",
                        "category": "academic",
                        "year": "2024"
                    }
                },
                {
                    "text": "A third document for comprehensive testing. This document has complex sentences with multiple clauses, which should result in different readability scores compared to the previous documents.",
                    "filename": "test_doc_3.txt",
                    "metadata": {
                        "author": "Test Author 3",
                        "category": "complex",
                        "year": "2024"
                    }
                }
            ]

            response = requests.post(
                f"{self.base_url}/batch/jobs/{self.job_id}/items",
                json=test_documents
            )
            response.raise_for_status()
            result = response.json()

            print(f"✅ Added {result['items_added']} items to job")
            print(f"   Total items: {result['total_items']}")
            return True

        except Exception as e:
            print(f"❌ Failed to add items: {e}")
            return False

    def test_start_job(self) -> bool:
        """Test starting the batch job"""
        if not self.job_id:
            print("❌ No job ID available")
            return False

        try:
            response = requests.post(f"{self.base_url}/batch/jobs/{self.job_id}/start")
            response.raise_for_status()
            result = response.json()

            print(f"✅ Started job: {result['status']}")
            return True

        except Exception as e:
            print(f"❌ Failed to start job: {e}")
            return False

    def test_job_monitoring(self, max_wait_time: int = 60) -> bool:
        """Test job status monitoring"""
        if not self.job_id:
            print("❌ No job ID available")
            return False

        try:
            start_time = time.time()
            while time.time() - start_time < max_wait_time:
                response = requests.get(f"{self.base_url}/batch/jobs/{self.job_id}")
                response.raise_for_status()
                job_info = response.json()

                status = job_info["status"]["current_status"]
                progress = job_info["status"]["progress_percentage"]
                completed = job_info["status"]["completed_items"]
                total = job_info["status"]["total_items"]

                print(f"📊 Job status: {status} - {progress:.1f}% ({completed}/{total})")

                if status == "completed":
                    print(f"✅ Job completed successfully!")
                    return True
                elif status == "failed":
                    print(f"❌ Job failed")
                    return False

                time.sleep(2)  # Check every 2 seconds

            print(f"⏰ Job monitoring timeout after {max_wait_time}s")
            return False

        except Exception as e:
            print(f"❌ Job monitoring failed: {e}")
            return False

    def test_get_job_items(self) -> bool:
        """Test retrieving job items"""
        if not self.job_id:
            print("❌ No job ID available")
            return False

        try:
            response = requests.get(f"{self.base_url}/batch/jobs/{self.job_id}/items")
            response.raise_for_status()
            items = response.json()

            print(f"✅ Retrieved {len(items)} job items")
            for item in items:
                print(f"   Item {item['id'][:8]}...: {item['status']}")
                if item['status'] == 'completed' and item.get('result_data'):
                    result = item['result_data']
                    print(f"      Word count: {result.get('word_count', 'N/A')}")
                    print(f"      Readability: {result.get('readability_score', 'N/A')}")

            return True

        except Exception as e:
            print(f"❌ Failed to get job items: {e}")
            return False

    def test_export_results(self, export_format: str = "jsonl") -> bool:
        """Test exporting job results"""
        if not self.job_id:
            print("❌ No job ID available")
            return False

        try:
            export_data = {
                "export_format": export_format,
                "include_metadata": True,
                "filter_status": ["completed"]
            }

            response = requests.post(
                f"{self.base_url}/batch/jobs/{self.job_id}/export",
                json=export_data
            )
            response.raise_for_status()
            export_info = response.json()

            print(f"✅ Export created: {export_format} format")
            print(f"   Download URL: {export_info['download_url']}")
            print(f"   File size: {export_info['file_size_bytes']} bytes")
            print(f"   Item count: {export_info['item_count']}")

            return True

        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False

    def test_list_jobs(self) -> bool:
        """Test listing all batch jobs"""
        try:
            response = requests.get(f"{self.base_url}/batch/jobs")
            response.raise_for_status()
            jobs = response.json()

            print(f"✅ Listed {len(jobs)} batch jobs")
            for job in jobs:
                status = job["status"]["current_status"]
                progress = job["status"]["progress_percentage"]
                print(f"   Job {job['id'][:8]}... ({job['name']}): {status} - {progress:.1f}%")

            return True

        except Exception as e:
            print(f"❌ Failed to list jobs: {e}")
            return False

    def run_full_test_suite(self) -> bool:
        """Run the complete test suite"""
        print("🧪 Starting Document-Lens Batch Processing Test Suite")
        print("=" * 60)

        tests = [
            ("Service Health Check", self.test_health_check),
            ("Batch Health Check", self.test_batch_health_check),
            ("Create Batch Job", self.test_create_job),
            ("Add Items to Job", self.test_add_items),
            ("Start Job Processing", self.test_start_job),
            ("Monitor Job Progress", self.test_job_monitoring),
            ("Get Job Items", self.test_get_job_items),
            ("Export Results (JSONL)", lambda: self.test_export_results("jsonl")),
            ("Export Results (CSV)", lambda: self.test_export_results("csv")),
            ("List All Jobs", self.test_list_jobs)
        ]

        results = []
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            print("-" * 40)
            result = test_func()
            results.append((test_name, result))

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)

        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
            if result:
                passed += 1

        total = len(results)
        print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

        if passed == total:
            print("🎉 All tests passed! Batch processing is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the service and try again.")

        return passed == total


def main():
    """Main test execution"""
    tester = BatchProcessingTest()

    if not tester.test_health_check():
        print("❌ Document-lens service is not running on http://localhost:8002")
        print("Please start the service and try again.")
        return

    success = tester.run_full_test_suite()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()