"""
Factory pattern implementations for the notification system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Type, Optional
import logging

logger = logging.getLogger(__name__)


class NotificationChannel(ABC):
    """Abstract base class for notification channels."""
    
    @abstractmethod
    def send(self, message: str, recipient: str, **kwargs) -> bool:
        """Send a notification message."""
        pass
    
    @abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        """Validate recipient format."""
        pass


class NotificationChannelFactory:
    """Factory for creating notification channel instances."""
    
    _channels: Dict[str, Type[NotificationChannel]] = {}
    
    @classmethod
    def register_channel(cls, channel_type: str, channel_class: Type[NotificationChannel]):
        """Register a notification channel."""
        cls._channels[channel_type.lower()] = channel_class
        logger.info(f"Registered notification channel: {channel_type}")
    
    @classmethod
    def create_channel(cls, channel_type: str) -> Optional[NotificationChannel]:
        """Create a notification channel instance."""
        channel_class = cls._channels.get(channel_type.lower())
        if channel_class:
            return channel_class()
        logger.error(f"Unknown notification channel: {channel_type}")
        return None
    
    @classmethod
    def get_available_channels(cls) -> list:
        """Get list of available notification channels."""
        return list(cls._channels.keys())


class CircuitBreakerState:
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker pattern implementation for fault tolerance."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        import time
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful execution."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def _on_failure(self):
        """Handle failed execution."""
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN


class StrategyPattern:
    """Strategy pattern for different notification strategies."""
    
    def __init__(self):
        self._strategies = {}
    
    def register_strategy(self, name: str, strategy):
        """Register a notification strategy."""
        self._strategies[name] = strategy
    
    def execute_strategy(self, strategy_name: str, *args, **kwargs):
        """Execute a specific strategy."""
        strategy = self._strategies.get(strategy_name)
        if strategy:
            return strategy(*args, **kwargs)
        raise ValueError(f"Unknown strategy: {strategy_name}")


class SingletonMeta(type):
    """Singleton metaclass for ensuring single instance."""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Observer(ABC):
    """Abstract observer for observer pattern."""
    
    @abstractmethod
    def update(self, event_type: str, data: dict):
        """Handle event notification."""
        pass


class Subject:
    """Subject class for observer pattern."""
    
    def __init__(self):
        self._observers = []
    
    def attach(self, observer: Observer):
        """Attach an observer."""
        self._observers.append(observer)
    
    def detach(self, observer: Observer):
        """Detach an observer."""
        self._observers.remove(observer)
    
    def notify(self, event_type: str, data: dict):
        """Notify all observers."""
        for observer in self._observers:
            observer.update(event_type, data)
