"""
Test script for the FinancialTableDetectorAgent.
"""
import os
import sys
import cv2
import numpy as np
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_sample_table_image(width=800, height=600):
    """
    Create a sample image with a financial table for testing.

    Args:
        width: Image width
        height: Image height

    Returns:
        Sample image as numpy array
    """
    # Create a blank image
    image = np.ones((height, width), dtype=np.uint8) * 255

    # Add table grid lines
    # Horizontal lines
    for y in range(100, 401, 50):
        cv2.line(image, (100, y), (700, y), (0, 0, 0), 1)

    # Vertical lines
    for x in range(100, 701, 150):
        cv2.line(image, (x, 100), (x, 400), (0, 0, 0), 1)

    # Add table headers
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, "Security", (120, 90), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "Quantity", (270, 90), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "Price", (420, 90), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "Value", (570, 90), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)

    # Add table data
    cv2.putText(image, "Apple Inc.", (120, 140), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "100", (270, 140), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$150.25", (420, 140), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$15,025.00", (570, 140), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)

    cv2.putText(image, "Microsoft", (120, 190), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "50", (270, 190), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$300.50", (420, 190), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$15,025.00", (570, 190), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)

    cv2.putText(image, "Amazon", (120, 240), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "25", (270, 240), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$130.75", (420, 240), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$3,268.75", (570, 240), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)

    cv2.putText(image, "Tesla", (120, 290), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "30", (270, 290), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$220.00", (420, 290), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$6,600.00", (570, 290), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)

    cv2.putText(image, "NVIDIA", (120, 340), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "40", (270, 340), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$450.25", (420, 340), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$18,010.00", (570, 340), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)

    cv2.putText(image, "Total", (120, 390), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "$57,928.75", (570, 390), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)

    # Add some noise
    noise = np.random.randint(0, 10, (height, width), dtype=np.uint8)
    image = cv2.subtract(image, noise)

    return image

def test_financial_table_detector_agent(api_key=None):
    """Test the FinancialTableDetectorAgent."""
    try:
        from DevDocs.backend.agents.financial_table_detector_agent import FinancialTableDetectorAgent

        # Check for API key
        api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("Error: OpenRouter API key is required. Provide it with --api-key or set OPENROUTER_API_KEY environment variable.")
            return {
                "agent_name": "FinancialTableDetectorAgent",
                "test_date": datetime.now().isoformat(),
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "success_rate": 0,
                "error": "API key not provided"
            }

        print(f"\n=== Testing FinancialTableDetectorAgent ===\n")

        # Create the agent
        agent = FinancialTableDetectorAgent(api_key=api_key)

        # Create a sample table image
        image = create_sample_table_image()

        # Convert to BGR if it's grayscale
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Save the sample image
        output_dir = Path("./test_output")
        output_dir.mkdir(exist_ok=True, parents=True)
        sample_path = output_dir / "sample_table.png"
        cv2.imwrite(str(sample_path), image)
        print(f"Created sample table image: {sample_path}")

        # Create test cases
        test_cases = [
            {
                "description": "Detect table in sample image",
                "input": {
                    "image": image,
                    "language": "eng"
                },
                "expected": {
                    "status": "success"
                }
            }
        ]

        results = {
            "agent_name": "FinancialTableDetectorAgent",
            "test_date": datetime.now().isoformat(),
            "total_tests": len(test_cases),
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": []
        }

        for i, test_case in enumerate(test_cases):
            print(f"Test {i+1}/{len(test_cases)}: {test_case.get('description', 'No description')}")

            try:
                start_time = datetime.now()
                result = agent.process(test_case["input"])
                end_time = datetime.now()

                # Check if the test passed
                passed = True
                if "status" in test_case["expected"]:
                    if "status" not in result or result["status"] != test_case["expected"]["status"]:
                        passed = False
                        print(f"Status mismatch: expected {test_case['expected']['status']}, got {result.get('status', 'None')}")

                # Record the result
                test_result = {
                    "test_id": i + 1,
                    "description": test_case.get("description", "No description"),
                    "passed": passed,
                    "execution_time": (end_time - start_time).total_seconds(),
                    "input": test_case.get("input", {}),
                    "expected": test_case.get("expected", {}),
                    "actual": result
                }

                # Update counters
                if passed:
                    results["passed_tests"] += 1
                    print("✓ Test passed")

                    # If the test passed, save the detected tables
                    if "tables" in result:
                        print(f"Detected {len(result['tables'])} tables")

                        # Save the table data
                        table_data_path = output_dir / "table_data.json"
                        with open(table_data_path, 'w', encoding='utf-8') as f:
                            json.dump(result["tables"], f, indent=2)
                        print(f"Saved table data to {table_data_path}")

                        # If there are table images, save them
                        if "table_images" in result:
                            for j, table_img in enumerate(result["table_images"]):
                                table_img_path = output_dir / f"table_{j+1}.png"
                                cv2.imwrite(str(table_img_path), table_img)
                                print(f"Saved table image to {table_img_path}")
                else:
                    results["failed_tests"] += 1
                    print("X Test failed")

                results["test_results"].append(test_result)

            except Exception as e:
                print(f"X Test failed with exception: {str(e)}")

                # Record the error
                test_result = {
                    "test_id": i + 1,
                    "description": test_case.get("description", "No description"),
                    "passed": False,
                    "execution_time": 0,
                    "input": test_case.get("input", {}),
                    "expected": test_case.get("expected", {}),
                    "actual": {"error": str(e)}
                }

                results["failed_tests"] += 1
                results["test_results"].append(test_result)

        # Calculate success rate
        results["success_rate"] = (results["passed_tests"] / results["total_tests"]) * 100 if results["total_tests"] > 0 else 0

        # Print summary
        print(f"\nSummary for FinancialTableDetectorAgent:")
        print(f"Total tests: {results['total_tests']}")
        print(f"Passed tests: {results['passed_tests']}")
        print(f"Failed tests: {results['failed_tests']}")
        print(f"Success rate: {results['success_rate']:.2f}%")

        # Save results
        results_dir = Path("./evaluation_results")
        results_dir.mkdir(exist_ok=True, parents=True)
        results_path = results_dir / "financial_table_detector_evaluation.json"

        # Clean the results for JSON serialization
        clean_results = {}
        for k, v in results.items():
            if k == "test_results":
                clean_results[k] = []
                for tr in v:
                    clean_tr = {}
                    for trk, trv in tr.items():
                        if trk not in ["actual", "input"]:
                            clean_tr[trk] = trv
                        elif trk == "input":
                            clean_tr[trk] = {ik: "image data" if ik == "image" else iv for ik, iv in trv.items()}
                        else:
                            clean_tr[trk] = {ak: "image data" if ak == "table_images" else av for ak, av in trv.items()} if isinstance(trv, dict) else str(trv)
                    clean_results[k].append(clean_tr)
            else:
                clean_results[k] = v

        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(clean_results, f, indent=2)

        print(f"Results saved to {results_path}")

        return results

    except ImportError as e:
        print(f"Error importing FinancialTableDetectorAgent: {str(e)}")
        return {
            "agent_name": "FinancialTableDetectorAgent",
            "test_date": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "success_rate": 0,
            "error": str(e)
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test FinancialTableDetectorAgent")
    parser.add_argument("--api-key", help="OpenRouter API key")
    args = parser.parse_args()

    test_financial_table_detector_agent(args.api_key)
