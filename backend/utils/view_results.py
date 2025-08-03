"""
Utility script to view and analyze JSON results
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import sys

class ResultsViewer:
    def __init__(self, results_dir: str = "./data/results"):
        self.results_dir = results_dir
    
    def list_all_results(self) -> Dict[str, List[str]]:
        """List all result files organized by type"""
        results = {
            "attempts": [],
            "feedback": [],
            "complete_results": [],
            "daily_summaries": []
        }
        
        # List attempts
        attempts_dir = os.path.join(self.results_dir, "attempts")
        if os.path.exists(attempts_dir):
            results["attempts"] = [f for f in os.listdir(attempts_dir) if f.endswith('.json')]
        
        # List feedback
        feedback_dir = os.path.join(self.results_dir, "feedback")
        if os.path.exists(feedback_dir):
            results["feedback"] = [f for f in os.listdir(feedback_dir) if f.endswith('.json')]
        
        # List complete results
        if os.path.exists(self.results_dir):
            results["complete_results"] = [f for f in os.listdir(self.results_dir) 
                                         if f.startswith('complete_result_') and f.endswith('.json')]
        
        # List daily summaries
        summaries_dir = os.path.join(self.results_dir, "daily_summaries")
        if os.path.exists(summaries_dir):
            results["daily_summaries"] = [f for f in os.listdir(summaries_dir) if f.endswith('.json')]
        
        return results
    
    def view_latest_result(self) -> Dict:
        """View the most recent complete result"""
        results = self.list_all_results()
        if not results["complete_results"]:
            return {"error": "No complete results found"}
        
        # Sort by modification time
        complete_results = []
        for filename in results["complete_results"]:
            filepath = os.path.join(self.results_dir, filename)
            mtime = os.path.getmtime(filepath)
            complete_results.append((mtime, filepath, filename))
        
        complete_results.sort(reverse=True)
        latest_path = complete_results[0][1]
        
        with open(latest_path, 'r') as f:
            return json.load(f)
    
    def view_today_summary(self) -> Dict:
        """View today's summary"""
        today = datetime.now().strftime("%Y-%m-%d")
        summary_path = os.path.join(self.results_dir, "daily_summaries", f"summary_{today}.json")
        
        if not os.path.exists(summary_path):
            return {"error": "No summary for today"}
        
        with open(summary_path, 'r') as f:
            return json.load(f)
    
    def print_result_summary(self, result: Dict):
        """Pretty print a result summary"""
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        if "attempt" in result and "feedback" in result:
            # Complete result
            print("\n" + "="*60)
            print("PRACTICE ATTEMPT RESULT")
            print("="*60)
            
            attempt = result["attempt"]
            feedback = result["feedback"]
            
            print(f"\nAttempt ID: {attempt['id']}")
            print(f"Scenario: {attempt['scenario_id']}")
            print(f"Timestamp: {attempt['timestamp']}")
            print(f"\nUser Response (first 200 chars):")
            print(f"  {attempt['user_response'][:200]}...")
            
            print(f"\nOVERALL SCORE: {feedback['overall_score']}/10")
            print(f"\nDetailed Scores:")
            for category, details in feedback['detailed_scores'].items():
                print(f"  {category.replace('_', ' ').title()}: {details['score']}/10")
            
            print(f"\nGeneral Feedback:")
            print(f"  {feedback['general_feedback']}")
            
        elif "date" in result and "total_attempts" in result:
            # Daily summary
            print("\n" + "="*60)
            print(f"DAILY SUMMARY - {result['date']}")
            print("="*60)
            
            print(f"\nTotal Attempts: {result['total_attempts']}")
            print(f"Average Score: {result['average_score']}/10")
            print(f"\nScenarios Practiced:")
            for scenario_id, count in result['scenarios_practiced'].items():
                print(f"  {scenario_id}: {count} attempts")
            
            print(f"\nIndividual Attempts:")
            for attempt in result['attempts'][-5:]:  # Last 5 attempts
                print(f"  {attempt['timestamp']}: Score {attempt['score']}/10 ({attempt['scenario_id']})")

def main():
    viewer = ResultsViewer()
    
    print("Healthcare Communication Assistant - Results Viewer")
    print("-" * 50)
    
    # List all results
    all_results = viewer.list_all_results()
    print("\nAvailable Results:")
    for category, files in all_results.items():
        print(f"\n{category.replace('_', ' ').title()}: {len(files)} files")
        if files and len(files) <= 5:
            for f in files:
                print(f"  - {f}")
    
    # View latest result
    print("\n" + "-"*50)
    print("LATEST RESULT:")
    latest = viewer.view_latest_result()
    viewer.print_result_summary(latest)
    
    # View today's summary
    print("\n" + "-"*50)
    print("TODAY'S SUMMARY:")
    today_summary = viewer.view_today_summary()
    viewer.print_result_summary(today_summary)

if __name__ == "__main__":
    main()