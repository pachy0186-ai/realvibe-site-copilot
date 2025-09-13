"""
Agent Pipeline Orchestrator for RealVibe Site Copilot

Coordinates the execution of all agents in the pipeline:
Planner → Retriever → Mapper → Evidencer → Filler → QA → Recorder
"""

from typing import Dict, Any, List, Optional
from .base import BaseAgent, AgentContext, AgentResult
from .planner import PlannerAgent
from .retriever import RetrieverAgent
from .mapper import MapperAgent
from .evidencer import EvidencerAgent
from .filler import FillerAgent
from .qa import QAAgent
from .recorder import RecorderAgent
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentPipeline:
    """
    Main pipeline orchestrator that manages the execution of all agents
    """
    
    def __init__(self):
        self.agents = {
            "planner": PlannerAgent(),
            "retriever": RetrieverAgent(),
            "mapper": MapperAgent(),
            "evidencer": EvidencerAgent(),
            "filler": FillerAgent(),
            "qa": QAAgent(),
            "recorder": RecorderAgent()
        }
        self.execution_order = [
            "planner", "retriever", "mapper", 
            "evidencer", "filler", "qa", "recorder"
        ]
    
    async def execute(
        self, 
        site_id: str,
        questionnaire_template_id: str,
        questionnaire_schema: Dict[str, Any],
        run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete autofill pipeline
        
        Args:
            site_id: ID of the research site
            questionnaire_template_id: ID of the questionnaire template
            questionnaire_schema: The questionnaire structure
            run_id: Optional existing run ID, will create new if not provided
            
        Returns:
            Dictionary containing execution results and metrics
        """
        start_time = datetime.utcnow()
        
        # Initialize context
        context = AgentContext(
            site_id=site_id,
            questionnaire_template_id=questionnaire_template_id,
            run_id=run_id or f"run_{int(start_time.timestamp())}",
            questionnaire_schema=questionnaire_schema
        )
        
        results = {}
        execution_log = []
        
        logger.info(f"Starting autofill pipeline for run {context.run_id}")
        
        try:
            # Execute agents in sequence
            for agent_name in self.execution_order:
                agent = self.agents[agent_name]
                
                logger.info(f"Executing {agent_name} agent")
                agent_start = datetime.utcnow()
                
                result = await agent.run(context)
                
                agent_end = datetime.utcnow()
                execution_time = (agent_end - agent_start).total_seconds()
                
                # Log execution
                execution_log.append({
                    "agent": agent_name,
                    "success": result.success,
                    "execution_time": execution_time,
                    "errors": result.errors,
                    "warnings": result.warnings
                })
                
                results[agent_name] = result
                
                # Update context with agent results
                if result.success and result.data:
                    context.metadata[agent_name] = result.data
                
                # Stop pipeline if agent failed critically
                if not result.success and agent_name in ["planner", "retriever"]:
                    logger.error(f"Critical agent {agent_name} failed, stopping pipeline")
                    break
                
                # Allow agents to specify next agent (for conditional flow)
                if result.next_agent and result.next_agent != self._get_next_agent(agent_name):
                    logger.info(f"Agent {agent_name} requested jump to {result.next_agent}")
                    # Handle conditional flow if needed
                    pass
            
            end_time = datetime.utcnow()
            total_execution_time = (end_time - start_time).total_seconds()
            
            # Calculate pipeline metrics
            pipeline_success = all(
                results.get(agent, AgentResult(success=False)).success 
                for agent in ["planner", "retriever", "mapper", "filler"]
            )
            
            autofill_percentage = self._calculate_autofill_percentage(results)
            
            pipeline_result = {
                "run_id": context.run_id,
                "success": pipeline_success,
                "execution_time": total_execution_time,
                "autofill_percentage": autofill_percentage,
                "agent_results": results,
                "execution_log": execution_log,
                "context": context.dict(),
                "timestamp": start_time.isoformat()
            }
            
            logger.info(
                f"Pipeline completed for run {context.run_id}: "
                f"success={pipeline_success}, "
                f"autofill={autofill_percentage:.1f}%, "
                f"time={total_execution_time:.2f}s"
            )
            
            return pipeline_result
            
        except Exception as e:
            logger.exception(f"Pipeline execution failed for run {context.run_id}")
            return {
                "run_id": context.run_id,
                "success": False,
                "error": str(e),
                "execution_log": execution_log,
                "timestamp": start_time.isoformat()
            }
    
    def _get_next_agent(self, current_agent: str) -> Optional[str]:
        """Get the next agent in the execution order"""
        try:
            current_index = self.execution_order.index(current_agent)
            if current_index < len(self.execution_order) - 1:
                return self.execution_order[current_index + 1]
        except ValueError:
            pass
        return None
    
    def _calculate_autofill_percentage(self, results: Dict[str, AgentResult]) -> float:
        """Calculate the percentage of fields that were successfully auto-filled"""
        planner_result = results.get("planner")
        filler_result = results.get("filler")
        
        if not planner_result or not planner_result.success:
            return 0.0
        
        total_fields = planner_result.data.get("total_fields", 0)
        if total_fields == 0:
            return 0.0
        
        if not filler_result or not filler_result.success:
            return 0.0
        
        filled_fields = filler_result.data.get("filled_fields", 0)
        return (filled_fields / total_fields) * 100.0
    
    async def get_pipeline_status(self, run_id: str) -> Dict[str, Any]:
        """Get the current status of a pipeline execution"""
        # TODO: Implement status tracking for long-running pipelines
        return {
            "run_id": run_id,
            "status": "unknown",
            "message": "Status tracking not yet implemented"
        }
    
    async def cancel_pipeline(self, run_id: str) -> bool:
        """Cancel a running pipeline"""
        # TODO: Implement pipeline cancellation
        logger.warning(f"Pipeline cancellation requested for run {run_id} but not yet implemented")
        return False

