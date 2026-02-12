"""
Load Balancer for TARS Cluster
FASE 17: Cluster Management - Traffic distribution and load balancing

Manages traffic distribution across multiple backend replicas:
- Round-robin load balancing
- Health-aware routing
- Weighted distribution
- Connection pooling
"""

import os
import json
import logging
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, timedelta
import random
import time

# Initialize logger
logger = logging.getLogger(__name__)


class BalanceStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round-robin"      # Rotate through backends
    LEAST_CONN = "least-connections"  # Route to least busy
    WEIGHTED = "weighted"             # Based on weights
    RANDOM = "random"                # Random selection
    IP_HASH = "ip-hash"              # Sticky sessions


@dataclass
class BackendNode:
    """Backend node information"""
    name: str
    host: str
    port: int
    weight: int = 1
    status: str = "healthy"  # healthy, degraded, unhealthy
    connections: int = 0
    requests_served: int = 0
    last_checked: str = None
    response_time_ms: float = 0.0
    error_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def is_healthy(self) -> bool:
        """Check if node is healthy"""
        return self.status == "healthy"
    
    def load_score(self) -> float:
        """Calculate node load score"""
        # Higher score = more loaded
        conn_score = self.connections * 0.7
        response_score = self.response_time_ms * 0.2
        error_score = self.error_rate * 10.0
        
        return conn_score + response_score + error_score


class LoadBalancer:
    """Load balancer for TARS cluster"""
    
    def __init__(
        self,
        strategy: str = "round-robin",
        health_check_interval: int = 30,
        max_connections: int = 1000
    ):
        """
        Initialize load balancer
        
        Args:
            strategy: Load balancing strategy
            health_check_interval: Health check interval in seconds
            max_connections: Max connections per backend
        """
        self.strategy = strategy
        self.health_check_interval = health_check_interval
        self.max_connections = max_connections
        self.backends: List[BackendNode] = []
        self.current_index = 0
        self.last_health_check = None
        self.session_affinity: Dict[str, str] = {}  # IP -> backend mapping
        
        logger.info(
            f"LoadBalancer initialized: strategy={strategy}, "
            f"health_check_interval={health_check_interval}s"
        )
    
    def add_backend(
        self,
        name: str,
        host: str,
        port: int,
        weight: int = 1
    ) -> bool:
        """Add backend node"""
        try:
            backend = BackendNode(
                name=name,
                host=host,
                port=port,
                weight=weight
            )
            self.backends.append(backend)
            
            logger.info(
                f"Backend added: {name} ({host}:{port}, weight={weight})"
            )
            return True
        
        except Exception as e:
            logger.error(f"Failed to add backend: {e}")
            return False
    
    def remove_backend(self, name: str) -> bool:
        """Remove backend node"""
        try:
            self.backends = [b for b in self.backends if b.name != name]
            logger.info(f"Backend removed: {name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to remove backend: {e}")
            return False
    
    def select_backend(self, client_ip: Optional[str] = None) -> Optional[BackendNode]:
        """
        Select backend node based on strategy
        
        Args:
            client_ip: Client IP (for sticky sessions)
        
        Returns:
            Selected backend node or None
        """
        # Filter healthy backends
        healthy = [b for b in self.backends if b.is_healthy()]
        
        if not healthy:
            logger.warning("No healthy backends available")
            return None
        
        if self.strategy == "round-robin":
            backend = self._select_round_robin(healthy)
        
        elif self.strategy == "least-connections":
            backend = self._select_least_conn(healthy)
        
        elif self.strategy == "weighted":
            backend = self._select_weighted(healthy)
        
        elif self.strategy == "random":
            backend = self._select_random(healthy)
        
        elif self.strategy == "ip-hash":
            backend = self._select_ip_hash(healthy, client_ip)
        
        else:
            backend = random.choice(healthy)
        
        if backend:
            logger.debug(f"Backend selected: {backend.name}")
        
        return backend
    
    def _select_round_robin(self, backends: List[BackendNode]) -> BackendNode:
        """Round-robin selection"""
        backend = backends[self.current_index % len(backends)]
        self.current_index += 1
        return backend
    
    def _select_least_conn(self, backends: List[BackendNode]) -> BackendNode:
        """Select backend with least connections"""
        return min(backends, key=lambda b: b.connections)
    
    def _select_weighted(self, backends: List[BackendNode]) -> BackendNode:
        """Weighted round-robin"""
        # Create weighted list
        weighted_backends = []
        for backend in backends:
            weighted_backends.extend([backend] * backend.weight)
        
        return random.choice(weighted_backends)
    
    def _select_random(self, backends: List[BackendNode]) -> BackendNode:
        """Random selection"""
        return random.choice(backends)
    
    def _select_ip_hash(
        self,
        backends: List[BackendNode],
        client_ip: Optional[str]
    ) -> BackendNode:
        """IP hash for sticky sessions"""
        if not client_ip:
            return random.choice(backends)
        
        # Check if already assigned
        if client_ip in self.session_affinity:
            backend_name = self.session_affinity[client_ip]
            backend = next((b for b in backends if b.name == backend_name), None)
            if backend:
                return backend
        
        # Hash IP to backend
        hash_value = hash(client_ip) % len(backends)
        backend = backends[hash_value]
        
        # Store affinity
        self.session_affinity[client_ip] = backend.name
        
        return backend
    
    def record_request(
        self,
        backend: BackendNode,
        response_time_ms: float,
        success: bool
    ):
        """Record request statistics"""
        try:
            backend.requests_served += 1
            backend.response_time_ms = (
                0.7 * backend.response_time_ms + 0.3 * response_time_ms
            )
            
            if not success:
                backend.error_rate = min(
                    backend.error_rate + 0.01,
                    1.0
                )
            else:
                backend.error_rate = max(
                    backend.error_rate - 0.001,
                    0.0
                )
        
        except Exception as e:
            logger.error(f"Failed to record request: {e}")
    
    def health_check(self) -> Dict[str, str]:
        """Perform health checks on all backends"""
        try:
            import socket
            
            results = {}
            
            for backend in self.backends:
                try:
                    # TCP connection test
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    
                    result = sock.connect_ex((backend.host, backend.port))
                    sock.close()
                    
                    if result == 0:
                        backend.status = "healthy"
                        results[backend.name] = "healthy"
                    else:
                        backend.status = "unhealthy"
                        results[backend.name] = "unhealthy"
                
                except socket.timeout:
                    backend.status = "degraded"
                    results[backend.name] = "degraded"
                
                except Exception as e:
                    backend.status = "unhealthy"
                    results[backend.name] = "unhealthy"
                    logger.warning(f"Health check failed for {backend.name}: {e}")
            
            self.last_health_check = datetime.now().isoformat()
            
            logger.info(f"Health check completed: {results}")
            return results
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {}
    
    def update_backend_status(self, name: str, status: str) -> bool:
        """Manually update backend status"""
        try:
            backend = next((b for b in self.backends if b.name == name), None)
            if backend:
                backend.status = status
                logger.info(f"Backend {name} status updated to {status}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Failed to update backend status: {e}")
            return False
    
    def get_backend_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all backends"""
        return [
            {
                "name": b.name,
                "host": f"{b.host}:{b.port}",
                "status": b.status,
                "connections": b.connections,
                "requests_served": b.requests_served,
                "response_time_ms": f"{b.response_time_ms:.2f}",
                "error_rate": f"{b.error_rate:.2%}",
                "load_score": f"{b.load_score():.2f}"
            }
            for b in self.backends
        ]
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """Get overall cluster statistics"""
        total_connections = sum(b.connections for b in self.backends)
        total_requests = sum(b.requests_served for b in self.backends)
        healthy_count = sum(1 for b in self.backends if b.is_healthy())
        avg_response_time = (
            sum(b.response_time_ms for b in self.backends) / len(self.backends)
            if self.backends else 0
        )
        
        return {
            "total_backends": len(self.backends),
            "healthy_backends": healthy_count,
            "total_connections": total_connections,
            "total_requests": total_requests,
            "average_response_time_ms": f"{avg_response_time:.2f}",
            "strategy": self.strategy,
            "last_health_check": self.last_health_check
        }
    
    def rebalance(self) -> bool:
        """Rebalance load across backends"""
        try:
            # Sort backends by load
            self.backends.sort(key=lambda b: b.load_score())
            
            # Optionally migrate connections if using session affinity
            logger.info("Load rebalancing completed")
            return True
        
        except Exception as e:
            logger.error(f"Failed to rebalance: {e}")
            return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize load balancer
    lb = LoadBalancer(strategy="least-connections")
    
    # Add backends
    # lb.add_backend("backend-1", "localhost", 8001, weight=1)
    # lb.add_backend("backend-2", "localhost", 8002, weight=1)
    # lb.add_backend("backend-3", "localhost", 8003, weight=2)
    
    # Health check
    # lb.health_check()
    
    # Select backend
    # backend = lb.select_backend("192.168.1.100")
    # if backend:
    #     print(f"Selected: {backend.name} ({backend.host}:{backend.port})")
    
    # Record request
    # lb.record_request(backend, response_time_ms=45.2, success=True)
    
    # Get stats
    # print(lb.get_cluster_stats())
