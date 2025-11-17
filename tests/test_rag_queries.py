"""
Comprehensive test suite for the RAG query system.
Tests various types of questions against the sample PDFs.
"""

from src.query.query import QueryEngine
import time
from typing import List, Tuple, Optional

class RAGTester:
    def __init__(self):
        """Initialize the test suite."""
        print("Initializing RAG Query Test Suite...")
        self.engine = QueryEngine()
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def run_test(self,
                 question: str,
                 expected_answer_contains: Optional[List[str]] = None,
                 test_name: str = "",
                 debug: bool = False) -> Tuple[bool, str]:
        """
        Run a single test query.

        Args:
            question: The question to ask
            expected_answer_contains: List of strings that should appear in the answer
            test_name: Name/description of the test
            debug: Whether to print debug info

        Returns:
            Tuple of (passed: bool, answer: str)
        """
        print(f"\n{'='*80}")
        print(f"TEST: {test_name}")
        print(f"QUESTION: {question}")
        print(f"{'='*80}")

        start_time = time.time()
        answer = self.engine.ask(question, debug=debug)
        elapsed_time = time.time() - start_time

        print(f"\nANSWER: {answer}")
        print(f"\nTime taken: {elapsed_time:.2f} seconds")

        # Check if expected content is in the answer
        passed = True
        if expected_answer_contains:
            for expected in expected_answer_contains:
                if expected.lower() not in answer.lower():
                    passed = False
                    print(f"❌ FAILED: Expected to find '{expected}' in answer")
                    break

        if passed and expected_answer_contains:
            print(f"✓ PASSED: Answer contains expected content")
            self.tests_passed += 1
        elif not expected_answer_contains:
            print(f"⚠ INFO: Manual verification needed (no expected answer provided)")
        else:
            self.tests_failed += 1

        self.test_results.append({
            'test_name': test_name,
            'question': question,
            'answer': answer,
            'passed': passed,
            'time': elapsed_time
        })

        return passed, answer

    def run_all_tests(self):
        """Run all test cases."""
        print("\n" + "="*80)
        print("STARTING COMPREHENSIVE RAG QUERY TESTS")
        print("="*80)

        # Test 1: Simple lookup from project budget
        self.run_test(
            question="What is the estimated hours for software development?",
            expected_answer_contains=["160"],
            test_name="1. Simple Table Lookup - Single Value"
        )

        # Test 2: Cost calculation
        self.run_test(
            question="What is the total project budget?",
            expected_answer_contains=["50,400", "50400"],
            test_name="2. Table Total Lookup"
        )

        # Test 3: Timeline query
        self.run_test(
            question="When does the development phase end?",
            expected_answer_contains=["2024-04-22", "April 22"],
            test_name="3. Date Lookup from Timeline Table"
        )

        # Test 4: Financial report - revenue query
        self.run_test(
            question="What was the Q4 2023 revenue for Cloud Services?",
            expected_answer_contains=["950,000", "950000"],
            test_name="4. Specific Cell Lookup - Revenue Data"
        )

        # Test 5: Growth percentage
        self.run_test(
            question="What was the revenue growth percentage for Enterprise Software?",
            expected_answer_contains=["16.7"],
            test_name="5. Percentage Value Lookup"
        )

        # Test 6: Expense breakdown
        self.run_test(
            question="How much was spent on Marketing & Sales in Q4?",
            expected_answer_contains=["380,000", "380000"],
            test_name="6. Expense Category Lookup"
        )

        # Test 7: Machine learning model performance
        self.run_test(
            question="Which machine learning model had the highest accuracy?",
            expected_answer_contains=["Random Forest", "94.2"],
            test_name="7. Best Performer Identification"
        )

        # Test 8: Model comparison
        self.run_test(
            question="What was the F1 score of XGBoost?",
            expected_answer_contains=["93.6"],
            test_name="8. Model Metric Lookup"
        )

        # Test 9: Dataset characteristics
        self.run_test(
            question="How many samples were in the training set?",
            expected_answer_contains=["40,000", "40000"],
            test_name="9. Dataset Information Lookup"
        )

        # Test 10: Hardware specifications
        self.run_test(
            question="What processor does the CloudServer Pro X500 use?",
            expected_answer_contains=["Intel Xeon Gold 6348", "28 cores"],
            test_name="10. Product Specification Lookup"
        )

        # Test 11: Memory specification
        self.run_test(
            question="How much RAM does the X500 have?",
            expected_answer_contains=["512", "GB"],
            test_name="11. Hardware Component Specification"
        )

        # Test 12: Performance benchmark
        self.run_test(
            question="What is the storage IOPS for the X500?",
            expected_answer_contains=["2,500,000", "2500000"],
            test_name="12. Performance Metric Lookup"
        )

        # Test 13: Regional sales
        self.run_test(
            question="What were the total sales for Asia-Pacific in 2023?",
            expected_answer_contains=["4.7M", "4.7"],
            test_name="13. Regional Total Lookup"
        )

        # Test 14: Quarterly sales
        self.run_test(
            question="What were North America Q4 sales?",
            expected_answer_contains=["1.5M", "1.5"],
            test_name="14. Quarterly Regional Sales"
        )

        # Test 15: Top performer
        self.run_test(
            question="Who was the top sales representative and what were their total sales?",
            expected_answer_contains=["Sarah Johnson", "2,100,000"],
            test_name="15. Top Performer Identification"
        )

        # Test 16: Average deal size
        self.run_test(
            question="What was Marcus Schmidt's average deal size?",
            expected_answer_contains=["43,421"],
            test_name="16. Calculated Metric Lookup"
        )

        # Test 17: Cross-document query
        self.run_test(
            question="What was the growth rate for Asia-Pacific?",
            expected_answer_contains=["45"],
            test_name="17. Growth Rate Lookup"
        )

        # Test 18: Multiple values
        self.run_test(
            question="List all the phases in the project timeline.",
            expected_answer_contains=["Requirements", "Design", "Development", "Testing", "Deployment"],
            test_name="18. Multiple Row Lookup"
        )

        # Test 19: Comparison query
        self.run_test(
            question="Compare the accuracy of Random Forest and XGBoost models.",
            expected_answer_contains=["Random Forest", "94.2", "XGBoost", "93.8"],
            test_name="19. Model Comparison Query"
        )

        # Test 20: Summary query
        self.run_test(
            question="What are the main expense categories and their amounts?",
            expected_answer_contains=["Salaries", "1,200,000", "Marketing", "380,000"],
            test_name="20. Multiple Category Summary"
        )

    def print_summary(self):
        """Print test summary."""
        print("\n\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total tests run: {len(self.test_results)}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_failed}")

        if self.test_results:
            avg_time = sum(r['time'] for r in self.test_results) / len(self.test_results)
            print(f"Average response time: {avg_time:.2f} seconds")

        print("\n" + "="*80)
        print("DETAILED RESULTS")
        print("="*80)

        for i, result in enumerate(self.test_results, 1):
            status = "✓ PASS" if result['passed'] else "❌ FAIL"
            print(f"\n{i}. {result['test_name']}")
            print(f"   Status: {status}")
            print(f"   Time: {result['time']:.2f}s")
            if not result['passed']:
                print(f"   Question: {result['question']}")
                print(f"   Answer: {result['answer'][:200]}...")

        print("\n" + "="*80)
        if self.tests_failed == 0:
            print("✓ ALL TESTS PASSED!")
        else:
            print(f"⚠ {self.tests_failed} tests failed. Review the output above for details.")
        print("="*80)

def main():
    """Main test execution function."""
    import sys

    # Check if debug mode is requested
    debug = "--debug" in sys.argv

    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║        RAG Query System - Comprehensive Test Suite                   ║
    ║                                                                      ║
    ║  This script tests the RAG system with various question types:      ║
    ║  - Simple table lookups                                             ║
    ║  - Row/column intersection queries                                  ║
    ║  - Calculated metrics                                               ║
    ║  - Multi-value extractions                                          ║
    ║  - Comparison queries                                               ║
    ║                                                                      ║
    ║  Prerequisites:                                                     ║
    ║  1. Generate PDFs: python generate_sample_pdfs.py                   ║
    ║  2. Ingest data: python run_pipeline.py                            ║
    ║  3. Ollama running with llama3:8b model                            ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)

    input("\nPress Enter to start testing (or Ctrl+C to cancel)...")

    tester = RAGTester()

    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\nError during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tester.print_summary()

if __name__ == "__main__":
    main()
