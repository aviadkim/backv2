"""
Test script for evaluating agent performance.
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

class AgentEvaluator:
    """Class for evaluating agent performance."""
    
    def __init__(self, output_dir="./evaluation_results"):
        """Initialize the evaluator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.results = {}
    
    def evaluate_agent(self, agent_name, agent_instance, test_cases):
        """
        Evaluate an agent on a set of test cases.
        
        Args:
            agent_name: Name of the agent
            agent_instance: Instance of the agent
            test_cases: List of test cases
            
        Returns:
            Dictionary with evaluation results
        """
        print(f"\n=== Evaluating {agent_name} ===")
        
        agent_results = {
            "agent_name": agent_name,
            "test_date": datetime.now().isoformat(),
            "total_tests": len(test_cases),
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": []
        }
        
        for i, test_case in enumerate(test_cases):
            print(f"\nTest {i+1}/{len(test_cases)}: {test_case.get('description', 'No description')}")
            
            # Run the test
            try:
                start_time = datetime.now()
                result = agent_instance.process(test_case.get("input", {}))
                end_time = datetime.now()
                
                # Check if the test passed
                passed = self._validate_result(result, test_case.get("expected", {}))
                
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
                    agent_results["passed_tests"] += 1
                    print("✅ Test passed")
                else:
                    agent_results["failed_tests"] += 1
                    print("❌ Test failed")
                
                agent_results["test_results"].append(test_result)
                
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
                
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
                
                agent_results["failed_tests"] += 1
                agent_results["test_results"].append(test_result)
        
        # Calculate success rate
        agent_results["success_rate"] = (agent_results["passed_tests"] / agent_results["total_tests"]) * 100 if agent_results["total_tests"] > 0 else 0
        
        # Print summary
        print(f"\nSummary for {agent_name}:")
        print(f"Total tests: {agent_results['total_tests']}")
        print(f"Passed tests: {agent_results['passed_tests']}")
        print(f"Failed tests: {agent_results['failed_tests']}")
        print(f"Success rate: {agent_results['success_rate']:.2f}%")
        
        # Save results
        self.results[agent_name] = agent_results
        self._save_results(agent_name, agent_results)
        
        return agent_results
    
    def _validate_result(self, actual, expected):
        """
        Validate the result against the expected output.
        
        Args:
            actual: Actual result
            expected: Expected result
            
        Returns:
            True if the result is valid, False otherwise
        """
        # If expected is empty, consider the test passed
        if not expected:
            return True
        
        # Check if the actual result contains all expected keys
        for key, value in expected.items():
            if key not in actual:
                print(f"Missing key: {key}")
                return False
            
            # For status, check exact match
            if key == "status" and actual[key] != value:
                print(f"Status mismatch: expected {value}, got {actual[key]}")
                return False
        
        return True
    
    def _save_results(self, agent_name, results):
        """
        Save evaluation results to a file.
        
        Args:
            agent_name: Name of the agent
            results: Evaluation results
        """
        # Create a clean filename
        filename = f"{agent_name.replace(' ', '_').lower()}_evaluation.json"
        file_path = self.output_dir / filename
        
        # Save the results
        with open(file_path, 'w', encoding='utf-8') as f:
            # Remove numpy arrays and other non-serializable objects
            clean_results = self._clean_for_json(results)
            json.dump(clean_results, f, indent=2)
        
        print(f"Results saved to {file_path}")
    
    def _clean_for_json(self, obj):
        """
        Clean an object for JSON serialization.
        
        Args:
            obj: Object to clean
            
        Returns:
            JSON-serializable object
        """
        if isinstance(obj, dict):
            return {k: self._clean_for_json(v) for k, v in obj.items() if k not in ["preprocessed_image", "image"]}
        elif isinstance(obj, list):
            return [self._clean_for_json(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return "numpy.ndarray"
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)

def create_sample_image(width=500, height=500, text="Sample Text", skew_angle=15, noise_level=50):
    """
    Create a sample image for testing.
    
    Args:
        width: Image width
        height: Image height
        text: Text to add to the image
        skew_angle: Angle to skew the image
        noise_level: Level of noise to add
        
    Returns:
        Sample image as numpy array
    """
    # Create a blank image
    image = np.ones((height, width), dtype=np.uint8) * 255
    
    # Add some text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, text, (width // 4, height // 2), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
    
    # Add some noise
    if noise_level > 0:
        noise = np.random.randint(0, noise_level, (height, width), dtype=np.uint8)
        image = cv2.subtract(image, noise)
    
    # Add skew
    if skew_angle != 0:
        M = cv2.getRotationMatrix2D((width / 2, height / 2), skew_angle, 1)
        image = cv2.warpAffine(image, M, (width, height))
    
    return image

def test_document_preprocessor_agent():
    """Test the DocumentPreprocessorAgent."""
    from DevDocs.backend.agents.document_preprocessor_agent import DocumentPreprocessorAgent
    
    # Create the agent
    agent = DocumentPreprocessorAgent()
    
    # Create test cases
    test_cases = [
        {
            "description": "Basic image preprocessing",
            "input": {
                "image": create_sample_image(500, 500, "Sample Text", 15, 50),
                "options": {
                    "enhance_contrast": True,
                    "fix_skew": True,
                    "remove_noise": True,
                    "binarize": False
                }
            },
            "expected": {
                "status": "success"
            }
        },
        {
            "description": "Image preprocessing with binarization",
            "input": {
                "image": create_sample_image(500, 500, "Financial Document", 10, 30),
                "options": {
                    "enhance_contrast": True,
                    "fix_skew": True,
                    "remove_noise": True,
                    "binarize": True
                }
            },
            "expected": {
                "status": "success"
            }
        },
        {
            "description": "Image preprocessing without skew correction",
            "input": {
                "image": create_sample_image(500, 500, "No Skew Correction", 20, 40),
                "options": {
                    "enhance_contrast": True,
                    "fix_skew": False,
                    "remove_noise": True,
                    "binarize": False
                }
            },
            "expected": {
                "status": "success"
            }
        },
        {
            "description": "Image preprocessing with high DPI",
            "input": {
                "image": create_sample_image(500, 500, "High DPI", 5, 20),
                "options": {
                    "enhance_contrast": True,
                    "fix_skew": True,
                    "remove_noise": True,
                    "binarize": False,
                    "dpi": 600
                }
            },
            "expected": {
                "status": "success"
            }
        },
        {
            "description": "Text region detection",
            "input": {
                "image": create_sample_image(800, 600, "Text Region Detection", 0, 10),
                "options": {
                    "enhance_contrast": True,
                    "fix_skew": True,
                    "remove_noise": True
                }
            },
            "expected": {
                "status": "success"
            }
        }
    ]
    
    # Evaluate the agent
    evaluator = AgentEvaluator()
    results = evaluator.evaluate_agent("DocumentPreprocessorAgent", agent, test_cases)
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test agent evaluation")
    parser.add_argument("--agent", help="Agent to test", default="document_preprocessor")
    args = parser.parse_args()
    
    if args.agent == "document_preprocessor":
        test_document_preprocessor_agent()
    else:
        print(f"Unknown agent: {args.agent}")
