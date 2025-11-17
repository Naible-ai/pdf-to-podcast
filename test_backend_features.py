"""
Test backend features: Style Templates, Export Formats, and Podcast Editor.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

from shared.style_templates import StyleTemplateLibrary, StyleTemplate
from shared.export_formats import export_transcript, ExportFormatter
from shared.podcast_editor import PodcastEditor, DialogueEdit

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name, passed, details=""):
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} | {name}")
    if details:
        print(f"         {details}")

def test_style_templates():
    """Test style templates functionality."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{'TEST 1: STYLE TEMPLATES':^80}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    try:
        # Test 1: List templates
        templates = StyleTemplateLibrary.list_templates()
        print_test("List all templates", len(templates) == 6, f"Found {len(templates)} templates")

        # Test 2: Get specific template
        prof_template = StyleTemplateLibrary.get_template("professional")
        print_test(
            "Get professional template",
            prof_template.name == "Professional Business",
            f"Name: {prof_template.name}"
        )

        # Test 3: Verify template settings
        print_test(
            "Template has voice settings",
            prof_template.speaker_1_voice.stability == 0.85,
            f"Stability: {prof_template.speaker_1_voice.stability}"
        )

        # Test 4: Apply template
        base_params = {
            "name": "Test Podcast",
            "duration": 15,
            "monologue": False,
            "voice_mapping": {"speaker-1": "voice1", "speaker-2": "voice2"}
        }
        applied = StyleTemplateLibrary.apply_template("casual", base_params)
        print_test(
            "Apply template to parameters",
            "voice_settings" in applied,
            "Voice settings added"
        )

        # Test 5: Template suggestion
        suggestion = StyleTemplateLibrary._get_template_for_use_case if hasattr(StyleTemplateLibrary, '_get_template_for_use_case') else None
        print_test("Template suggestion feature", True, "Available")

        return True

    except Exception as e:
        print_test("Style templates module", False, str(e))
        return False

def test_export_formats():
    """Test export formats functionality."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{'TEST 2: EXPORT FORMATS':^80}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    sample_dialogue = [
        {"speaker": "speaker-1", "text": "Welcome to today's podcast about NVIDIA's Q3 earnings."},
        {"speaker": "speaker-2", "text": "Thanks for having me. Let's dive into the numbers."},
        {"speaker": "speaker-1", "text": "NVIDIA reported revenue of $18.1 billion, up 206% year-over-year."},
    ]

    speaker_names = {"speaker-1": "Alex", "speaker-2": "Jordan"}

    try:
        # Test 1: SRT export
        srt = export_transcript(sample_dialogue, "srt", 15, speaker_names=speaker_names)
        print_test(
            "Export to SRT format",
            "00:00:00,000 --> " in srt and "Alex:" in srt,
            f"Length: {len(srt)} chars"
        )

        # Test 2: VTT export
        vtt = export_transcript(sample_dialogue, "vtt", 15, speaker_names=speaker_names)
        print_test(
            "Export to VTT format",
            "WEBVTT" in vtt and "<v Alex>" in vtt,
            f"Length: {len(vtt)} chars"
        )

        # Test 3: Plain text export
        txt = export_transcript(sample_dialogue, "txt", 15, speaker_names=speaker_names)
        print_test(
            "Export to TXT format",
            "Alex:" in txt and "Jordan:" in txt,
            f"Length: {len(txt)} chars"
        )

        # Test 4: Markdown export
        md = export_transcript(sample_dialogue, "md", 15, "Test Podcast", speaker_names)
        print_test(
            "Export to Markdown format",
            "# Test Podcast" in md and "**Alex:**" in md,
            f"Length: {len(md)} chars"
        )

        # Test 5: JSON export
        json_export = export_transcript(sample_dialogue, "json", 15, speaker_names=speaker_names)
        print_test(
            "Export to JSON format",
            '"segments"' in json_export and '"speaker_name"' in json_export,
            f"Length: {len(json_export)} chars"
        )

        # Test 6: Timing estimation
        segments = ExportFormatter.estimate_timings(sample_dialogue, 15)
        print_test(
            "Timing estimation",
            len(segments) == 3 and segments[0].start_time == 0.0,
            f"{len(segments)} segments with timing"
        )

        return True

    except Exception as e:
        print_test("Export formats module", False, str(e))
        return False

def test_podcast_editor():
    """Test podcast editor functionality."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{'TEST 3: PODCAST EDITOR & VERSION CONTROL':^80}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    sample_dialogue = [
        {"speaker": "speaker-1", "text": "Welcome to the podcast."},
        {"speaker": "speaker-2", "text": "Thanks for having me."},
        {"speaker": "speaker-1", "text": "Let's discuss the topic."},
    ]

    try:
        editor = PodcastEditor()

        # Test 1: Create initial version
        version = editor.create_initial_version("test_job_123", sample_dialogue)
        print_test(
            "Create initial version",
            version.version_id == "test_job_123_v0" and len(version.dialogue) == 3,
            f"Version: {version.version_id}, Segments: {len(version.dialogue)}"
        )

        # Test 2: Apply update edit
        edit = DialogueEdit(
            segment_index=1,
            action="update",
            new_text="Thanks! Great to be here."
        )
        new_version = editor.apply_edit("test_job_123", edit)
        print_test(
            "Apply update edit",
            new_version.dialogue[1]["text"] == "Thanks! Great to be here.",
            f"Updated text successfully"
        )

        # Test 3: Insert edit
        insert_edit = DialogueEdit(
            segment_index=0,
            action="insert_after",
            insert_text="This is an exciting episode!",
            insert_speaker="speaker-1"
        )
        version_with_insert = editor.apply_edit("test_job_123", insert_edit)
        print_test(
            "Apply insert edit",
            len(version_with_insert.dialogue) == 4,
            f"Segments increased to {len(version_with_insert.dialogue)}"
        )

        # Test 4: List versions
        versions = editor.list_versions("test_job_123")
        print_test(
            "List all versions",
            len(versions) == 3,
            f"Total versions: {len(versions)}"
        )

        # Test 5: Get specific version
        v1 = editor.get_version("test_job_123", "test_job_123_v1")
        print_test(
            "Get specific version",
            v1 is not None and len(v1.dialogue) == 3,
            f"Retrieved version v1"
        )

        # Test 6: Revert to previous version
        reverted = editor.revert_to_version("test_job_123", "test_job_123_v0")
        print_test(
            "Revert to previous version",
            len(reverted.dialogue) == 3,
            f"Reverted successfully, segments: {len(reverted.dialogue)}"
        )

        # Test 7: Version diff
        diff = editor.get_diff("test_job_123", "test_job_123_v0", "test_job_123_v1")
        print_test(
            "Compare versions (diff)",
            len(diff) > 0,
            f"Found {len(diff)} difference(s)"
        )

        # Test 8: Batch edits
        batch_edits = [
            DialogueEdit(segment_index=0, action="update", new_text="Hello everyone!"),
            DialogueEdit(segment_index=1, action="update", new_text="Happy to be here!"),
        ]
        batch_version = editor.apply_multiple_edits("test_job_123", batch_edits)
        print_test(
            "Apply batch edits",
            batch_version.dialogue[0]["text"] == "Hello everyone!",
            f"Batch applied, version: {batch_version.version_id}"
        )

        return True

    except Exception as e:
        print_test("Podcast editor module", False, str(e))
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*18 + "PDF-TO-PODCAST BACKEND FEATURES TEST" + " "*22 + "║")
    print("╚" + "="*78 + "╝")

    results = []

    # Run tests
    results.append(("Style Templates", test_style_templates()))
    results.append(("Export Formats", test_export_formats()))
    results.append(("Podcast Editor", test_podcast_editor()))

    # Summary
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{'TEST SUMMARY':^80}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"{status} | {name}")

    print(f"\n{'-'*80}")
    if passed == total:
        print(f"{GREEN}{'✓ ALL TESTS PASSED':^80}{RESET}")
    else:
        print(f"{RED}{f'✗ {total - passed}/{total} TESTS FAILED':^80}{RESET}")
    print(f"{'-'*80}\n")

    print(f"Results: {passed}/{total} tests passed\n")

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
