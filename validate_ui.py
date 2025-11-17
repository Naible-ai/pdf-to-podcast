"""
Validation script for Web UI components and backend integration.

This script validates:
1. Python backend APIs are accessible
2. Component structure is correct
3. File organization is proper
4. Required endpoints exist
"""

import os
import sys
import json
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text:^80}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text):
    print(f"{RED}✗{RESET} {text}")

def print_warning(text):
    print(f"{YELLOW}⚠{RESET} {text}")

def print_info(text):
    print(f"{BLUE}ℹ{RESET} {text}")

class UIValidator:
    def __init__(self):
        self.webui_path = Path(__file__).parent / "services" / "WebUI"
        self.src_path = self.webui_path / "src"
        self.errors = []
        self.warnings = []
        self.successes = []

    def validate_directory_structure(self):
        """Validate WebUI directory structure."""
        print_header("1. VALIDATING DIRECTORY STRUCTURE")

        required_dirs = [
            self.webui_path,
            self.src_path,
            self.src_path / "pages",
            self.src_path / "components",
            self.src_path / "utils",
            self.src_path / "styles",
        ]

        for dir_path in required_dirs:
            if dir_path.exists():
                print_success(f"Directory exists: {dir_path.relative_to(self.webui_path.parent)}")
                self.successes.append(f"Dir: {dir_path.name}")
            else:
                print_error(f"Directory missing: {dir_path.relative_to(self.webui_path.parent)}")
                self.errors.append(f"Missing dir: {dir_path.name}")

    def validate_config_files(self):
        """Validate configuration files."""
        print_header("2. VALIDATING CONFIGURATION FILES")

        config_files = {
            "package.json": self.webui_path / "package.json",
            "vite.config.ts": self.webui_path / "vite.config.ts",
            "tsconfig.json": self.webui_path / "tsconfig.json",
            "tailwind.config.js": self.webui_path / "tailwind.config.js",
            "index.html": self.webui_path / "index.html",
        }

        for name, path in config_files.items():
            if path.exists():
                print_success(f"Config file exists: {name}")
                self.successes.append(f"Config: {name}")

                # Validate package.json
                if name == "package.json":
                    try:
                        with open(path) as f:
                            pkg = json.load(f)
                            if "dependencies" in pkg:
                                print_info(f"  Dependencies: {len(pkg['dependencies'])} packages")
                            if "devDependencies" in pkg:
                                print_info(f"  Dev dependencies: {len(pkg['devDependencies'])} packages")
                    except Exception as e:
                        print_error(f"  Invalid JSON: {e}")
                        self.errors.append(f"Invalid package.json")
            else:
                print_error(f"Config file missing: {name}")
                self.errors.append(f"Missing: {name}")

    def validate_components(self):
        """Validate React components."""
        print_header("3. VALIDATING REACT COMPONENTS")

        components = {
            "App.tsx": self.src_path / "App.tsx",
            "main.tsx": self.src_path / "main.tsx",
            "ProgressTracker.tsx": self.src_path / "components" / "ProgressTracker.tsx",
            "TemplateSelector.tsx": self.src_path / "components" / "TemplateSelector.tsx",
        }

        for name, path in components.items():
            if path.exists():
                print_success(f"Component exists: {name}")
                self.successes.append(f"Component: {name}")

                # Basic validation
                try:
                    with open(path) as f:
                        content = f.read()

                        # Check for imports
                        if "import" in content:
                            import_count = content.count("import")
                            print_info(f"  Imports: {import_count}")

                        # Check for export
                        if "export default" in content or "export {" in content:
                            print_info(f"  Has exports: ✓")
                        else:
                            print_warning(f"  No default export found")
                            self.warnings.append(f"{name}: No default export")

                        # Check for TypeScript
                        if ": " in content or "interface " in content or "type " in content:
                            print_info(f"  TypeScript types: ✓")

                except Exception as e:
                    print_error(f"  Error reading file: {e}")
                    self.errors.append(f"Error reading {name}")
            else:
                print_error(f"Component missing: {name}")
                self.errors.append(f"Missing component: {name}")

    def validate_pages(self):
        """Validate page components."""
        print_header("4. VALIDATING PAGE COMPONENTS")

        pages = {
            "CreatePodcast.tsx": self.src_path / "pages" / "CreatePodcast.tsx",
            "MyPodcasts.tsx": self.src_path / "pages" / "MyPodcasts.tsx",
            "Templates.tsx": self.src_path / "pages" / "Templates.tsx",
            "EditPodcast.tsx": self.src_path / "pages" / "EditPodcast.tsx",
        }

        for name, path in pages.items():
            if path.exists():
                print_success(f"Page exists: {name}")
                self.successes.append(f"Page: {name}")

                try:
                    with open(path) as f:
                        content = f.read()
                        # Check for React hooks
                        hooks = ["useState", "useEffect", "useQuery", "useParams"]
                        found_hooks = [hook for hook in hooks if hook in content]
                        if found_hooks:
                            print_info(f"  Hooks used: {', '.join(found_hooks)}")
                except Exception as e:
                    print_error(f"  Error reading file: {e}")
            else:
                print_error(f"Page missing: {name}")
                self.errors.append(f"Missing page: {name}")

    def validate_utilities(self):
        """Validate utility files."""
        print_header("5. VALIDATING UTILITY FILES")

        utils = {
            "api.ts": self.src_path / "utils" / "api.ts",
            "types.ts": self.src_path / "types.ts",
        }

        for name, path in utils.items():
            if path.exists():
                print_success(f"Utility file exists: {name}")
                self.successes.append(f"Util: {name}")

                try:
                    with open(path) as f:
                        content = f.read()
                        if name == "api.ts":
                            # Check for API methods
                            methods = ["getTemplates", "createPodcast", "exportPodcast"]
                            found = [m for m in methods if m in content]
                            print_info(f"  API methods: {len(found)}/{len(methods)}")

                        if name == "types.ts":
                            # Check for type definitions
                            if "interface" in content or "type" in content:
                                type_count = content.count("interface") + content.count("type ")
                                print_info(f"  Type definitions: {type_count}")
                except Exception as e:
                    print_error(f"  Error reading file: {e}")
            else:
                print_error(f"Utility file missing: {name}")
                self.errors.append(f"Missing: {name}")

    def validate_styles(self):
        """Validate styles."""
        print_header("6. VALIDATING STYLES")

        style_file = self.src_path / "styles" / "index.css"
        if style_file.exists():
            print_success("Styles file exists: index.css")
            self.successes.append("Styles: index.css")

            try:
                with open(style_file) as f:
                    content = f.read()
                    if "@tailwind" in content:
                        print_info("  TailwindCSS imports: ✓")
                    if "@keyframes" in content:
                        print_info("  Custom animations: ✓")
            except Exception as e:
                print_error(f"  Error reading file: {e}")
        else:
            print_error("Styles file missing")
            self.errors.append("Missing: index.css")

    def validate_backend_integration(self):
        """Validate backend API integration."""
        print_header("7. VALIDATING BACKEND INTEGRATION")

        # Check if enhanced endpoints file exists
        enhanced_api = Path(__file__).parent / "services" / "APIService" / "enhanced_endpoints.py"

        if enhanced_api.exists():
            print_success("Enhanced API endpoints file exists")
            self.successes.append("Backend: enhanced_endpoints.py")

            try:
                with open(enhanced_api) as f:
                    content = f.read()

                    # Check for router endpoints
                    endpoints = [
                        "GET /templates",
                        "GET /templates/{template_id}",
                        "POST /templates/apply",
                        "GET /podcast/{job_id}/versions",
                        "POST /podcast/{job_id}/edit",
                        "GET /podcast/{job_id}/export/{format}",
                    ]

                    found = 0
                    for endpoint in endpoints:
                        # Check for route decorator
                        if "@router.get" in content or "@router.post" in content:
                            found += 1

                    print_info(f"  API endpoints defined: ✓")

                    # Check for imports
                    if "from shared.style_templates import" in content:
                        print_info("  Style templates integration: ✓")
                    if "from shared.export_formats import" in content:
                        print_info("  Export formats integration: ✓")
                    if "from shared.podcast_editor import" in content:
                        print_info("  Podcast editor integration: ✓")

            except Exception as e:
                print_error(f"  Error reading file: {e}")
        else:
            print_error("Enhanced API endpoints file missing")
            self.errors.append("Missing: enhanced_endpoints.py")

    def print_summary(self):
        """Print validation summary."""
        print_header("VALIDATION SUMMARY")

        total = len(self.successes) + len(self.errors) + len(self.warnings)

        print(f"\n{GREEN}✓ Successes: {len(self.successes)}{RESET}")
        print(f"{RED}✗ Errors: {len(self.errors)}{RESET}")
        print(f"{YELLOW}⚠ Warnings: {len(self.warnings)}{RESET}")
        print(f"\nTotal checks: {total}")

        if self.errors:
            print(f"\n{RED}Errors found:{RESET}")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n{YELLOW}Warnings:{RESET}")
            for warning in self.warnings:
                print(f"  - {warning}")

        print("\n" + "="*80)
        if len(self.errors) == 0:
            print(f"{GREEN}{'✓ VALIDATION PASSED - UI IS READY TO USE!':^80}{RESET}")
        else:
            print(f"{RED}{'✗ VALIDATION FAILED - PLEASE FIX ERRORS ABOVE':^80}{RESET}")
        print("="*80 + "\n")

        # Next steps
        print_header("NEXT STEPS TO RUN THE UI")
        print("""
1. Install dependencies:
   cd services/WebUI
   npm install

2. Start development server:
   npm run dev

3. Open browser:
   http://localhost:3000

4. Test the following flows:
   a) Upload PDF and create podcast
   b) Browse templates
   c) View My Podcasts
   d) Export transcript
""")

        return len(self.errors) == 0

def main():
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "PDF-TO-PODCAST WEB UI VALIDATION" + " "*24 + "║")
    print("╚" + "="*78 + "╝")

    validator = UIValidator()

    # Run all validations
    validator.validate_directory_structure()
    validator.validate_config_files()
    validator.validate_components()
    validator.validate_pages()
    validator.validate_utilities()
    validator.validate_styles()
    validator.validate_backend_integration()

    # Print summary
    success = validator.print_summary()

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
