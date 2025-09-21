"""
Metrics service for RealVibe Site Copilot.
Handles KPI tracking, analytics, and dashboard metrics.
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import statistics

from supabase import create_client, Client
from app.core.config import settings


class MetricType(Enum):
    """Types of metrics tracked."""
    AUTOFILL_RATE = "autofill_rate"
    REVIEW_TIME = "review_time"
    CYCLE_TIME_SAVED = "cycle_time_saved"
    COMPLETION_RATE = "completion_rate"
    ERROR_RATE = "error_rate"
    USER_SATISFACTION = "user_satisfaction"


class TimeRange(Enum):
    """Time ranges for metrics aggregation."""
    LAST_24H = "last_24h"
    LAST_7D = "last_7d"
    LAST_30D = "last_30d"
    LAST_90D = "last_90d"
    LAST_YEAR = "last_year"
    ALL_TIME = "all_time"


class MetricsService:
    """Service for tracking and analyzing performance metrics."""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    async def track_run_metrics(
        self,
        run_id: str,
        site_id: str,
        questionnaire_name: str,
        sponsor: str,
        total_fields: int,
        autofilled_fields: int,
        review_time_minutes: Optional[int] = None,
        completion_time: Optional[datetime] = None
    ) -> bool:
        """
        Track metrics for a questionnaire run.
        
        Args:
            run_id: Unique run identifier
            site_id: Site identifier
            questionnaire_name: Name of questionnaire
            sponsor: Sponsor name
            total_fields: Total number of fields
            autofilled_fields: Number of successfully autofilled fields
            review_time_minutes: Time spent on review
            completion_time: When the run was completed
            
        Returns:
            True if metrics were tracked successfully
        """
        try:
            # Calculate autofill rate
            autofill_rate = (autofilled_fields / total_fields * 100) if total_fields > 0 else 0
            
            # Estimate cycle time saved (based on historical data)
            estimated_manual_time = total_fields * 15  # 15 minutes per field manually
            actual_time = review_time_minutes or 0
            time_saved_minutes = max(0, estimated_manual_time - actual_time)
            cycle_time_saved_weeks = time_saved_minutes / (60 * 40)  # Convert to weeks (40 hours/week)
            
            # Create metrics record
            metrics_data = {
                "run_id": run_id,
                "site_id": site_id,
                "questionnaire_name": questionnaire_name,
                "sponsor": sponsor,
                "total_fields": total_fields,
                "autofilled_fields": autofilled_fields,
                "autofill_rate": round(autofill_rate, 2),
                "review_time_minutes": review_time_minutes,
                "cycle_time_saved_weeks": round(cycle_time_saved_weeks, 2),
                "completion_time": completion_time.isoformat() if completion_time else datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in database
            result = self.supabase.table("run_metrics").insert(metrics_data).execute()
            
            if result.data:
                # Update aggregated metrics
                await self._update_aggregated_metrics(site_id)
                return True
            
            return False
            
        except Exception as e:
            print(f"Failed to track run metrics: {e}")
            return False
    
    async def get_dashboard_metrics(
        self,
        site_id: str,
        time_range: TimeRange = TimeRange.LAST_30D
    ) -> Dict[str, Any]:
        """
        Get dashboard metrics for a site.
        
        Args:
            site_id: Site identifier
            time_range: Time range for metrics
            
        Returns:
            Dictionary containing dashboard metrics
        """
        try:
            # Get time range filter
            start_date = self._get_start_date(time_range)
            
            # Get run metrics
            query = self.supabase.table("run_metrics").select("*").eq("site_id", site_id)
            
            if start_date:
                query = query.gte("completion_time", start_date.isoformat())
            
            result = query.execute()
            runs_data = result.data or []
            
            if not runs_data:
                return self._get_empty_metrics()
            
            # Calculate key metrics
            total_runs = len(runs_data)
            completed_runs = len([r for r in runs_data if r.get("review_time_minutes") is not None])
            
            # Autofill rate
            autofill_rates = [r["autofill_rate"] for r in runs_data if r.get("autofill_rate") is not None]
            avg_autofill_rate = statistics.mean(autofill_rates) if autofill_rates else 0
            
            # Review time
            review_times = [r["review_time_minutes"] for r in runs_data if r.get("review_time_minutes") is not None]
            avg_review_time = statistics.mean(review_times) if review_times else 0
            
            # Cycle time saved
            time_saved = [r["cycle_time_saved_weeks"] for r in runs_data if r.get("cycle_time_saved_weeks") is not None]
            total_time_saved = sum(time_saved) if time_saved else 0
            
            # Completion rate
            completion_rate = (completed_runs / total_runs * 100) if total_runs > 0 else 0
            
            # Recent activity
            recent_runs = sorted(runs_data, key=lambda x: x["completion_time"], reverse=True)[:5]
            
            # Trend data (last 7 days)
            trend_data = await self._get_trend_data(site_id, 7)
            
            return {
                "summary": {
                    "autofill_rate": round(avg_autofill_rate, 1),
                    "avg_review_time": round(avg_review_time, 1),
                    "total_time_saved": round(total_time_saved, 1),
                    "completion_rate": round(completion_rate, 1),
                    "total_runs": total_runs,
                    "completed_runs": completed_runs
                },
                "trends": trend_data,
                "recent_activity": [
                    {
                        "run_id": run["run_id"],
                        "questionnaire_name": run["questionnaire_name"],
                        "sponsor": run["sponsor"],
                        "autofill_rate": run["autofill_rate"],
                        "review_time": run.get("review_time_minutes"),
                        "completion_time": run["completion_time"]
                    }
                    for run in recent_runs
                ],
                "time_range": time_range.value,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Failed to get dashboard metrics: {e}")
            return self._get_empty_metrics()
    
    async def get_detailed_analytics(
        self,
        site_id: str,
        time_range: TimeRange = TimeRange.LAST_30D
    ) -> Dict[str, Any]:
        """
        Get detailed analytics for a site.
        
        Args:
            site_id: Site identifier
            time_range: Time range for analytics
            
        Returns:
            Dictionary containing detailed analytics
        """
        try:
            start_date = self._get_start_date(time_range)
            
            # Get run metrics
            query = self.supabase.table("run_metrics").select("*").eq("site_id", site_id)
            if start_date:
                query = query.gte("completion_time", start_date.isoformat())
            
            result = query.execute()
            runs_data = result.data or []
            
            if not runs_data:
                return {"message": "No data available for the selected time range"}
            
            # Performance by sponsor
            sponsor_metrics = {}
            for run in runs_data:
                sponsor = run.get("sponsor", "Unknown")
                if sponsor not in sponsor_metrics:
                    sponsor_metrics[sponsor] = {
                        "runs": 0,
                        "autofill_rates": [],
                        "review_times": []
                    }
                
                sponsor_metrics[sponsor]["runs"] += 1
                if run.get("autofill_rate") is not None:
                    sponsor_metrics[sponsor]["autofill_rates"].append(run["autofill_rate"])
                if run.get("review_time_minutes") is not None:
                    sponsor_metrics[sponsor]["review_times"].append(run["review_time_minutes"])
            
            # Calculate sponsor averages
            sponsor_performance = []
            for sponsor, data in sponsor_metrics.items():
                avg_autofill = statistics.mean(data["autofill_rates"]) if data["autofill_rates"] else 0
                avg_review_time = statistics.mean(data["review_times"]) if data["review_times"] else 0
                
                sponsor_performance.append({
                    "sponsor": sponsor,
                    "runs": data["runs"],
                    "avg_autofill_rate": round(avg_autofill, 1),
                    "avg_review_time": round(avg_review_time, 1)
                })
            
            # Performance distribution
            autofill_rates = [r["autofill_rate"] for r in runs_data if r.get("autofill_rate") is not None]
            review_times = [r["review_time_minutes"] for r in runs_data if r.get("review_time_minutes") is not None]
            
            # Distribution buckets
            autofill_distribution = self._calculate_distribution(autofill_rates, [0, 50, 70, 85, 95, 100])
            review_time_distribution = self._calculate_distribution(review_times, [0, 5, 10, 15, 20, 30])
            
            # Monthly trends
            monthly_trends = await self._get_monthly_trends(site_id, 12)
            
            return {
                "sponsor_performance": sorted(sponsor_performance, key=lambda x: x["avg_autofill_rate"], reverse=True),
                "distributions": {
                    "autofill_rate": autofill_distribution,
                    "review_time": review_time_distribution
                },
                "monthly_trends": monthly_trends,
                "statistics": {
                    "total_runs": len(runs_data),
                    "autofill_rate": {
                        "mean": round(statistics.mean(autofill_rates), 1) if autofill_rates else 0,
                        "median": round(statistics.median(autofill_rates), 1) if autofill_rates else 0,
                        "std_dev": round(statistics.stdev(autofill_rates), 1) if len(autofill_rates) > 1 else 0
                    },
                    "review_time": {
                        "mean": round(statistics.mean(review_times), 1) if review_times else 0,
                        "median": round(statistics.median(review_times), 1) if review_times else 0,
                        "std_dev": round(statistics.stdev(review_times), 1) if len(review_times) > 1 else 0
                    }
                }
            }
            
        except Exception as e:
            print(f"Failed to get detailed analytics: {e}")
            return {"error": str(e)}
    
    async def get_performance_benchmarks(self, site_id: str) -> Dict[str, Any]:
        """
        Get performance benchmarks and targets.
        
        Args:
            site_id: Site identifier
            
        Returns:
            Dictionary containing benchmarks and current performance
        """
        try:
            # Get recent performance (last 30 days)
            current_metrics = await self.get_dashboard_metrics(site_id, TimeRange.LAST_30D)
            
            # Industry benchmarks (these would typically come from a benchmarks database)
            benchmarks = {
                "autofill_rate": {
                    "excellent": 85.0,
                    "good": 70.0,
                    "acceptable": 50.0,
                    "current": current_metrics["summary"]["autofill_rate"]
                },
                "review_time": {
                    "excellent": 10.0,  # minutes
                    "good": 15.0,
                    "acceptable": 25.0,
                    "current": current_metrics["summary"]["avg_review_time"]
                },
                "completion_rate": {
                    "excellent": 95.0,
                    "good": 85.0,
                    "acceptable": 70.0,
                    "current": current_metrics["summary"]["completion_rate"]
                }
            }
            
            # Calculate performance scores
            scores = {}
            for metric, values in benchmarks.items():
                current = values["current"]
                
                if metric == "review_time":
                    # Lower is better for review time
                    if current <= values["excellent"]:
                        score = "excellent"
                    elif current <= values["good"]:
                        score = "good"
                    elif current <= values["acceptable"]:
                        score = "acceptable"
                    else:
                        score = "needs_improvement"
                else:
                    # Higher is better for other metrics
                    if current >= values["excellent"]:
                        score = "excellent"
                    elif current >= values["good"]:
                        score = "good"
                    elif current >= values["acceptable"]:
                        score = "acceptable"
                    else:
                        score = "needs_improvement"
                
                scores[metric] = score
            
            return {
                "benchmarks": benchmarks,
                "scores": scores,
                "overall_score": self._calculate_overall_score(scores),
                "recommendations": self._get_recommendations(scores, benchmarks)
            }
            
        except Exception as e:
            print(f"Failed to get performance benchmarks: {e}")
            return {"error": str(e)}
    
    def _get_start_date(self, time_range: TimeRange) -> Optional[datetime]:
        """Get start date for time range filter."""
        now = datetime.utcnow()
        
        if time_range == TimeRange.LAST_24H:
            return now - timedelta(hours=24)
        elif time_range == TimeRange.LAST_7D:
            return now - timedelta(days=7)
        elif time_range == TimeRange.LAST_30D:
            return now - timedelta(days=30)
        elif time_range == TimeRange.LAST_90D:
            return now - timedelta(days=90)
        elif time_range == TimeRange.LAST_YEAR:
            return now - timedelta(days=365)
        else:  # ALL_TIME
            return None
    
    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure."""
        return {
            "summary": {
                "autofill_rate": 0.0,
                "avg_review_time": 0.0,
                "total_time_saved": 0.0,
                "completion_rate": 0.0,
                "total_runs": 0,
                "completed_runs": 0
            },
            "trends": [],
            "recent_activity": [],
            "time_range": "last_30d",
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _get_trend_data(self, site_id: str, days: int) -> List[Dict[str, Any]]:
        """Get trend data for the last N days."""
        try:
            trends = []
            for i in range(days):
                date = datetime.utcnow() - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                
                # Mock trend data for demo
                trends.append({
                    "date": date_str,
                    "autofill_rate": 70 + (i * 2) + (i % 3),  # Simulated trend
                    "review_time": 15 - (i * 0.5),
                    "runs": max(1, 5 - i)
                })
            
            return list(reversed(trends))
            
        except Exception:
            return []
    
    async def _get_monthly_trends(self, site_id: str, months: int) -> List[Dict[str, Any]]:
        """Get monthly trend data."""
        try:
            trends = []
            for i in range(months):
                date = datetime.utcnow() - timedelta(days=i*30)
                month_str = date.strftime("%Y-%m")
                
                # Mock monthly data for demo
                trends.append({
                    "month": month_str,
                    "runs": max(10, 25 - i*2),
                    "avg_autofill_rate": 65 + (i % 4) * 5,
                    "avg_review_time": 12 + (i % 3) * 2,
                    "total_time_saved": max(1, 5 - i*0.5)
                })
            
            return list(reversed(trends))
            
        except Exception:
            return []
    
    def _calculate_distribution(self, values: List[float], buckets: List[float]) -> List[Dict[str, Any]]:
        """Calculate distribution of values into buckets."""
        if not values:
            return []
        
        distribution = []
        for i in range(len(buckets) - 1):
            min_val = buckets[i]
            max_val = buckets[i + 1]
            count = len([v for v in values if min_val <= v < max_val])
            percentage = (count / len(values)) * 100
            
            distribution.append({
                "range": f"{min_val}-{max_val}",
                "count": count,
                "percentage": round(percentage, 1)
            })
        
        return distribution
    
    def _calculate_overall_score(self, scores: Dict[str, str]) -> str:
        """Calculate overall performance score."""
        score_values = {"excellent": 4, "good": 3, "acceptable": 2, "needs_improvement": 1}
        
        total_score = sum(score_values.get(score, 1) for score in scores.values())
        avg_score = total_score / len(scores)
        
        if avg_score >= 3.5:
            return "excellent"
        elif avg_score >= 2.5:
            return "good"
        elif avg_score >= 1.5:
            return "acceptable"
        else:
            return "needs_improvement"
    
    def _get_recommendations(self, scores: Dict[str, str], benchmarks: Dict[str, Any]) -> List[str]:
        """Get performance improvement recommendations."""
        recommendations = []
        
        if scores.get("autofill_rate") in ["acceptable", "needs_improvement"]:
            recommendations.append("Consider uploading more comprehensive site documentation to improve autofill accuracy")
        
        if scores.get("review_time") in ["acceptable", "needs_improvement"]:
            recommendations.append("Provide reviewer training to reduce review time and improve efficiency")
        
        if scores.get("completion_rate") in ["acceptable", "needs_improvement"]:
            recommendations.append("Investigate common causes of incomplete questionnaires and address workflow issues")
        
        if not recommendations:
            recommendations.append("Excellent performance! Continue current practices and consider sharing best practices with other sites")
        
        return recommendations
    
    async def _update_aggregated_metrics(self, site_id: str):
        """Update aggregated metrics for a site."""
        try:
            # This would update aggregated metrics tables for faster dashboard queries
            # For now, we'll skip this implementation
            pass
        except Exception as e:
            print(f"Failed to update aggregated metrics: {e}")

