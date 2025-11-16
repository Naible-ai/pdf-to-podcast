"""
Progress tracking utility for podcast generation workflow.

This module provides a ProgressTracker class that calculates completion percentages,
estimates time to completion, and tracks resource usage across different workflow stages.
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class WorkflowStep:
    """Represents a step in the podcast generation workflow.

    Attributes:
        name (str): Name of the step
        weight (float): Relative weight/importance (0-1)
        estimated_duration (float): Estimated duration in seconds
    """
    name: str
    weight: float
    estimated_duration: float = 0.0


class ProgressTracker:
    """
    Tracks progress through a multi-step workflow with ETA calculation.

    This class maintains state for workflow progress, calculating completion
    percentages and estimating time to completion based on historical performance.

    Attributes:
        workflow_name (str): Name of the workflow being tracked
        steps (List[WorkflowStep]): List of workflow steps with weights
        current_step_index (int): Index of the current step
        start_time (float): Workflow start timestamp
        step_start_time (float): Current step start timestamp
        tokens_used (int): Total tokens consumed
        step_durations (List[float]): Actual duration of completed steps
    """

    # Predefined workflow configurations
    PODCAST_WORKFLOW = [
        WorkflowStep("PDF Processing", 0.15, 45.0),
        WorkflowStep("Summarization", 0.20, 90.0),
        WorkflowStep("Outline Generation", 0.10, 30.0),
        WorkflowStep("Segment Processing", 0.25, 120.0),
        WorkflowStep("Dialogue Creation", 0.20, 150.0),
        WorkflowStep("TTS Generation", 0.10, 60.0),
    ]

    MONOLOGUE_WORKFLOW = [
        WorkflowStep("PDF Processing", 0.20, 45.0),
        WorkflowStep("Summarization", 0.25, 90.0),
        WorkflowStep("Outline Generation", 0.15, 30.0),
        WorkflowStep("Monologue Generation", 0.30, 100.0),
        WorkflowStep("TTS Generation", 0.10, 60.0),
    ]

    def __init__(
        self,
        workflow_name: str = "podcast",
        custom_steps: Optional[List[WorkflowStep]] = None
    ):
        """
        Initialize the ProgressTracker.

        Args:
            workflow_name (str): Type of workflow ("podcast" or "monologue")
            custom_steps (Optional[List[WorkflowStep]]): Custom workflow steps
        """
        self.workflow_name = workflow_name

        if custom_steps:
            self.steps = custom_steps
        elif workflow_name == "monologue":
            self.steps = self.MONOLOGUE_WORKFLOW
        else:
            self.steps = self.PODCAST_WORKFLOW

        self.current_step_index = 0
        self.start_time = time.time()
        self.step_start_time = time.time()
        self.tokens_used = 0
        self.step_durations: List[float] = []

    def start_step(self, step_name: str):
        """
        Mark the start of a new workflow step.

        Args:
            step_name (str): Name of the step being started
        """
        # Find the step index
        for i, step in enumerate(self.steps):
            if step.name == step_name:
                self.current_step_index = i
                self.step_start_time = time.time()
                break

    def complete_step(self):
        """
        Mark the current step as complete and record its duration.
        """
        duration = time.time() - self.step_start_time
        self.step_durations.append(duration)
        self.current_step_index += 1

    def get_percentage(self) -> float:
        """
        Calculate the current completion percentage.

        Returns:
            float: Completion percentage (0-100)
        """
        if not self.steps:
            return 0.0

        # Calculate weight of completed steps
        completed_weight = sum(
            step.weight for step in self.steps[:self.current_step_index]
        )

        # Add partial progress of current step (assume 50% if in progress)
        if self.current_step_index < len(self.steps):
            current_step = self.steps[self.current_step_index]
            # Use time-based progress if we have estimates
            if current_step.estimated_duration > 0:
                step_elapsed = time.time() - self.step_start_time
                step_progress = min(step_elapsed / current_step.estimated_duration, 0.9)
                completed_weight += current_step.weight * step_progress
            else:
                # Default to 30% progress for current step
                completed_weight += current_step.weight * 0.3

        # Total weight should be 1.0, but normalize just in case
        total_weight = sum(step.weight for step in self.steps)
        percentage = (completed_weight / total_weight) * 100

        return min(percentage, 99.0)  # Cap at 99% until fully complete

    def get_eta_seconds(self) -> int:
        """
        Estimate time to completion based on historical performance.

        Returns:
            int: Estimated seconds to completion
        """
        if self.current_step_index >= len(self.steps):
            return 0

        # Calculate average speed factor
        if len(self.step_durations) > 0:
            # Compare actual vs estimated durations
            speed_factors = []
            for i, actual_duration in enumerate(self.step_durations):
                if i < len(self.steps) and self.steps[i].estimated_duration > 0:
                    factor = actual_duration / self.steps[i].estimated_duration
                    speed_factors.append(factor)

            avg_speed_factor = (
                sum(speed_factors) / len(speed_factors) if speed_factors else 1.0
            )
        else:
            avg_speed_factor = 1.0

        # Estimate remaining time
        remaining_time = 0.0

        # Time remaining in current step
        if self.current_step_index < len(self.steps):
            current_step = self.steps[self.current_step_index]
            step_elapsed = time.time() - self.step_start_time
            estimated_step_duration = current_step.estimated_duration * avg_speed_factor
            remaining_time += max(0, estimated_step_duration - step_elapsed)

        # Time for remaining steps
        for step in self.steps[self.current_step_index + 1:]:
            remaining_time += step.estimated_duration * avg_speed_factor

        return int(remaining_time)

    def add_tokens(self, tokens: int):
        """
        Add to the token usage count.

        Args:
            tokens (int): Number of tokens to add
        """
        self.tokens_used += tokens

    def estimate_cost(self, cost_per_1k_tokens: float = 0.002) -> float:
        """
        Estimate the cost based on token usage.

        Args:
            cost_per_1k_tokens (float): Cost per 1000 tokens (default: $0.002)

        Returns:
            float: Estimated cost in USD
        """
        return (self.tokens_used / 1000) * cost_per_1k_tokens

    def get_progress_summary(self) -> Dict[str, any]:
        """
        Get a comprehensive progress summary.

        Returns:
            Dict: Progress information including percentage, ETA, tokens, and cost
        """
        return {
            "percentage": round(self.get_percentage(), 2),
            "eta_seconds": self.get_eta_seconds(),
            "current_step": (
                self.steps[self.current_step_index].name
                if self.current_step_index < len(self.steps)
                else "Complete"
            ),
            "tokens_used": self.tokens_used,
            "estimated_cost": round(self.estimate_cost(), 4),
            "elapsed_seconds": int(time.time() - self.start_time),
        }
