"""
UI Change Documentation System
Creates comprehensive reports of UI state changes during testing
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class UIStateChange:
    """Represents a single UI state change event"""
    timestamp: str
    element_locator: str
    event_type: str  # 'appearance', 'disappearance', 'staleness'
    duration: float
    initial_state: Dict
    final_state: Dict
    success: bool
    test_name: str
    page_url: str
    notes: str = ""


class UIDocumentationSystem:
    """
    Comprehensive system to document UI state changes with reports and analysis
    """
    
    def __init__(self, report_dir: str = "reports/ui_changes"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.changes: List[UIStateChange] = []
        self.session_start = datetime.now()
        
    def record_change(self, change: UIStateChange):
        """Record a UI state change"""
        self.changes.append(change)
        
    def generate_report(self, test_session_name: str = "default_session") -> str:
        """Generate a comprehensive report of all UI changes"""
        report_data = {
            "session_info": {
                "session_name": test_session_name,
                "start_time": self.session_start.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration": str(datetime.now() - self.session_start),
                "total_changes": len(self.changes)
            },
            "changes": [asdict(change) for change in self.changes],
            "summary": self._generate_summary()
        }
        
        # Write JSON report
        json_report_path = self.report_dir / f"ui_changes_{test_session_name}.json"
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # Write human-readable report
        md_report_path = self.report_dir / f"ui_changes_{test_session_name}.md"
        self._write_markdown_report(report_data, md_report_path)
        
        return str(json_report_path)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for the session"""
        if not self.changes:
            return {"message": "No UI state changes recorded"}
        
        # Count by event type
        event_counts = {}
        total_duration = 0
        successful_changes = 0
        
        for change in self.changes:
            event_counts[change.event_type] = event_counts.get(change.event_type, 0) + 1
            total_duration += change.duration
            if change.success:
                successful_changes += 1
        
        avg_duration = total_duration / len(self.changes) if self.changes else 0
        
        return {
            "event_type_counts": event_counts,
            "successful_changes": successful_changes,
            "total_changes": len(self.changes),
            "success_rate": f"{(successful_changes / len(self.changes) * 100):.1f}%" if self.changes else "0%",
            "average_duration": f"{avg_duration:.2f}s",
            "total_duration": f"{total_duration:.2f}s"
        }
    
    def _write_markdown_report(self, report_data: Dict, output_path: Path):
        """Write a human-readable markdown report"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# UI State Change Report\n\n")
            f.write(f"**Session**: {report_data['session_info']['session_name']}\n")
            f.write(f"**Start Time**: {report_data['session_info']['start_time']}\n")
            f.write(f"**End Time**: {report_data['session_info']['end_time']}\n")
            f.write(f"**Duration**: {report_data['session_info']['duration']}\n\n")
            
            # Summary
            summary = report_data['summary']
            f.write("## Summary\n")
            if 'message' in summary:
                f.write(f"{summary['message']}\n\n")
            else:
                f.write(f"- Total UI State Changes: {summary['total_changes']}\n")
                f.write(f"- Successful Changes: {summary['successful_changes']}\n")
                f.write(f"- Success Rate: {summary['success_rate']}\n")
                f.write(f"- Average Duration: {summary['average_duration']}\n")
                
                f.write("\n### Changes by Type:\n")
                for event_type, count in summary['event_type_counts'].items():
                    f.write(f"- {event_type}: {count}\n")
                f.write("\n")
            
            # Detailed changes
            f.write("## Detailed Changes\n")
            for i, change in enumerate(report_data['changes'], 1):
                f.write(f"### Change {i}\n")
                f.write(f"- **Element**: `{change['element_locator']}`\n")
                f.write(f"- **Event**: {change['event_type']}\n") 
                f.write(f"- **Duration**: {change['duration']:.2f}s\n")
                f.write(f"- **Success**: {'✓' if change['success'] else '✗'}\n")
                f.write(f"- **URL**: {change['page_url']}\n")
                if change['notes']:
                    f.write(f"- **Notes**: {change['notes']}\n")
                f.write("\n")
    
    def create_visual_timeline(self) -> str:
        """Create a visual timeline of UI changes"""
        if not self.changes:
            return "No changes to visualize"
        
        # Sort changes by timestamp
        sorted_changes = sorted(self.changes, key=lambda x: x.timestamp)
        
        timeline_file = self.report_dir / "ui_timeline.md"
        with open(timeline_file, 'w', encoding='utf-8') as f:
            f.write("# UI Change Timeline\n\n")
            
            for change in sorted_changes:
                status_icon = "✅" if change.success else "❌"
                f.write(f"{status_icon} **{change.event_type.upper()}** - `{change.element_locator}`\n")
                f.write(f"  *{change.timestamp} - Duration: {change.duration:.2f}s*\n")
                f.write(f"  *URL: {change.page_url}*\n\n")
        
        return str(timeline_file)


# Example usage and testing
if __name__ == "__main__":
    doc_system = UIDocumentationSystem()
    
    # Example of how this would be used in a test
    print("UI Documentation System created successfully")
    print("To use in tests:")
    print("1. Create a UIDocumentationSystem instance")
    print("2. Record UI changes using doc_system.record_change()") 
    print("3. Generate reports with doc_system.generate_report()")