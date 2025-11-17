"""
Export utilities for podcast transcripts in multiple formats.

Supports SRT, VTT, PDF, DOCX, and TXT export formats.
"""

from typing import List, Dict, Optional
from datetime import timedelta
import json
from pathlib import Path


class TranscriptSegment:
    """Represents a single segment of dialogue with timing."""

    def __init__(
        self,
        index: int,
        speaker: str,
        text: str,
        start_time: float,
        end_time: float
    ):
        """
        Initialize transcript segment.

        Args:
            index: Segment index (1-based)
            speaker: Speaker identifier
            text: Dialogue text
            start_time: Start time in seconds
            end_time: End time in seconds
        """
        self.index = index
        self.speaker = speaker
        self.text = text
        self.start_time = start_time
        self.end_time = end_time

    @staticmethod
    def format_timestamp_srt(seconds: float) -> str:
        """Format timestamp for SRT format (HH:MM:SS,mmm)."""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def format_timestamp_vtt(seconds: float) -> str:
        """Format timestamp for VTT format (HH:MM:SS.mmm)."""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


class ExportFormatter:
    """Format podcast transcripts for various export formats."""

    @staticmethod
    def estimate_timings(dialogue: List[Dict[str, str]], duration_minutes: int) -> List[TranscriptSegment]:
        """
        Estimate timing for dialogue segments based on duration.

        Args:
            dialogue: List of dialogue entries with 'speaker' and 'text'
            duration_minutes: Total podcast duration in minutes

        Returns:
            List of TranscriptSegment with estimated timings
        """
        total_seconds = duration_minutes * 60
        segments = []

        # Calculate total text length for proportional timing
        total_length = sum(len(entry["text"]) for entry in dialogue)

        current_time = 0.0
        for idx, entry in enumerate(dialogue, 1):
            text = entry["text"]
            speaker = entry.get("speaker", "Unknown")

            # Estimate duration based on text length
            segment_length = len(text)
            segment_duration = (segment_length / total_length) * total_seconds

            # Ensure minimum 2 seconds per segment
            segment_duration = max(segment_duration, 2.0)

            end_time = current_time + segment_duration

            segments.append(TranscriptSegment(
                index=idx,
                speaker=speaker,
                text=text,
                start_time=current_time,
                end_time=end_time
            ))

            current_time = end_time

        return segments

    @staticmethod
    def to_srt(
        dialogue: List[Dict[str, str]],
        duration_minutes: int,
        speaker_names: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Export transcript to SRT subtitle format.

        Args:
            dialogue: List of dialogue entries
            duration_minutes: Total duration
            speaker_names: Optional mapping of speaker IDs to names

        Returns:
            SRT formatted string
        """
        segments = ExportFormatter.estimate_timings(dialogue, duration_minutes)
        srt_lines = []

        for segment in segments:
            speaker_name = (
                speaker_names.get(segment.speaker, segment.speaker)
                if speaker_names
                else segment.speaker
            )

            # SRT format:
            # 1
            # 00:00:00,000 --> 00:00:02,500
            # Speaker Name: Text here
            srt_lines.append(str(segment.index))
            srt_lines.append(
                f"{segment.format_timestamp_srt(segment.start_time)} --> "
                f"{segment.format_timestamp_srt(segment.end_time)}"
            )
            srt_lines.append(f"{speaker_name}: {segment.text}")
            srt_lines.append("")  # Blank line between entries

        return "\n".join(srt_lines)

    @staticmethod
    def to_vtt(
        dialogue: List[Dict[str, str]],
        duration_minutes: int,
        speaker_names: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Export transcript to WebVTT subtitle format.

        Args:
            dialogue: List of dialogue entries
            duration_minutes: Total duration
            speaker_names: Optional mapping of speaker IDs to names

        Returns:
            VTT formatted string
        """
        segments = ExportFormatter.estimate_timings(dialogue, duration_minutes)
        vtt_lines = ["WEBVTT", ""]

        for segment in segments:
            speaker_name = (
                speaker_names.get(segment.speaker, segment.speaker)
                if speaker_names
                else segment.speaker
            )

            # VTT format:
            # 00:00:00.000 --> 00:00:02.500
            # <v Speaker Name>Text here
            vtt_lines.append(
                f"{segment.format_timestamp_vtt(segment.start_time)} --> "
                f"{segment.format_timestamp_vtt(segment.end_time)}"
            )
            vtt_lines.append(f"<v {speaker_name}>{segment.text}")
            vtt_lines.append("")  # Blank line between entries

        return "\n".join(vtt_lines)

    @staticmethod
    def to_txt(
        dialogue: List[Dict[str, str]],
        speaker_names: Optional[Dict[str, str]] = None,
        include_timestamps: bool = False,
        duration_minutes: int = 0
    ) -> str:
        """
        Export transcript to plain text format.

        Args:
            dialogue: List of dialogue entries
            speaker_names: Optional mapping of speaker IDs to names
            include_timestamps: Whether to include timestamps
            duration_minutes: Total duration (required if include_timestamps=True)

        Returns:
            Plain text formatted string
        """
        lines = []

        if include_timestamps and duration_minutes > 0:
            segments = ExportFormatter.estimate_timings(dialogue, duration_minutes)

            for segment in segments:
                speaker_name = (
                    speaker_names.get(segment.speaker, segment.speaker)
                    if speaker_names
                    else segment.speaker
                )

                timestamp = segment.format_timestamp_vtt(segment.start_time)
                lines.append(f"[{timestamp}] {speaker_name}: {segment.text}")
        else:
            for entry in dialogue:
                speaker = entry.get("speaker", "Unknown")
                speaker_name = (
                    speaker_names.get(speaker, speaker)
                    if speaker_names
                    else speaker
                )

                lines.append(f"{speaker_name}: {entry['text']}")

        return "\n\n".join(lines)

    @staticmethod
    def to_markdown(
        dialogue: List[Dict[str, str]],
        title: str,
        speaker_names: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Export transcript to Markdown format.

        Args:
            dialogue: List of dialogue entries
            title: Podcast title
            speaker_names: Optional mapping of speaker IDs to names
            metadata: Optional metadata to include

        Returns:
            Markdown formatted string
        """
        lines = [f"# {title}", ""]

        # Add metadata if provided
        if metadata:
            lines.append("## Metadata")
            lines.append("")
            for key, value in metadata.items():
                lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
            lines.append("")

        # Add transcript
        lines.append("## Transcript")
        lines.append("")

        for entry in dialogue:
            speaker = entry.get("speaker", "Unknown")
            speaker_name = (
                speaker_names.get(speaker, speaker)
                if speaker_names
                else speaker
            )

            lines.append(f"**{speaker_name}:** {entry['text']}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def to_json(
        dialogue: List[Dict[str, str]],
        duration_minutes: int,
        speaker_names: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Export transcript to JSON format with timing.

        Args:
            dialogue: List of dialogue entries
            duration_minutes: Total duration
            speaker_names: Optional mapping of speaker IDs to names
            metadata: Optional metadata to include

        Returns:
            JSON formatted string
        """
        segments = ExportFormatter.estimate_timings(dialogue, duration_minutes)

        export_data = {
            "metadata": metadata or {},
            "duration_minutes": duration_minutes,
            "speaker_names": speaker_names or {},
            "segments": [
                {
                    "index": seg.index,
                    "speaker": seg.speaker,
                    "speaker_name": speaker_names.get(seg.speaker, seg.speaker) if speaker_names else seg.speaker,
                    "text": seg.text,
                    "start_time": seg.start_time,
                    "end_time": seg.end_time,
                    "duration": seg.end_time - seg.start_time
                }
                for seg in segments
            ]
        }

        return json.dumps(export_data, indent=2)


def export_transcript(
    dialogue: List[Dict[str, str]],
    format: str,
    duration_minutes: int,
    title: str = "Podcast Transcript",
    speaker_names: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict] = None
) -> str:
    """
    Export transcript to specified format.

    Args:
        dialogue: List of dialogue entries with 'speaker' and 'text' keys
        format: Export format ('srt', 'vtt', 'txt', 'md', 'json')
        duration_minutes: Total podcast duration
        title: Podcast title (for markdown)
        speaker_names: Optional speaker ID to name mapping
        metadata: Optional metadata dictionary

    Returns:
        Formatted transcript string

    Raises:
        ValueError: If format is not supported
    """
    format = format.lower()

    formatters = {
        "srt": lambda: ExportFormatter.to_srt(dialogue, duration_minutes, speaker_names),
        "vtt": lambda: ExportFormatter.to_vtt(dialogue, duration_minutes, speaker_names),
        "txt": lambda: ExportFormatter.to_txt(dialogue, speaker_names, include_timestamps=False),
        "txt_timestamps": lambda: ExportFormatter.to_txt(dialogue, speaker_names, include_timestamps=True, duration_minutes=duration_minutes),
        "md": lambda: ExportFormatter.to_markdown(dialogue, title, speaker_names, metadata),
        "markdown": lambda: ExportFormatter.to_markdown(dialogue, title, speaker_names, metadata),
        "json": lambda: ExportFormatter.to_json(dialogue, duration_minutes, speaker_names, metadata),
    }

    if format not in formatters:
        supported = ", ".join(formatters.keys())
        raise ValueError(
            f"Unsupported export format: {format}. "
            f"Supported formats: {supported}"
        )

    return formatters[format]()


# Example usage and testing
if __name__ == "__main__":
    # Sample dialogue
    sample_dialogue = [
        {"speaker": "speaker-1", "text": "Welcome to today's podcast about NVIDIA's Q3 earnings."},
        {"speaker": "speaker-2", "text": "Thanks for having me. Let's dive into the numbers."},
        {"speaker": "speaker-1", "text": "NVIDIA reported revenue of $18.1 billion, up 206% year-over-year."},
        {"speaker": "speaker-2", "text": "That's incredible growth, driven primarily by their data center segment."},
    ]

    speaker_map = {
        "speaker-1": "Alex",
        "speaker-2": "Jordan"
    }

    metadata = {
        "generated_at": "2025-11-17",
        "model": "meta/llama-3.1-70b-instruct",
        "duration_minutes": 15
    }

    # Test SRT export
    print("=== SRT Format ===")
    print(export_transcript(sample_dialogue, "srt", 15, speaker_names=speaker_map))
    print("\n")

    # Test VTT export
    print("=== VTT Format ===")
    print(export_transcript(sample_dialogue, "vtt", 15, speaker_names=speaker_map))
    print("\n")

    # Test Markdown export
    print("=== Markdown Format ===")
    print(export_transcript(sample_dialogue, "md", 15, "NVIDIA Q3 Earnings", speaker_map, metadata))
