"""
Base Agent class for RealVibe Site Copilot
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class AgentContext(BaseModel):
    """Context passed between agents"""
    site_id: str
    questionnaire_template_id: str
    run_id: str
    questionnaire_schema: Dict[str, Any]
    current_answers: Dict[str, Any] = {}
    evidence_links: Dict[str, List[Dict]] = {}
    metadata: Dict[str, Any] = {}


class AgentResult(BaseModel):
    """Result returned by an agent"""
    success: bool
    data: Dict[str, Any] = {}
    errors: List[str] = []
    warnings: List[str] = []
    next_agent: Optional[str] = None


class BaseAgent(ABC):
    """Base class for all agents in the pipeline"""
    
    def __init__(self, name: str, tools: List[Any] = None):
        self.name = name
        self.tools = tools or []
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the agent's main logic"""
        pass
    
    async def pre_execute(self, context: AgentContext) -> bool:
        """Pre-execution validation and setup"""
        self.logger.info(f"Starting {self.name} agent execution")
        return True
    
    async def post_execute(self, context: AgentContext, result: AgentResult) -> AgentResult:
        """Post-execution cleanup and validation"""
        if result.success:
            self.logger.info(f"{self.name} agent completed successfully")
        else:
            self.logger.error(f"{self.name} agent failed: {result.errors}")
        return result
    
    async def run(self, context: AgentContext) -> AgentResult:
        """Main entry point for agent execution"""
        try:
            # Pre-execution
            if not await self.pre_execute(context):
                return AgentResult(
                    success=False,
                    errors=[f"{self.name} agent pre-execution failed"]
                )
            
            # Main execution
            result = await self.execute(context)
            
            # Post-execution
            result = await self.post_execute(context, result)
            
            return result
            
        except Exception as e:
            self.logger.exception(f"Unexpected error in {self.name} agent")
            return AgentResult(
                success=False,
                errors=[f"Unexpected error in {self.name} agent: {str(e)}"]
            )

