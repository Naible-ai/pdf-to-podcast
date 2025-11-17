"""
Enhanced API endpoints for podcast editing, templates, and export.

These endpoints extend the base API with advanced user features.
"""

from fastapi import APIRouter, HTTPException, Query, Response
from typing import Optional, List
from pydantic import BaseModel, Field
import sys
import os

# Add shared directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.style_templates import StyleTemplateLibrary, StyleTemplate
from shared.export_formats import export_transcript
from shared.podcast_editor import (
    PodcastEditor,
    DialogueEdit,
    RegenerationRequest,
    PodcastVersion
)
from shared.storage import StorageManager
from shared.otel import OpenTelemetryInstrumentation

# Initialize router
router = APIRouter(prefix="/api/v1", tags=["enhanced"])

# Global instances (in production, use dependency injection)
podcast_editor = PodcastEditor()
telemetry = OpenTelemetryInstrumentation("enhanced-api")


# ============================================================================
# STYLE TEMPLATES ENDPOINTS
# ============================================================================

@router.get("/templates", summary="List all available style templates")
async def list_templates():
    """
    Get list of all available podcast style templates.

    Returns metadata for each template including name, description,
    and recommended use cases.
    """
    with telemetry.tracer.start_as_current_span("api.list_templates"):
        try:
            templates = StyleTemplateLibrary.list_templates()
            return {
                "templates": templates,
                "count": len(templates)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}", summary="Get specific template details")
async def get_template(template_id: str):
    """
    Get detailed configuration for a specific template.

    Args:
        template_id: Template identifier (professional, casual, educational, etc.)

    Returns:
        Complete template configuration including voice settings and LLM parameters
    """
    with telemetry.tracer.start_as_current_span("api.get_template") as span:
        span.set_attribute("template_id", template_id)

        try:
            template = StyleTemplateLibrary.get_template(template_id)
            return template.dict()
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


class ApplyTemplateRequest(BaseModel):
    """Request to apply a template to transcription parameters."""
    template_id: str = Field(..., description="Template to apply")
    base_params: dict = Field(..., description="Base transcription parameters")


@router.post("/templates/apply", summary="Apply template to parameters")
async def apply_template(request: ApplyTemplateRequest):
    """
    Apply a style template to transcription parameters.

    Takes base parameters and merges them with template configuration,
    returning updated parameters ready for podcast generation.

    Args:
        request: Template ID and base parameters

    Returns:
        Updated parameters with template applied
    """
    with telemetry.tracer.start_as_current_span("api.apply_template") as span:
        span.set_attribute("template_id", request.template_id)

        try:
            updated_params = StyleTemplateLibrary.apply_template(
                request.template_id,
                request.base_params
            )
            return {
                "status": "success",
                "params": updated_params
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PODCAST EDITING ENDPOINTS
# ============================================================================

@router.get("/podcast/{job_id}/versions", summary="List podcast versions")
async def list_podcast_versions(
    job_id: str,
    userId: str = Query(..., description="User ID")
):
    """
    List all versions of a podcast.

    Returns version history including edit counts and timestamps.

    Args:
        job_id: Job identifier
        userId: User identifier (for authorization)

    Returns:
        List of versions with metadata
    """
    with telemetry.tracer.start_as_current_span("api.list_versions") as span:
        span.set_attribute("job_id", job_id)

        try:
            versions = podcast_editor.list_versions(job_id)
            return {
                "job_id": job_id,
                "versions": versions,
                "count": len(versions)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/podcast/{job_id}/version/{version_id}", summary="Get specific version")
async def get_podcast_version(
    job_id: str,
    version_id: str,
    userId: str = Query(..., description="User ID")
):
    """
    Get a specific version of a podcast.

    Args:
        job_id: Job identifier
        version_id: Version identifier
        userId: User identifier

    Returns:
        Complete version data including dialogue
    """
    with telemetry.tracer.start_as_current_span("api.get_version") as span:
        span.set_attribute("job_id", job_id)
        span.set_attribute("version_id", version_id)

        version = podcast_editor.get_version(job_id, version_id)
        if not version:
            raise HTTPException(
                status_code=404,
                detail=f"Version {version_id} not found"
            )

        return version.dict()


@router.post("/podcast/{job_id}/edit", summary="Apply edit to podcast")
async def apply_podcast_edit(
    job_id: str,
    edit: DialogueEdit,
    userId: str = Query(..., description="User ID"),
    version_id: Optional[str] = Query(None, description="Version to edit from")
):
    """
    Apply an edit to a podcast, creating a new version.

    Supports update, delete, and insert operations on dialogue segments.

    Args:
        job_id: Job identifier
        edit: Edit to apply
        userId: User identifier
        version_id: Optional version to edit from (uses latest if not specified)

    Returns:
        New version with edit applied
    """
    with telemetry.tracer.start_as_current_span("api.apply_edit") as span:
        span.set_attribute("job_id", job_id)
        span.set_attribute("edit_action", edit.action)

        try:
            new_version = podcast_editor.apply_edit(job_id, edit, version_id)
            return {
                "status": "success",
                "version": new_version.dict()
            }
        except (ValueError, IndexError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


class BatchEditRequest(BaseModel):
    """Request to apply multiple edits."""
    edits: List[DialogueEdit] = Field(..., description="Edits to apply")
    version_id: Optional[str] = Field(None, description="Version to start from")


@router.post("/podcast/{job_id}/batch-edit", summary="Apply multiple edits")
async def apply_batch_edits(
    job_id: str,
    request: BatchEditRequest,
    userId: str = Query(..., description="User ID")
):
    """
    Apply multiple edits in sequence.

    Args:
        job_id: Job identifier
        request: Batch edit request with list of edits
        userId: User identifier

    Returns:
        New version with all edits applied
    """
    with telemetry.tracer.start_as_current_span("api.batch_edit") as span:
        span.set_attribute("job_id", job_id)
        span.set_attribute("edit_count", len(request.edits))

        try:
            new_version = podcast_editor.apply_multiple_edits(
                job_id,
                request.edits,
                request.version_id
            )
            return {
                "status": "success",
                "version": new_version.dict(),
                "edits_applied": len(request.edits)
            }
        except (ValueError, IndexError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/podcast/{job_id}/revert/{version_id}", summary="Revert to previous version")
async def revert_podcast_version(
    job_id: str,
    version_id: str,
    userId: str = Query(..., description="User ID")
):
    """
    Revert to a previous version (creates new version with old content).

    Args:
        job_id: Job identifier
        version_id: Version to revert to
        userId: User identifier

    Returns:
        New version with reverted content
    """
    with telemetry.tracer.start_as_current_span("api.revert_version") as span:
        span.set_attribute("job_id", job_id)
        span.set_attribute("revert_to", version_id)

        try:
            new_version = podcast_editor.revert_to_version(job_id, version_id)
            return {
                "status": "success",
                "message": f"Reverted to version {version_id}",
                "version": new_version.dict()
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/podcast/{job_id}/diff", summary="Get diff between versions")
async def get_version_diff(
    job_id: str,
    version_a: str = Query(..., description="First version ID"),
    version_b: str = Query(..., description="Second version ID"),
    userId: str = Query(..., description="User ID")
):
    """
    Get differences between two podcast versions.

    Args:
        job_id: Job identifier
        version_a: First version ID
        version_b: Second version ID
        userId: User identifier

    Returns:
        List of differences between versions
    """
    with telemetry.tracer.start_as_current_span("api.version_diff") as span:
        span.set_attribute("job_id", job_id)

        try:
            diffs = podcast_editor.get_diff(job_id, version_a, version_b)
            return {
                "job_id": job_id,
                "version_a": version_a,
                "version_b": version_b,
                "differences": diffs,
                "diff_count": len(diffs)
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@router.get("/podcast/{job_id}/export/{format}", summary="Export podcast transcript")
async def export_podcast(
    job_id: str,
    format: str,
    userId: str = Query(..., description="User ID"),
    version_id: Optional[str] = Query(None, description="Specific version to export"),
    include_metadata: bool = Query(True, description="Include metadata in export")
):
    """
    Export podcast transcript in various formats.

    Supported formats:
    - srt: SubRip subtitle format
    - vtt: WebVTT subtitle format
    - txt: Plain text transcript
    - md/markdown: Markdown format with metadata
    - json: JSON with timing and metadata

    Args:
        job_id: Job identifier
        format: Export format (srt, vtt, txt, md, json)
        userId: User identifier
        version_id: Optional specific version (uses latest if not specified)
        include_metadata: Whether to include metadata

    Returns:
        Formatted transcript with appropriate content-type
    """
    with telemetry.tracer.start_as_current_span("api.export_podcast") as span:
        span.set_attribute("job_id", job_id)
        span.set_attribute("format", format)

        try:
            # Get version (latest or specified)
            if version_id:
                version = podcast_editor.get_version(job_id, version_id)
                if not version:
                    raise HTTPException(404, f"Version {version_id} not found")
            else:
                version = podcast_editor.get_latest_version(job_id)
                if not version:
                    raise HTTPException(404, f"No versions found for job {job_id}")

            # Get metadata from version if available
            metadata = version.metadata if include_metadata else None

            # TODO: Get speaker names and duration from job metadata
            # For now, use defaults
            speaker_names = {
                "speaker-1": "Speaker 1",
                "speaker-2": "Speaker 2"
            }
            duration_minutes = metadata.get("duration", 15) if metadata else 15
            title = metadata.get("name", "Podcast Transcript") if metadata else "Podcast Transcript"

            # Export to format
            content = export_transcript(
                dialogue=version.dialogue,
                format=format,
                duration_minutes=duration_minutes,
                title=title,
                speaker_names=speaker_names,
                metadata=metadata
            )

            # Set appropriate content type and filename
            content_types = {
                "srt": "application/x-subrip",
                "vtt": "text/vtt",
                "txt": "text/plain",
                "txt_timestamps": "text/plain",
                "md": "text/markdown",
                "markdown": "text/markdown",
                "json": "application/json"
            }

            extensions = {
                "srt": "srt",
                "vtt": "vtt",
                "txt": "txt",
                "txt_timestamps": "txt",
                "md": "md",
                "markdown": "md",
                "json": "json"
            }

            content_type = content_types.get(format, "text/plain")
            extension = extensions.get(format, "txt")
            filename = f"podcast_{job_id}.{extension}"

            return Response(
                content=content,
                media_type=content_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/podcast/{job_id}/export-formats", summary="List available export formats")
async def list_export_formats(job_id: str):
    """
    List all available export formats for a podcast.

    Args:
        job_id: Job identifier

    Returns:
        List of supported export formats with descriptions
    """
    return {
        "job_id": job_id,
        "formats": [
            {
                "id": "srt",
                "name": "SubRip Subtitle",
                "description": "Standard subtitle format with timestamps",
                "extension": "srt",
                "use_case": "Video subtitles, accessibility"
            },
            {
                "id": "vtt",
                "name": "WebVTT",
                "description": "Web video text tracks format",
                "extension": "vtt",
                "use_case": "HTML5 video subtitles"
            },
            {
                "id": "txt",
                "name": "Plain Text",
                "description": "Simple text transcript",
                "extension": "txt",
                "use_case": "Reading, archiving"
            },
            {
                "id": "md",
                "name": "Markdown",
                "description": "Formatted markdown with metadata",
                "extension": "md",
                "use_case": "Documentation, blogs"
            },
            {
                "id": "json",
                "name": "JSON",
                "description": "Structured data with timing",
                "extension": "json",
                "use_case": "Data processing, integration"
            }
        ]
    }


# Health check for enhanced endpoints
@router.get("/health", summary="Health check for enhanced endpoints")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "enhanced-endpoints",
        "features": [
            "style_templates",
            "podcast_editing",
            "version_control",
            "multi_format_export"
        ]
    }
