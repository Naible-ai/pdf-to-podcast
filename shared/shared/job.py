from shared.api_types import ServiceType
from shared.otel import OpenTelemetryInstrumentation
import redis
import time
import ujson as json
import threading


class JobStatusManager:
    """
    Manages job status and results using Redis as a backend store.
    
    This class provides methods to track job status, store results, and manage cleanup
    of old jobs. It uses Redis hash sets for status storage and Redis pub/sub for 
    real-time status updates.
    
    Attributes:
        telemetry (OpenTelemetryInstrumentation): Telemetry instrumentation instance
        redis (redis.Redis): Redis client instance
        service_type (ServiceType): Type of service using this manager
        _lock (threading.Lock): Thread lock for synchronization
    """

    def __init__(
        self,
        service_type: ServiceType,
        telemetry: OpenTelemetryInstrumentation,
        redis_url="redis://redis:6379",
    ):
        """
        Initialize the JobStatusManager.
        
        Args:
            service_type (ServiceType): Type of service using this manager
            telemetry (OpenTelemetryInstrumentation): Telemetry instrumentation instance
            redis_url (str, optional): Redis connection URL. Defaults to "redis://redis:6379"
        """
        self.telemetry = telemetry
        self.redis = redis.Redis.from_url(redis_url, decode_responses=False)
        self.service_type = service_type
        self._lock = threading.Lock()

    def create_job(self, job_id: str):
        """
        Create a new job with pending status.
        
        Args:
            job_id (str): Unique identifier for the job
        """
        with self.telemetry.tracer.start_as_current_span("job.create_job") as span:
            span.set_attribute("job_id", job_id)
            update = {
                "job_id": job_id,
                "status": "pending",
                "message": "Job created",
                "service": self.service_type,
                "timestamp": time.time(),
            }
            # Encode the update dict as JSON bytes
            hset_key = f"status:{job_id}:{str(self.service_type)}"
            span.set_attribute("hset_key", hset_key)
            self.redis.hset(
                hset_key,
                mapping={k: str(v).encode() for k, v in update.items()},
            )
            self.redis.publish("status_updates:all", json.dumps(update).encode())

    def update_status(self, job_id: str, status: str, message: str,
                     percentage: float = None, eta_seconds: int = None,
                     tokens_used: int = None, estimated_cost: float = None):
        """
        Update the status of an existing job with enhanced progress tracking.

        Args:
            job_id (str): Job identifier
            status (str): New status value
            message (str): Status update message
            percentage (float, optional): Completion percentage (0-100)
            eta_seconds (int, optional): Estimated time to completion in seconds
            tokens_used (int, optional): Total tokens consumed
            estimated_cost (float, optional): Estimated cost in USD
        """
        with self.telemetry.tracer.start_as_current_span("job.update_status") as span:
            span.set_attribute("job_id", job_id)
            update = {
                "job_id": job_id,
                "status": status,
                "message": message,
                "service": self.service_type,
                "timestamp": time.time(),
            }

            # Add optional progress metrics
            if percentage is not None:
                update["percentage"] = round(percentage, 2)
                span.set_attribute("percentage", percentage)
            if eta_seconds is not None:
                update["eta_seconds"] = eta_seconds
                span.set_attribute("eta_seconds", eta_seconds)
            if tokens_used is not None:
                update["tokens_used"] = tokens_used
                span.set_attribute("tokens_used", tokens_used)
            if estimated_cost is not None:
                update["estimated_cost"] = round(estimated_cost, 4)
                span.set_attribute("estimated_cost", estimated_cost)

            # Encode the update dict as JSON bytes
            hset_key = f"status:{job_id}:{str(self.service_type)}"
            span.set_attribute("hset_key", hset_key)
            self.redis.hset(
                hset_key,
                mapping={k: str(v).encode() for k, v in update.items()},
            )
            self.redis.publish("status_updates:all", json.dumps(update).encode())

    def set_result(self, job_id: str, result: bytes):
        """
        Store the result data for a job.
        
        Args:
            job_id (str): Job identifier
            result (bytes): Result data to store
        """
        with self.telemetry.tracer.start_as_current_span("job.set_result") as span:
            span.set_attribute("job_id", job_id)
            set_key = f"result:{job_id}:{str(self.service_type)}"
            span.set_attribute("set_key", set_key)
            self.redis.set(set_key, result)

    def set_result_with_expiration(self, job_id: str, result: bytes, ex: int):
        """
        Store the result data with an expiration time.
        
        Args:
            job_id (str): Job identifier
            result (bytes): Result data to store
            ex (int): Expiration time in seconds
        """
        with self.telemetry.tracer.start_as_current_span(
            "job.set_result_with_expiration"
        ) as span:
            span.set_attribute("job_id", job_id)
            set_key = f"result:{job_id}:{str(self.service_type)}"
            span.set_attribute("set_key", set_key)
            self.redis.set(set_key, result, ex=ex)

    def get_result(self, job_id: str):
        """
        Retrieve the result data for a job.
        
        Args:
            job_id (str): Job identifier
            
        Returns:
            bytes: Result data if found, None otherwise
        """
        with self.telemetry.tracer.start_as_current_span("job.get_result") as span:
            span.set_attribute("job_id", job_id)
            get_key = f"result:{job_id}:{str(self.service_type)}"
            span.set_attribute("get_key", get_key)
            result = self.redis.get(get_key)
            return result if result else None

    def get_status(self, job_id: str):
        """
        Get the current status of a job.
        
        Args:
            job_id (str): Job identifier
            
        Returns:
            dict: Job status information
            
        Raises:
            ValueError: If job not found
        """
        with self.telemetry.tracer.start_as_current_span("job.get_status") as span:
            span.set_attribute("job_id", job_id)
            # Get raw bytes and decode manually
            hget_key = f"status:{job_id}:{str(self.service_type)}"
            span.set_attribute("hget_key", hget_key)
            status = self.redis.hgetall(hget_key)
            if not status:
                raise ValueError("Job not found")
            # Decode bytes to strings for each field
            return {k.decode(): v.decode() for k, v in status.items()}

    def cleanup_old_jobs(self, max_age=3600):
        """
        Remove jobs older than the specified age.
        
        Args:
            max_age (int, optional): Maximum age in seconds. Defaults to 3600.
            
        Returns:
            int: Number of jobs removed
        """
        current_time = time.time()
        removed = 0
        pattern = f"status:*:{str(self.service_type)}"
        for key in self.redis.scan_iter(match=pattern):
            status = self.redis.hgetall(key)
            try:
                timestamp = float(status[b"timestamp"].decode())
                if timestamp < current_time - max_age:
                    self.redis.delete(key)
                    job_id = key.split(b":")[1].decode()
                    self.redis.delete(f"result:{job_id}:{self.service_type}")
                    removed += 1
            except (KeyError, ValueError):
                # Handle malformed status entries
                continue
        return removed
