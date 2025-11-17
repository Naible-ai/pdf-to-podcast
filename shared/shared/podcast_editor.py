"""
Podcast editing and regeneration capabilities.

Provides APIs for editing dialogue segments, regenerating specific parts,
and managing podcast versions.
"""

from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
import json
import hashlib


class DialogueEdit(BaseModel):
    """Represents an edit to a dialogue segment."""
    segment_index: int = Field(..., description="Index of segment to edit (0-based)")
    new_text: Optional[str] = Field(None, description="New text content")
    new_speaker: Optional[str] = Field(None, description="New speaker assignment")
    action: str = Field(..., description="Edit action: 'update', 'delete', 'insert_before', 'insert_after'")
    insert_text: Optional[str] = Field(None, description="Text to insert (for insert actions)")
    insert_speaker: Optional[str] = Field(None, description="Speaker for inserted segment")


class RegenerationRequest(BaseModel):
    """Request to regenerate specific podcast segments."""
    job_id: str = Field(..., description="Original job ID")
    segment_indices: List[int] = Field(..., description="Indices of segments to regenerate")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt for regeneration")
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0, description="Override temperature")
    preserve_context: bool = Field(True, description="Use surrounding segments as context")


class PodcastVersion(BaseModel):
    """Represents a version of a podcast."""
    version_id: str = Field(..., description="Unique version identifier")
    job_id: str = Field(..., description="Parent job ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    dialogue: List[Dict[str, str]] = Field(..., description="Dialogue content")
    edits_applied: List[DialogueEdit] = Field(default_factory=list, description="Edits in this version")
    metadata: Dict = Field(default_factory=dict, description="Version metadata")
    parent_version: Optional[str] = Field(None, description="Parent version ID")

    def get_version_hash(self) -> str:
        """Generate a hash for this version based on content."""
        content = json.dumps(self.dialogue, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:12]


class PodcastEditor:
    """
    Editor for podcast transcripts with version control.

    Supports editing, regeneration, and undo/redo functionality.
    """

    def __init__(self):
        """Initialize the podcast editor."""
        self.versions: Dict[str, List[PodcastVersion]] = {}  # job_id -> versions

    def create_initial_version(
        self,
        job_id: str,
        dialogue: List[Dict[str, str]],
        metadata: Optional[Dict] = None
    ) -> PodcastVersion:
        """
        Create the initial version of a podcast.

        Args:
            job_id: Job identifier
            dialogue: Initial dialogue content
            metadata: Optional metadata

        Returns:
            PodcastVersion instance
        """
        version = PodcastVersion(
            version_id=f"{job_id}_v0",
            job_id=job_id,
            dialogue=dialogue,
            metadata=metadata or {}
        )

        if job_id not in self.versions:
            self.versions[job_id] = []

        self.versions[job_id].append(version)
        return version

    def apply_edit(
        self,
        job_id: str,
        edit: DialogueEdit,
        current_version_id: Optional[str] = None
    ) -> PodcastVersion:
        """
        Apply an edit to create a new version.

        Args:
            job_id: Job identifier
            edit: Edit to apply
            current_version_id: Version to edit from (latest if None)

        Returns:
            New PodcastVersion with edit applied
        """
        if job_id not in self.versions or not self.versions[job_id]:
            raise ValueError(f"No versions found for job {job_id}")

        # Get current version
        if current_version_id:
            current = next(
                (v for v in self.versions[job_id] if v.version_id == current_version_id),
                None
            )
            if not current:
                raise ValueError(f"Version {current_version_id} not found")
        else:
            current = self.versions[job_id][-1]

        # Apply edit to create new dialogue
        new_dialogue = current.dialogue.copy()

        if edit.action == "update":
            if edit.segment_index >= len(new_dialogue):
                raise IndexError(f"Segment index {edit.segment_index} out of range")

            if edit.new_text:
                new_dialogue[edit.segment_index]["text"] = edit.new_text
            if edit.new_speaker:
                new_dialogue[edit.segment_index]["speaker"] = edit.new_speaker

        elif edit.action == "delete":
            if edit.segment_index >= len(new_dialogue):
                raise IndexError(f"Segment index {edit.segment_index} out of range")
            new_dialogue.pop(edit.segment_index)

        elif edit.action == "insert_before":
            if not edit.insert_text or not edit.insert_speaker:
                raise ValueError("insert_text and insert_speaker required for insert_before")

            new_segment = {
                "speaker": edit.insert_speaker,
                "text": edit.insert_text
            }
            new_dialogue.insert(edit.segment_index, new_segment)

        elif edit.action == "insert_after":
            if not edit.insert_text or not edit.insert_speaker:
                raise ValueError("insert_text and insert_speaker required for insert_after")

            new_segment = {
                "speaker": edit.insert_speaker,
                "text": edit.insert_text
            }
            new_dialogue.insert(edit.segment_index + 1, new_segment)

        else:
            raise ValueError(f"Unknown action: {edit.action}")

        # Create new version
        version_num = len(self.versions[job_id])
        new_version = PodcastVersion(
            version_id=f"{job_id}_v{version_num}",
            job_id=job_id,
            dialogue=new_dialogue,
            edits_applied=[edit],
            parent_version=current.version_id,
            metadata={
                "edit_type": edit.action,
                "edited_at": datetime.utcnow().isoformat()
            }
        )

        self.versions[job_id].append(new_version)
        return new_version

    def apply_multiple_edits(
        self,
        job_id: str,
        edits: List[DialogueEdit],
        current_version_id: Optional[str] = None
    ) -> PodcastVersion:
        """
        Apply multiple edits in sequence.

        Args:
            job_id: Job identifier
            edits: List of edits to apply
            current_version_id: Version to start from

        Returns:
            New PodcastVersion with all edits applied
        """
        current_id = current_version_id

        for edit in edits:
            new_version = self.apply_edit(job_id, edit, current_id)
            current_id = new_version.version_id

        return self.versions[job_id][-1]

    def get_version(self, job_id: str, version_id: str) -> Optional[PodcastVersion]:
        """
        Get a specific version.

        Args:
            job_id: Job identifier
            version_id: Version identifier

        Returns:
            PodcastVersion or None if not found
        """
        if job_id not in self.versions:
            return None

        return next(
            (v for v in self.versions[job_id] if v.version_id == version_id),
            None
        )

    def get_latest_version(self, job_id: str) -> Optional[PodcastVersion]:
        """
        Get the latest version for a job.

        Args:
            job_id: Job identifier

        Returns:
            Latest PodcastVersion or None
        """
        if job_id not in self.versions or not self.versions[job_id]:
            return None

        return self.versions[job_id][-1]

    def list_versions(self, job_id: str) -> List[Dict]:
        """
        List all versions for a job.

        Args:
            job_id: Job identifier

        Returns:
            List of version metadata
        """
        if job_id not in self.versions:
            return []

        return [
            {
                "version_id": v.version_id,
                "created_at": v.created_at.isoformat(),
                "segment_count": len(v.dialogue),
                "edits_count": len(v.edits_applied),
                "parent_version": v.parent_version,
                "content_hash": v.get_version_hash()
            }
            for v in self.versions[job_id]
        ]

    def revert_to_version(self, job_id: str, version_id: str) -> PodcastVersion:
        """
        Revert to a previous version (creates new version with old content).

        Args:
            job_id: Job identifier
            version_id: Version to revert to

        Returns:
            New PodcastVersion with reverted content
        """
        target_version = self.get_version(job_id, version_id)
        if not target_version:
            raise ValueError(f"Version {version_id} not found")

        # Create new version with same dialogue as target
        version_num = len(self.versions[job_id])
        new_version = PodcastVersion(
            version_id=f"{job_id}_v{version_num}",
            job_id=job_id,
            dialogue=target_version.dialogue.copy(),
            parent_version=self.versions[job_id][-1].version_id,
            metadata={
                "reverted_from": version_id,
                "reverted_at": datetime.utcnow().isoformat()
            }
        )

        self.versions[job_id].append(new_version)
        return new_version

    def get_diff(self, job_id: str, version_a: str, version_b: str) -> List[Dict]:
        """
        Get differences between two versions.

        Args:
            job_id: Job identifier
            version_a: First version ID
            version_b: Second version ID

        Returns:
            List of differences
        """
        v_a = self.get_version(job_id, version_a)
        v_b = self.get_version(job_id, version_b)

        if not v_a or not v_b:
            raise ValueError("One or both versions not found")

        diffs = []

        # Simple line-by-line diff
        max_len = max(len(v_a.dialogue), len(v_b.dialogue))

        for i in range(max_len):
            a_text = v_a.dialogue[i] if i < len(v_a.dialogue) else None
            b_text = v_b.dialogue[i] if i < len(v_b.dialogue) else None

            if a_text != b_text:
                diffs.append({
                    "index": i,
                    "version_a": a_text,
                    "version_b": b_text,
                    "type": "modified" if a_text and b_text else ("added" if b_text else "removed")
                })

        return diffs

    def extract_segment_context(
        self,
        dialogue: List[Dict[str, str]],
        segment_index: int,
        context_size: int = 2
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Extract context around a segment for regeneration.

        Args:
            dialogue: Full dialogue
            segment_index: Index of segment to regenerate
            context_size: Number of segments before/after to include

        Returns:
            Tuple of (before_context, after_context)
        """
        start_idx = max(0, segment_index - context_size)
        end_idx = min(len(dialogue), segment_index + context_size + 1)

        before = dialogue[start_idx:segment_index]
        after = dialogue[segment_index + 1:end_idx]

        return before, after

    def prepare_regeneration_prompt(
        self,
        segment_to_regenerate: Dict[str, str],
        before_context: List[Dict],
        after_context: List[Dict],
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Prepare prompt for segment regeneration.

        Args:
            segment_to_regenerate: Original segment
            before_context: Previous dialogue
            after_context: Following dialogue
            custom_instructions: Optional custom instructions

        Returns:
            Regeneration prompt
        """
        prompt_parts = [
            "Please regenerate the following dialogue segment to improve it while maintaining context.",
            ""
        ]

        if before_context:
            prompt_parts.append("Previous dialogue:")
            for seg in before_context:
                prompt_parts.append(f"{seg['speaker']}: {seg['text']}")
            prompt_parts.append("")

        prompt_parts.append("Segment to regenerate:")
        prompt_parts.append(f"{segment_to_regenerate['speaker']}: {segment_to_regenerate['text']}")
        prompt_parts.append("")

        if after_context:
            prompt_parts.append("Following dialogue:")
            for seg in after_context:
                prompt_parts.append(f"{seg['speaker']}: {seg['text']}")
            prompt_parts.append("")

        if custom_instructions:
            prompt_parts.append("Custom instructions:")
            prompt_parts.append(custom_instructions)
            prompt_parts.append("")

        prompt_parts.append("Provide an improved version of the segment while:")
        prompt_parts.append("1. Maintaining consistency with surrounding context")
        prompt_parts.append("2. Keeping the same speaker")
        prompt_parts.append("3. Preserving the general topic/intent")
        prompt_parts.append("4. Making it more engaging and natural")

        return "\n".join(prompt_parts)
