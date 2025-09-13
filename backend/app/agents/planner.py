"""
Planner Agent - Analyzes questionnaire and creates execution plan
"""

from typing import Dict, Any, List
from .base import BaseAgent, AgentContext, AgentResult
import json


class PlannerAgent(BaseAgent):
    """
    Planner Agent - First agent in the pipeline
    
    Responsibilities:
    - Analyze questionnaire template schema
    - Identify required fields and their types
    - Create execution plan for other agents
    - Prioritize fields based on complexity and dependencies
    """
    
    def __init__(self):
        super().__init__("planner")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute planner logic"""
        try:
            schema = context.questionnaire_schema
            
            # Analyze questionnaire structure
            fields = self._extract_fields(schema)
            
            # Create execution plan
            execution_plan = self._create_execution_plan(fields)
            
            # Prioritize fields
            prioritized_fields = self._prioritize_fields(fields)
            
            return AgentResult(
                success=True,
                data={
                    "fields": fields,
                    "execution_plan": execution_plan,
                    "prioritized_fields": prioritized_fields,
                    "total_fields": len(fields)
                },
                next_agent="retriever"
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                errors=[f"Planner execution failed: {str(e)}"]
            )
    
    def _extract_fields(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all fields from questionnaire schema"""
        fields = []
        
        def extract_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    if self._is_field(value):
                        fields.append({
                            "id": current_path,
                            "type": value.get("type", "text"),
                            "label": value.get("label", key),
                            "required": value.get("required", False),
                            "options": value.get("options", []),
                            "validation": value.get("validation", {}),
                            "dependencies": value.get("dependencies", [])
                        })
                    else:
                        extract_recursive(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_recursive(item, f"{path}[{i}]")
        
        extract_recursive(schema)
        return fields
    
    def _is_field(self, obj: Any) -> bool:
        """Check if object represents a form field"""
        if not isinstance(obj, dict):
            return False
        
        field_indicators = ["type", "label", "required", "validation"]
        return any(indicator in obj for indicator in field_indicators)
    
    def _create_execution_plan(self, fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create execution plan for the pipeline"""
        return {
            "phases": [
                {
                    "name": "retrieval",
                    "description": "Search answer memory and source files",
                    "fields": [f["id"] for f in fields]
                },
                {
                    "name": "mapping", 
                    "description": "Map retrieved answers to questionnaire fields",
                    "fields": [f["id"] for f in fields]
                },
                {
                    "name": "evidence",
                    "description": "Attach evidence links to answers",
                    "fields": [f["id"] for f in fields if f["required"]]
                },
                {
                    "name": "filling",
                    "description": "Fill questionnaire with answers",
                    "fields": [f["id"] for f in fields]
                },
                {
                    "name": "qa",
                    "description": "Quality assurance and validation",
                    "fields": [f["id"] for f in fields if f["required"]]
                }
            ],
            "estimated_duration": len(fields) * 2  # 2 seconds per field estimate
        }
    
    def _prioritize_fields(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize fields based on importance and complexity"""
        def priority_score(field):
            score = 0
            
            # Required fields get higher priority
            if field["required"]:
                score += 10
            
            # Simple field types are easier to fill
            simple_types = ["text", "number", "date", "boolean"]
            if field["type"] in simple_types:
                score += 5
            
            # Fields with dependencies get lower priority
            if field["dependencies"]:
                score -= len(field["dependencies"]) * 2
            
            return score
        
        return sorted(fields, key=priority_score, reverse=True)

