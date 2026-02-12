"""
Kubernetes Cluster Manager
FASE 17: Cluster Management - Pod orchestration and monitoring

Manages TARS pods in Kubernetes cluster:
- Pod health monitoring
- Rolling updates
- Replica scaling
- Pod coordination across nodes
"""

import os
import json
import logging
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio

# Initialize logger
logger = logging.getLogger(__name__)


@dataclass
class PodInfo:
    """Kubernetes Pod information"""
    name: str
    namespace: str
    status: str  # Running, Pending, Failed, Succeeded, Unknown
    phase: str
    ready: bool
    restarts: int
    node: str
    ip: str
    cpu_usage: str
    memory_usage: str
    created_at: str
    last_transition: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ClusterInfo:
    """Kubernetes Cluster information"""
    name: str
    version: str
    nodes_count: int
    pods_running: int
    pods_pending: int
    pods_failed: int
    cpu_capacity: str
    memory_capacity: str
    storage_capacity: str
    cpu_allocated: str
    memory_allocated: str
    timestamp: str


class ClusterManager:
    """Kubernetes cluster management"""
    
    def __init__(
        self,
        namespace: str = "tars",
        context: Optional[str] = None,
        config_path: Optional[str] = None
    ):
        """
        Initialize cluster manager
        
        Args:
            namespace: Kubernetes namespace
            context: kubeconfig context
            config_path: kubeconfig file path
        """
        self.namespace = namespace
        self.context = context
        self.config_path = config_path or os.path.expanduser("~/.kube/config")
        self.client = None
        self.api = None
        
        self._init_kubernetes()
        
        logger.info(
            f"ClusterManager initialized: namespace={namespace}, "
            f"context={context}"
        )
    
    def _init_kubernetes(self):
        """Initialize Kubernetes client"""
        try:
            from kubernetes import client, config
            
            # Load config
            if self.context:
                config.load_kube_config(
                    config_file=self.config_path,
                    context=self.context
                )
            else:
                config.load_kube_config(config_file=self.config_path)
            
            self.client = client.CoreV1Api()
            self.api = client.AppsV1Api()
            
            logger.info("Kubernetes client initialized successfully")
        
        except ImportError:
            logger.error("kubernetes-client not installed. Install with: pip install kubernetes")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            raise
    
    def get_pod_info(self, pod_name: str) -> Optional[PodInfo]:
        """Get information about a specific pod"""
        try:
            pod = self.client.read_namespaced_pod(pod_name, self.namespace)
            
            # Extract pod info
            status = pod.status
            conditions = {c.type: c.status for c in status.conditions or []}
            
            # Get resource usage (requires metrics API)
            cpu_usage = "N/A"
            memory_usage = "N/A"
            
            return PodInfo(
                name=pod.metadata.name,
                namespace=pod.metadata.namespace,
                status=status.phase,
                phase=status.phase,
                ready=conditions.get("Ready", "Unknown") == "True",
                restarts=pod.status.container_statuses[0].restart_count if pod.status.container_statuses else 0,
                node=pod.spec.node_name or "Unscheduled",
                ip=status.pod_ip or "Pending",
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                created_at=pod.metadata.creation_timestamp.isoformat(),
                last_transition=conditions.get("LastTransition", "Unknown")
            )
        
        except Exception as e:
            logger.error(f"Failed to get pod info for {pod_name}: {e}")
            return None
    
    def list_pods(self, label_selector: Optional[str] = None) -> List[PodInfo]:
        """List all pods in namespace"""
        try:
            pods = self.client.list_namespaced_pod(
                self.namespace,
                label_selector=label_selector
            )
            
            pod_infos = []
            for pod in pods.items:
                info = self.get_pod_info(pod.metadata.name)
                if info:
                    pod_infos.append(info)
            
            return pod_infos
        
        except Exception as e:
            logger.error(f"Failed to list pods: {e}")
            return []
    
    def scale_deployment(self, deployment_name: str, replicas: int) -> bool:
        """Scale deployment to desired replica count"""
        try:
            # Get current deployment
            deployment = self.api.read_namespaced_deployment(
                deployment_name,
                self.namespace
            )
            
            # Update replicas
            deployment.spec.replicas = replicas
            
            # Patch deployment
            self.api.patch_namespaced_deployment(
                deployment_name,
                self.namespace,
                deployment
            )
            
            logger.info(
                f"Deployment {deployment_name} scaled to {replicas} replicas"
            )
            return True
        
        except Exception as e:
            logger.error(f"Failed to scale deployment: {e}")
            return False
    
    def get_deployment_status(self, deployment_name: str) -> Dict[str, Any]:
        """Get deployment status"""
        try:
            deployment = self.api.read_namespaced_deployment(
                deployment_name,
                self.namespace
            )
            
            status = deployment.status
            
            return {
                "name": deployment.metadata.name,
                "desired_replicas": deployment.spec.replicas,
                "ready_replicas": status.ready_replicas or 0,
                "updated_replicas": status.updated_replicas or 0,
                "available_replicas": status.available_replicas or 0,
                "unavailable_replicas": status.unavailable_replicas or 0,
                "updated_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to get deployment status: {e}")
            return {}
    
    def rollout_status(self, deployment_name: str) -> Dict[str, Any]:
        """Check rollout status"""
        try:
            status = self.get_deployment_status(deployment_name)
            
            desired = status.get("desired_replicas", 0)
            ready = status.get("ready_replicas", 0)
            updated = status.get("updated_replicas", 0)
            
            # Determine rollout state
            if desired == 0:
                rollout_state = "Scaled down"
            elif updated == desired and ready == desired:
                rollout_state = "Complete"
            elif ready < desired:
                rollout_state = "In progress"
            else:
                rollout_state = "Unknown"
            
            return {
                **status,
                "rollout_state": rollout_state,
                "progress": f"{ready}/{desired}" if desired > 0 else "0/0"
            }
        
        except Exception as e:
            logger.error(f"Failed to check rollout status: {e}")
            return {}
    
    def get_cluster_info(self) -> ClusterInfo:
        """Get cluster information"""
        try:
            # List all nodes
            nodes = self.client.list_node()
            
            # Count pods by status
            pods = self.client.list_namespaced_pod(self.namespace)
            
            status_counts = {
                "Running": 0,
                "Pending": 0,
                "Failed": 0,
                "Succeeded": 0
            }
            
            for pod in pods.items:
                phase = pod.status.phase
                status_counts[phase] = status_counts.get(phase, 0) + 1
            
            # Calculate resources
            cpu_capacity = sum(
                int(node.status.capacity.get("cpu", "0").replace("m", "") or 0)
                for node in nodes.items
            )
            memory_capacity = sum(
                self._parse_memory(node.status.capacity.get("memory", "0"))
                for node in nodes.items
            )
            
            return ClusterInfo(
                name=self.context or "default",
                version="1.25+",  # Would need to query API
                nodes_count=len(nodes.items),
                pods_running=status_counts["Running"],
                pods_pending=status_counts["Pending"],
                pods_failed=status_counts["Failed"],
                cpu_capacity=f"{cpu_capacity}m",
                memory_capacity=f"{memory_capacity}Mi",
                storage_capacity="N/A",
                cpu_allocated="N/A",
                memory_allocated="N/A",
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            logger.error(f"Failed to get cluster info: {e}")
            return None
    
    def restart_pod(self, pod_name: str) -> bool:
        """Restart a pod by deleting it (ReplicaSet will recreate)"""
        try:
            self.client.delete_namespaced_pod(
                pod_name,
                self.namespace,
                grace_period_seconds=30
            )
            
            logger.info(f"Pod {pod_name} marked for deletion (will restart)")
            return True
        
        except Exception as e:
            logger.error(f"Failed to restart pod: {e}")
            return False
    
    def monitor_pod_logs(
        self,
        pod_name: str,
        follow: bool = True,
        lines: int = 100
    ) -> str:
        """Get pod logs"""
        try:
            logs = self.client.read_namespaced_pod_log(
                pod_name,
                self.namespace,
                tail_lines=lines
            )
            
            return logs
        
        except Exception as e:
            logger.error(f"Failed to get pod logs: {e}")
            return ""
    
    def execute_in_pod(
        self,
        pod_name: str,
        command: List[str],
        container: Optional[str] = None
    ) -> str:
        """Execute command in pod (requires stream module)"""
        try:
            from kubernetes.stream import stream
            
            exec_command = [
                "/bin/sh",
                "-c",
                " ".join(command)
            ]
            
            resp = stream(
                self.client.connect_get_namespaced_pod_exec,
                pod_name,
                self.namespace,
                command=exec_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False
            )
            
            return resp
        
        except Exception as e:
            logger.error(f"Failed to execute in pod: {e}")
            return ""
    
    def get_node_info(self) -> List[Dict[str, Any]]:
        """Get information about all nodes"""
        try:
            nodes = self.client.list_node()
            
            node_infos = []
            for node in nodes.items:
                status = node.status
                
                node_info = {
                    "name": node.metadata.name,
                    "status": "Ready" if any(
                        c.type == "Ready" and c.status == "True"
                        for c in status.conditions or []
                    ) else "NotReady",
                    "cpu_capacity": status.capacity.get("cpu", "N/A"),
                    "memory_capacity": status.capacity.get("memory", "N/A"),
                    "pod_capacity": status.capacity.get("pods", "N/A"),
                    "allocated_cpu": status.allocatable.get("cpu", "N/A"),
                    "allocated_memory": status.allocatable.get("memory", "N/A"),
                    "kernel_version": status.node_info.kernel_version,
                    "container_runtime": status.node_info.container_runtime_version
                }
                
                node_infos.append(node_info)
            
            return node_infos
        
        except Exception as e:
            logger.error(f"Failed to get node info: {e}")
            return []
    
    @staticmethod
    def _parse_memory(mem_string: str) -> int:
        """Parse memory string to Mi"""
        if "Gi" in mem_string:
            return int(mem_string.replace("Gi", "")) * 1024
        elif "Mi" in mem_string:
            return int(mem_string.replace("Mi", ""))
        else:
            return 0


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize manager
    manager = ClusterManager(namespace="tars")
    
    # Get cluster info
    # cluster_info = manager.get_cluster_info()
    # print(f"Cluster: {cluster_info.name}, Nodes: {cluster_info.nodes_count}")
    
    # List pods
    # pods = manager.list_pods(label_selector="app=tars")
    # for pod in pods:
    #     print(f"Pod: {pod.name}, Status: {pod.status}")
    
    # Scale deployment
    # manager.scale_deployment("tars-backend", replicas=5)
