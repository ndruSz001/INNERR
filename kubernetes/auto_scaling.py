"""
Auto-Scaling Manager for TARS Cluster
FASE 17: Cluster Management - Horizontal Pod Autoscaling

Manages automatic scaling based on metrics:
- CPU utilization monitoring
- Memory utilization monitoring
- Request rate monitoring
- Custom metric-based scaling
"""

import os
import json
import logging
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import time

# Initialize logger
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric types for autoscaling"""
    CPU = "cpu"
    MEMORY = "memory"
    REQUESTS_PER_SECOND = "rps"
    CONNECTIONS = "connections"
    CUSTOM = "custom"


@dataclass
class MetricValue:
    """Metric measurement"""
    metric_type: str
    value: float
    timestamp: str
    unit: str


@dataclass
class ScalingPolicy:
    """Auto-scaling policy"""
    metric_type: str
    target_value: float
    scale_up_threshold: float      # When to scale up
    scale_down_threshold: float    # When to scale down
    min_replicas: int
    max_replicas: int
    scale_up_cooldown_secs: int    # Wait before next scale up
    scale_down_cooldown_secs: int  # Wait before next scale down
    metric_aggregation_window_secs: int  # Time window for averaging


@dataclass
class ScalingEvent:
    """Scaling event record"""
    timestamp: str
    action: str  # scale_up, scale_down, check
    from_replicas: int
    to_replicas: int
    reason: str
    metric_value: float


class AutoScaler:
    """Horizontal Pod Autoscaler"""
    
    def __init__(
        self,
        deployment_name: str,
        namespace: str = "tars",
        check_interval_secs: int = 30
    ):
        """
        Initialize autoscaler
        
        Args:
            deployment_name: Target deployment
            namespace: Kubernetes namespace
            check_interval_secs: Metric check interval
        """
        self.deployment_name = deployment_name
        self.namespace = namespace
        self.check_interval_secs = check_interval_secs
        self.policies: List[ScalingPolicy] = []
        self.metrics_history: List[MetricValue] = []
        self.scaling_events: List[ScalingEvent] = []
        self.current_replicas = 1
        self.last_scale_up = None
        self.last_scale_down = None
        self.cluster_manager = None
        
        logger.info(
            f"AutoScaler initialized: deployment={deployment_name}, "
            f"check_interval={check_interval_secs}s"
        )
    
    def add_policy(self, policy: ScalingPolicy) -> bool:
        """Add scaling policy"""
        try:
            self.policies.append(policy)
            logger.info(
                f"Scaling policy added: {policy.metric_type} "
                f"(target={policy.target_value}, "
                f"min={policy.min_replicas}, max={policy.max_replicas})"
            )
            return True
        
        except Exception as e:
            logger.error(f"Failed to add policy: {e}")
            return False
    
    def record_metric(self, metric: MetricValue) -> bool:
        """Record metric value"""
        try:
            self.metrics_history.append(metric)
            
            # Keep only last 100 metrics
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
            return False
    
    def get_average_metric(
        self,
        metric_type: str,
        window_secs: int
    ) -> Optional[float]:
        """Get average metric value in time window"""
        try:
            cutoff_time = (
                datetime.now() - timedelta(seconds=window_secs)
            ).isoformat()
            
            recent_metrics = [
                m.value for m in self.metrics_history
                if m.metric_type == metric_type and m.timestamp > cutoff_time
            ]
            
            if not recent_metrics:
                return None
            
            return sum(recent_metrics) / len(recent_metrics)
        
        except Exception as e:
            logger.error(f"Failed to get average metric: {e}")
            return None
    
    def evaluate_policies(self) -> Optional[int]:
        """
        Evaluate all policies and determine desired replica count
        
        Returns:
            Desired number of replicas or None
        """
        try:
            desired_replicas = self.current_replicas
            
            for policy in self.policies:
                # Get average metric for policy window
                avg_metric = self.get_average_metric(
                    policy.metric_type,
                    policy.metric_aggregation_window_secs
                )
                
                if avg_metric is None:
                    logger.debug(
                        f"No metrics available for {policy.metric_type}"
                    )
                    continue
                
                # Determine scaling action
                if avg_metric >= policy.scale_up_threshold:
                    # Scale up
                    scale_factor = avg_metric / policy.target_value
                    new_replicas = int(
                        self.current_replicas * scale_factor
                    )
                    desired_replicas = max(desired_replicas, new_replicas)
                
                elif avg_metric <= policy.scale_down_threshold:
                    # Scale down
                    scale_factor = avg_metric / policy.target_value
                    new_replicas = max(
                        int(self.current_replicas * scale_factor),
                        policy.min_replicas
                    )
                    desired_replicas = min(desired_replicas, new_replicas)
                
                # Apply constraints
                desired_replicas = max(
                    desired_replicas,
                    policy.min_replicas
                )
                desired_replicas = min(
                    desired_replicas,
                    policy.max_replicas
                )
            
            return desired_replicas
        
        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")
            return None
    
    def scale(self, desired_replicas: int, reason: str) -> bool:
        """Scale deployment to desired replicas"""
        try:
            if not self.cluster_manager:
                logger.warning("Cluster manager not available")
                return False
            
            # Check cooldown periods
            now = datetime.now()
            
            if desired_replicas > self.current_replicas:
                # Scale up
                if self.last_scale_up:
                    policy = next(
                        (p for p in self.policies),
                        None
                    )
                    cooldown = (
                        policy.scale_up_cooldown_secs
                        if policy else 60
                    )
                    
                    if (now - self.last_scale_up).total_seconds() < cooldown:
                        logger.info(
                            "Scale up in cooldown period, skipping"
                        )
                        return False
                
                # Perform scale up
                if self.cluster_manager.scale_deployment(
                    self.deployment_name,
                    desired_replicas
                ):
                    self.current_replicas = desired_replicas
                    self.last_scale_up = now
                    
                    event = ScalingEvent(
                        timestamp=now.isoformat(),
                        action="scale_up",
                        from_replicas=self.current_replicas - desired_replicas,
                        to_replicas=desired_replicas,
                        reason=reason,
                        metric_value=0.0
                    )
                    self.scaling_events.append(event)
                    
                    logger.info(
                        f"Scaled up: {self.current_replicas} → "
                        f"{desired_replicas} ({reason})"
                    )
                    return True
            
            elif desired_replicas < self.current_replicas:
                # Scale down
                if self.last_scale_down:
                    policy = next(
                        (p for p in self.policies),
                        None
                    )
                    cooldown = (
                        policy.scale_down_cooldown_secs
                        if policy else 300  # Longer cooldown for scale down
                    )
                    
                    if (now - self.last_scale_down).total_seconds() < cooldown:
                        logger.info(
                            "Scale down in cooldown period, skipping"
                        )
                        return False
                
                # Perform scale down
                if self.cluster_manager.scale_deployment(
                    self.deployment_name,
                    desired_replicas
                ):
                    self.current_replicas = desired_replicas
                    self.last_scale_down = now
                    
                    event = ScalingEvent(
                        timestamp=now.isoformat(),
                        action="scale_down",
                        from_replicas=self.current_replicas + desired_replicas,
                        to_replicas=desired_replicas,
                        reason=reason,
                        metric_value=0.0
                    )
                    self.scaling_events.append(event)
                    
                    logger.info(
                        f"Scaled down: {self.current_replicas + desired_replicas} → "
                        f"{desired_replicas} ({reason})"
                    )
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"Scaling failed: {e}")
            return False
    
    def check_and_scale(self) -> bool:
        """Check metrics and scale if needed"""
        try:
            desired_replicas = self.evaluate_policies()
            
            if desired_replicas is None:
                logger.debug("No scaling decision made")
                return False
            
            if desired_replicas != self.current_replicas:
                # Determine reason
                reason = f"Target: {desired_replicas} replicas"
                self.scale(desired_replicas, reason)
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Check and scale failed: {e}")
            return False
    
    def get_scaling_history(
        self,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent scaling events"""
        events = self.scaling_events[-limit:]
        return [asdict(e) for e in events]
    
    def get_status(self) -> Dict[str, Any]:
        """Get autoscaler status"""
        return {
            "deployment": self.deployment_name,
            "current_replicas": self.current_replicas,
            "policies": len(self.policies),
            "scaling_events": len(self.scaling_events),
            "last_scale_up": (
                self.last_scale_up.isoformat()
                if self.last_scale_up else None
            ),
            "last_scale_down": (
                self.last_scale_down.isoformat()
                if self.last_scale_down else None
            ),
            "metrics_recorded": len(self.metrics_history)
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize autoscaler
    autoscaler = AutoScaler(
        deployment_name="tars-backend",
        namespace="tars"
    )
    
    # Add scaling policies
    cpu_policy = ScalingPolicy(
        metric_type="cpu",
        target_value=60.0,
        scale_up_threshold=80.0,
        scale_down_threshold=30.0,
        min_replicas=2,
        max_replicas=10,
        scale_up_cooldown_secs=60,
        scale_down_cooldown_secs=300,
        metric_aggregation_window_secs=60
    )
    autoscaler.add_policy(cpu_policy)
    
    # Example: Record metrics and check scaling
    # metric = MetricValue(
    #     metric_type="cpu",
    #     value=75.5,
    #     timestamp=datetime.now().isoformat(),
    #     unit="%"
    # )
    # autoscaler.record_metric(metric)
    # autoscaler.check_and_scale()
