"""
Módulo de métricas para UDCito
Recopila y gestiona métricas del sistema
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque

logger = logging.getLogger(__name__)

class MetricsCollector:
    """
    Recolector de métricas del sistema
    Mantiene un historial de métricas para análisis
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.start_time = datetime.now()
        
        # Contadores de uso
        self.requests_total = 0
        self.successful_queries = 0
        self.failed_queries = 0
        
        # Tiempos de respuesta
        self.response_times: List[float] = deque(maxlen=1000)
    
    def record_request(self, success: bool, response_time: float):
        """Registra una petición al sistema"""
        self.requests_total += 1
        if success:
            self.successful_queries += 1
        else:
            self.failed_queries += 1
        
        self.response_times.append(response_time)
        
        # Registrar en el historial
        metric = {
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'response_time': response_time
        }
        self.metrics_history.append(metric)
    
    def get_current_metrics(self) -> Dict:
        """Obtiene métricas actuales del sistema"""
        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times else 0
        )
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'total_requests': self.requests_total,
            'successful_requests': self.successful_queries,
            'failed_requests': self.failed_queries,
            'success_rate': (
                (self.successful_queries / self.requests_total * 100)
                if self.requests_total > 0 else 0
            ),
            'average_response_time': avg_response_time,
            'requests_per_minute': (
                self.requests_total / (uptime / 60)
                if uptime > 0 else 0
            )
        }
    
    def reset_metrics(self):
        """Reinicia los contadores de métricas"""
        self.requests_total = 0
        self.successful_queries = 0
        self.failed_queries = 0
        self.response_times.clear()
        self.metrics_history.clear()
        self.start_time = datetime.now()
        logger.info("Metrics have been reset")

# Instancia global del collector de métricas
metrics_collector = MetricsCollector()