"""
Task-specific LLM parameter configurations.

This module defines optimized temperature and top_p settings for different
types of LLM tasks to balance creativity, consistency, and quality.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMTaskConfig:
    """
    Configuration for a specific LLM task.

    Attributes:
        temperature (float): Sampling temperature (0.0-1.0)
        top_p (float): Nucleus sampling threshold (0.0-1.0)
        max_tokens (Optional[int]): Maximum tokens to generate
        description (str): Human-readable description of the task
    """
    temperature: float
    top_p: float
    max_tokens: Optional[int] = None
    description: str = ""


class LLMTaskConfigs:
    """
    Predefined LLM configurations for different podcast generation tasks.

    These configurations are optimized based on the nature of each task:
    - High temperature for creative tasks (dialogue, storytelling)
    - Low temperature for structured tasks (JSON formatting, combining)
    - Medium temperature for analytical tasks (summarization, outlining)
    """

    # PDF Summarization: Balanced - needs to be comprehensive but structured
    SUMMARIZE = LLMTaskConfig(
        temperature=0.5,
        top_p=0.9,
        max_tokens=4000,
        description="Comprehensive PDF summarization with factual accuracy"
    )

    # Outline Generation: Creative but structured
    OUTLINE_GENERATION = LLMTaskConfig(
        temperature=0.7,
        top_p=0.9,
        max_tokens=3000,
        description="Creative outline generation with narrative flow"
    )

    # Segment Processing: Analytical and informative
    SEGMENT_PROCESSING = LLMTaskConfig(
        temperature=0.6,
        top_p=0.85,
        max_tokens=2500,
        description="Detailed segment content generation"
    )

    # Dialogue Creation: Creative and engaging
    DIALOGUE_CREATION = LLMTaskConfig(
        temperature=0.8,
        top_p=0.95,
        max_tokens=2000,
        description="Natural, engaging dialogue generation"
    )

    # Dialogue Combining: Consistent formatting
    DIALOGUE_COMBINING = LLMTaskConfig(
        temperature=0.3,
        top_p=0.85,
        max_tokens=3000,
        description="Consistent dialogue combination and flow"
    )

    # JSON Formatting: Deterministic and structured
    JSON_FORMATTING = LLMTaskConfig(
        temperature=0.1,
        top_p=0.8,
        max_tokens=1500,
        description="Structured JSON output generation"
    )

    # Monologue Generation: Creative but focused
    MONOLOGUE_GENERATION = LLMTaskConfig(
        temperature=0.75,
        top_p=0.9,
        max_tokens=3500,
        description="Engaging monologue script generation"
    )

    # Introduction/Hook: Very creative
    CREATIVE_INTRO = LLMTaskConfig(
        temperature=0.9,
        top_p=0.95,
        max_tokens=500,
        description="Engaging podcast introduction"
    )

    # Conclusion: Balanced and summarizing
    CONCLUSION = LLMTaskConfig(
        temperature=0.6,
        top_p=0.9,
        max_tokens=800,
        description="Thoughtful conclusion and summary"
    )

    @classmethod
    def get_config(cls, task_name: str) -> LLMTaskConfig:
        """
        Get configuration for a specific task.

        Args:
            task_name (str): Name of the task

        Returns:
            LLMTaskConfig: Configuration for the task

        Raises:
            ValueError: If task_name is not found
        """
        task_map = {
            "summarize": cls.SUMMARIZE,
            "outline": cls.OUTLINE_GENERATION,
            "segment": cls.SEGMENT_PROCESSING,
            "dialogue": cls.DIALOGUE_CREATION,
            "combine": cls.DIALOGUE_COMBINING,
            "json": cls.JSON_FORMATTING,
            "monologue": cls.MONOLOGUE_GENERATION,
            "intro": cls.CREATIVE_INTRO,
            "conclusion": cls.CONCLUSION,
        }

        if task_name.lower() not in task_map:
            # Return a balanced default config
            return LLMTaskConfig(
                temperature=0.7,
                top_p=0.9,
                max_tokens=2000,
                description="Default balanced configuration"
            )

        return task_map[task_name.lower()]

    @classmethod
    def get_all_configs(cls) -> Dict[str, LLMTaskConfig]:
        """
        Get all available task configurations.

        Returns:
            Dict[str, LLMTaskConfig]: Dictionary mapping task names to configs
        """
        return {
            "summarize": cls.SUMMARIZE,
            "outline": cls.OUTLINE_GENERATION,
            "segment": cls.SEGMENT_PROCESSING,
            "dialogue": cls.DIALOGUE_CREATION,
            "combine": cls.DIALOGUE_COMBINING,
            "json": cls.JSON_FORMATTING,
            "monologue": cls.MONOLOGUE_GENERATION,
            "intro": cls.CREATIVE_INTRO,
            "conclusion": cls.CONCLUSION,
        }
