"""
Base Tool class for RealVibe Site Copilot agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class ToolInput(BaseModel):
    """Base input for tools"""
    site_id: str
    parameters: Dict[str, Any] = {}


class ToolOutput(BaseModel):
    """Base output from tools"""
    success: bool
    data: Dict[str, Any] = {}
    errors: List[str] = []
    metadata: Dict[str, Any] = {}


class BaseTool(ABC):
    """Base class for all agent tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"tool.{name}")
    
    @abstractmethod
    async def execute(self, input_data: ToolInput) -> ToolOutput:
        """Execute the tool's main logic"""
        pass
    
    async def validate_input(self, input_data: ToolInput) -> bool:
        """Validate tool input"""
        if not input_data.site_id:
            self.logger.error("Site ID is required")
            return False
        return True
    
    async def run(self, input_data: ToolInput) -> ToolOutput:
        """Main entry point for tool execution"""
        try:
            # Validate input
            if not await self.validate_input(input_data):
                return ToolOutput(
                    success=False,
                    errors=["Invalid input data"]
                )
            
            self.logger.info(f"Executing {self.name} tool")
            
            # Execute main logic
            result = await self.execute(input_data)
            
            if result.success:
                self.logger.info(f"{self.name} tool completed successfully")
            else:
                self.logger.error(f"{self.name} tool failed: {result.errors}")
            
            return result
            
        except Exception as e:
            self.logger.exception(f"Unexpected error in {self.name} tool")
            return ToolOutput(
                success=False,
                errors=[f"Unexpected error: {str(e)}"]
            )

