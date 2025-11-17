"""
Style templates for podcast generation.

This module provides predefined configurations for different podcast styles,
including voice settings, LLM parameters, and prompt customizations.
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from pydantic import BaseModel, Field
from .api_types import VoiceSettings
from .llm_config import LLMTaskConfig


@dataclass
class PromptModifiers:
    """Modifiers to apply to prompts for different styles."""
    tone_instruction: str
    pacing_instruction: str
    style_notes: str
    example_phrases: List[str]


class StyleTemplate(BaseModel):
    """
    Complete style template for podcast generation.

    Combines voice settings, LLM parameters, and prompt modifiers
    to create a cohesive podcast style.
    """
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    use_case: str = Field(..., description="Ideal use case")

    # Voice configuration
    speaker_1_voice: VoiceSettings
    speaker_2_voice: Optional[VoiceSettings] = None

    # LLM configuration overrides
    dialogue_temperature: float = Field(0.8, ge=0.0, le=1.0)
    outline_temperature: float = Field(0.7, ge=0.0, le=1.0)

    # Prompt modifiers
    tone: str = Field(..., description="Overall tone (professional, casual, friendly, etc.)")
    pacing: str = Field(..., description="Pacing (slow, medium, fast)")
    depth: str = Field(..., description="Content depth (overview, detailed, comprehensive)")

    # Additional instructions
    custom_instructions: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Professional Business",
                "description": "Polished, authoritative discussion",
                "use_case": "Earnings calls, business analysis",
                "tone": "professional",
                "pacing": "medium",
                "depth": "comprehensive"
            }
        }


class StyleTemplateLibrary:
    """
    Library of predefined podcast style templates.

    Provides ready-to-use configurations for common podcast styles.
    """

    # Professional Business Template
    PROFESSIONAL_BUSINESS = StyleTemplate(
        name="Professional Business",
        description="Polished, authoritative discussion for business content",
        use_case="Earnings reports, market analysis, quarterly reviews",
        speaker_1_voice=VoiceSettings(
            voice_id="iP95p4xoKVk53GoZ742B",  # Default professional voice
            stability=0.85,
            similarity_boost=0.90,
            style_exaggeration=0.15,
            use_speaker_boost=True
        ),
        speaker_2_voice=VoiceSettings(
            voice_id="9BWtsMINqrJLrRacOk9x",
            stability=0.80,
            similarity_boost=0.85,
            style_exaggeration=0.20,
            use_speaker_boost=True
        ),
        dialogue_temperature=0.6,  # More consistent
        outline_temperature=0.5,   # Structured
        tone="professional",
        pacing="medium",
        depth="comprehensive",
        custom_instructions="""
Maintain a professional, business-focused tone throughout.
Use precise financial terminology and data-driven insights.
Speakers should sound knowledgeable and authoritative.
Include specific numbers, percentages, and metrics.
Keep discussions objective and analytical.
"""
    )

    # Casual Conversation Template
    CASUAL_CONVERSATION = StyleTemplate(
        name="Casual Conversation",
        description="Friendly, relaxed discussion like chatting with friends",
        use_case="Book reviews, pop culture, general interest topics",
        speaker_1_voice=VoiceSettings(
            voice_id="iP95p4xoKVk53GoZ742B",
            stability=0.50,
            similarity_boost=0.75,
            style_exaggeration=0.50,
            use_speaker_boost=True
        ),
        speaker_2_voice=VoiceSettings(
            voice_id="9BWtsMINqrJLrRacOk9x",
            stability=0.45,
            similarity_boost=0.70,
            style_exaggeration=0.60,
            use_speaker_boost=True
        ),
        dialogue_temperature=0.85,  # More creative
        outline_temperature=0.75,   # Flexible
        tone="casual",
        pacing="medium-fast",
        depth="detailed",
        custom_instructions="""
Keep the conversation light and engaging.
Use everyday language and relatable analogies.
Speakers should feel like friends discussing over coffee.
Include personal reactions and opinions.
Use conversational fillers naturally (though, you know, I mean).
Add humor and personality to make it entertaining.
"""
    )

    # Educational Deep Dive Template
    EDUCATIONAL_DEEP_DIVE = StyleTemplate(
        name="Educational Deep Dive",
        description="Thorough, informative exploration of complex topics",
        use_case="Research papers, technical documentation, educational content",
        speaker_1_voice=VoiceSettings(
            voice_id="iP95p4xoKVk53GoZ742B",
            stability=0.80,
            similarity_boost=0.85,
            style_exaggeration=0.25,
            use_speaker_boost=True
        ),
        speaker_2_voice=VoiceSettings(
            voice_id="9BWtsMINqrJLrRacOk9x",
            stability=0.75,
            similarity_boost=0.80,
            style_exaggeration=0.30,
            use_speaker_boost=True
        ),
        dialogue_temperature=0.7,
        outline_temperature=0.65,
        tone="educational",
        pacing="slow-medium",
        depth="comprehensive",
        custom_instructions="""
Explain complex concepts clearly and thoroughly.
Break down technical topics into digestible segments.
Use analogies and examples to clarify difficult ideas.
One speaker can play the 'teacher' role, another the 'curious learner'.
Include definitions of key terms.
Build on concepts progressively.
Encourage questions and explanations.
"""
    )

    # Storytelling Narrative Template
    STORYTELLING_NARRATIVE = StyleTemplate(
        name="Storytelling Narrative",
        description="Engaging, dramatic narrative style",
        use_case="Historical events, case studies, narrative non-fiction",
        speaker_1_voice=VoiceSettings(
            voice_id="iP95p4xoKVk53GoZ742B",
            stability=0.70,
            similarity_boost=0.85,
            style_exaggeration=0.55,
            use_speaker_boost=True
        ),
        speaker_2_voice=VoiceSettings(
            voice_id="9BWtsMINqrJLrRacOk9x",
            stability=0.65,
            similarity_boost=0.80,
            style_exaggeration=0.60,
            use_speaker_boost=True
        ),
        dialogue_temperature=0.9,   # Very creative
        outline_temperature=0.85,   # Narrative flow
        tone="engaging",
        pacing="varied",
        depth="detailed",
        custom_instructions="""
Create a compelling narrative arc with beginning, middle, and end.
Use vivid descriptions and sensory details.
Build tension and suspense where appropriate.
Include character development and motivations.
Use dramatic pacing - slow down for important moments.
Create emotional connection with the audience.
Paint pictures with words.
"""
    )

    # News & Current Events Template
    NEWS_ANALYSIS = StyleTemplate(
        name="News Analysis",
        description="Timely, balanced discussion of current events",
        use_case="News articles, policy documents, current affairs",
        speaker_1_voice=VoiceSettings(
            voice_id="iP95p4xoKVk53GoZ742B",
            stability=0.75,
            similarity_boost=0.88,
            style_exaggeration=0.20,
            use_speaker_boost=True
        ),
        speaker_2_voice=VoiceSettings(
            voice_id="9BWtsMINqrJLrRacOk9x",
            stability=0.72,
            similarity_boost=0.85,
            style_exaggeration=0.25,
            use_speaker_boost=True
        ),
        dialogue_temperature=0.65,
        outline_temperature=0.60,
        tone="journalistic",
        pacing="medium-fast",
        depth="detailed",
        custom_instructions="""
Present information objectively and factually.
Include multiple perspectives on controversial topics.
Use clear, journalistic language.
Cite sources and provide context.
Maintain urgency appropriate for news content.
Separate facts from analysis clearly.
Ask probing questions to explore implications.
"""
    )

    # Comedy & Entertainment Template
    COMEDY_ENTERTAINMENT = StyleTemplate(
        name="Comedy & Entertainment",
        description="Fun, humorous take on content",
        use_case="Light content, entertainment, humorous reviews",
        speaker_1_voice=VoiceSettings(
            voice_id="iP95p4xoKVk53GoZ742B",
            stability=0.40,
            similarity_boost=0.70,
            style_exaggeration=0.70,
            use_speaker_boost=True
        ),
        speaker_2_voice=VoiceSettings(
            voice_id="9BWtsMINqrJLrRacOk9x",
            stability=0.35,
            similarity_boost=0.65,
            style_exaggeration=0.75,
            use_speaker_boost=True
        ),
        dialogue_temperature=0.95,  # Maximum creativity
        outline_temperature=0.90,   # Flexible structure
        tone="humorous",
        pacing="fast",
        depth="overview",
        custom_instructions="""
Make it entertaining and fun!
Use humor, jokes, and witty commentary.
React with personality and emotion.
Playful banter between speakers.
Don't be afraid to be silly or exaggerate for effect.
Use pop culture references.
Keep energy high and engaging.
"""
    )

    @classmethod
    def get_template(cls, template_name: str) -> StyleTemplate:
        """
        Get a template by name.

        Args:
            template_name: Name of the template

        Returns:
            StyleTemplate instance

        Raises:
            ValueError: If template not found
        """
        templates = {
            "professional": cls.PROFESSIONAL_BUSINESS,
            "casual": cls.CASUAL_CONVERSATION,
            "educational": cls.EDUCATIONAL_DEEP_DIVE,
            "storytelling": cls.STORYTELLING_NARRATIVE,
            "news": cls.NEWS_ANALYSIS,
            "comedy": cls.COMEDY_ENTERTAINMENT,
        }

        template_name = template_name.lower()
        if template_name not in templates:
            available = ", ".join(templates.keys())
            raise ValueError(
                f"Template '{template_name}' not found. "
                f"Available templates: {available}"
            )

        return templates[template_name]

    @classmethod
    def list_templates(cls) -> List[Dict[str, str]]:
        """
        List all available templates with descriptions.

        Returns:
            List of template metadata
        """
        return [
            {
                "id": "professional",
                "name": cls.PROFESSIONAL_BUSINESS.name,
                "description": cls.PROFESSIONAL_BUSINESS.description,
                "use_case": cls.PROFESSIONAL_BUSINESS.use_case,
            },
            {
                "id": "casual",
                "name": cls.CASUAL_CONVERSATION.name,
                "description": cls.CASUAL_CONVERSATION.description,
                "use_case": cls.CASUAL_CONVERSATION.use_case,
            },
            {
                "id": "educational",
                "name": cls.EDUCATIONAL_DEEP_DIVE.name,
                "description": cls.EDUCATIONAL_DEEP_DIVE.description,
                "use_case": cls.EDUCATIONAL_DEEP_DIVE.use_case,
            },
            {
                "id": "storytelling",
                "name": cls.STORYTELLING_NARRATIVE.name,
                "description": cls.STORYTELLING_NARRATIVE.description,
                "use_case": cls.STORYTELLING_NARRATIVE.use_case,
            },
            {
                "id": "news",
                "name": cls.NEWS_ANALYSIS.name,
                "description": cls.NEWS_ANALYSIS.description,
                "use_case": cls.NEWS_ANALYSIS.use_case,
            },
            {
                "id": "comedy",
                "name": cls.COMEDY_ENTERTAINMENT.name,
                "description": cls.COMEDY_ENTERTAINMENT.description,
                "use_case": cls.COMEDY_ENTERTAINMENT.use_case,
            },
        ]

    @classmethod
    def apply_template(
        cls,
        template_name: str,
        base_params: Dict
    ) -> Dict:
        """
        Apply a template to base transcription parameters.

        Args:
            template_name: Name of the template to apply
            base_params: Base transcription parameters

        Returns:
            Updated parameters with template applied
        """
        template = cls.get_template(template_name)

        # Create voice settings dictionary
        voice_settings = {
            "speaker-1": template.speaker_1_voice
        }

        if not base_params.get("monologue", False) and template.speaker_2_voice:
            voice_settings["speaker-2"] = template.speaker_2_voice

        # Build custom guide combining template instructions with user guide
        guide_parts = []

        # Add template-specific instructions
        if template.custom_instructions:
            guide_parts.append(f"Style: {template.name}")
            guide_parts.append(template.custom_instructions.strip())

        # Add user's original guide if provided
        if base_params.get("guide"):
            guide_parts.append("\nAdditional Instructions:")
            guide_parts.append(base_params["guide"])

        # Update parameters
        updated = base_params.copy()
        updated["voice_settings"] = {
            k: v.dict() for k, v in voice_settings.items()
        }
        updated["guide"] = "\n\n".join(guide_parts) if guide_parts else None

        # Store template metadata for reference
        updated["template_applied"] = {
            "name": template.name,
            "tone": template.tone,
            "pacing": template.pacing,
            "depth": template.depth,
            "dialogue_temperature": template.dialogue_temperature,
            "outline_temperature": template.outline_temperature,
        }

        return updated


def get_template_for_use_case(keywords: List[str]) -> str:
    """
    Suggest a template based on content keywords.

    Args:
        keywords: List of keywords from the content

    Returns:
        Template ID suggestion
    """
    keywords_lower = [k.lower() for k in keywords]

    # Business/financial keywords
    if any(k in keywords_lower for k in ["earnings", "revenue", "profit", "financial", "quarterly", "market"]):
        return "professional"

    # Educational keywords
    if any(k in keywords_lower for k in ["research", "study", "analysis", "methodology", "findings"]):
        return "educational"

    # News keywords
    if any(k in keywords_lower for k in ["breaking", "report", "update", "announced", "policy"]):
        return "news"

    # Storytelling keywords
    if any(k in keywords_lower for k in ["story", "narrative", "journey", "history", "case study"]):
        return "storytelling"

    # Default to casual for general content
    return "casual"
