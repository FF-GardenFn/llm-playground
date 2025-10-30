#!/usr/bin/env python3
"""
Tool Name: Codebase Search
Purpose: Search codebase for files, functions, classes, and patterns
Usage: python search_codebase.py [options]

This tool helps agents find relevant code, patterns, and integration points
before implementing new features.

Examples:
    python search_codebase.py --pattern "User.*Auth"
    python search_codebase.py --file-pattern "*.py" --content "def create"
    python search_codebase.py --class "UserService"
    python search_codebase.py --function "validate_email"
"""

import argparse
import sys
import json
import logging
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result"""
    file_path: str
    line_number: int
    line_content: str
    match_type: str  # 'pattern', 'class', 'function', 'import'
    context_before: List[str] = None
    context_after: List[str] = None

    def __post_init__(self):
        if self.context_before is None:
            self.context_before = []
        if self.context_after is None:
            self.context_after = []


class CodebaseSearcher:
    """Search codebase for patterns, classes, functions"""

    def __init__(self, root_dir: str = ".", exclude_dirs: List[str] = None):
        """
        Initialize searcher.

        Args:
            root_dir: Root directory to search from
            exclude_dirs: Directories to exclude (default: common exclusions)
        """
        self.root_dir = Path(root_dir).resolve()
        self.exclude_dirs = exclude_dirs or [
            '.git', '.svn', '__pycache__', 'node_modules',
            'venv', 'env', '.venv', 'dist', 'build',
            '.pytest_cache', '.mypy_cache', '.tox'
        ]
        logger.debug(f"Initialized searcher for: {self.root_dir}")

    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded"""
        parts = path.relative_to(self.root_dir).parts
        return any(exclude in parts for exclude in self.exclude_dirs)

    def find_files(self, pattern: str = "*") -> List[Path]:
        """
        Find files matching pattern.

        Args:
            pattern: Glob pattern (e.g., "*.py", "test_*.py")

        Returns:
            List of matching file paths
        """
        files = []
        for file_path in self.root_dir.rglob(pattern):
            if file_path.is_file() and not self.should_exclude(file_path):
                files.append(file_path)
        return sorted(files)

    def search_pattern(self, pattern: str, file_pattern: str = "*",
                      context_lines: int = 2) -> List[SearchResult]:
        """
        Search for regex pattern in files.

        Args:
            pattern: Regex pattern to search
            file_pattern: File glob pattern
            context_lines: Lines of context before/after match

        Returns:
            List of search results
        """
        results = []
        regex = re.compile(pattern)
        files = self.find_files(file_pattern)

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for i, line in enumerate(lines):
                    if regex.search(line):
                        result = SearchResult(
                            file_path=str(file_path.relative_to(self.root_dir)),
                            line_number=i + 1,
                            line_content=line.rstrip(),
                            match_type='pattern',
                            context_before=self._get_context(lines, i, -context_lines),
                            context_after=self._get_context(lines, i, context_lines)
                        )
                        results.append(result)

            except (UnicodeDecodeError, PermissionError) as e:
                logger.debug(f"Skipping {file_path}: {e}")
                continue

        return results

    def search_class(self, class_name: str, file_pattern: str = "*.py") -> List[SearchResult]:
        """
        Search for class definitions.

        Args:
            class_name: Class name to search for
            file_pattern: File pattern (default: *.py)

        Returns:
            List of class definitions found
        """
        # Python class definition pattern
        pattern = rf'^\s*class\s+{re.escape(class_name)}\s*[\(:]'
        return self.search_pattern(pattern, file_pattern, context_lines=5)

    def search_function(self, func_name: str, file_pattern: str = "*.py") -> List[SearchResult]:
        """
        Search for function definitions.

        Args:
            func_name: Function name to search for
            file_pattern: File pattern

        Returns:
            List of function definitions found
        """
        # Python function definition pattern (handles def and async def)
        pattern = rf'^\s*(?:async\s+)?def\s+{re.escape(func_name)}\s*\('
        return self.search_pattern(pattern, file_pattern, context_lines=3)

    def search_import(self, import_name: str, file_pattern: str = "*.py") -> List[SearchResult]:
        """
        Search for import statements.

        Args:
            import_name: Module/package name
            file_pattern: File pattern

        Returns:
            List of import statements found
        """
        pattern = rf'^\s*(?:from\s+.+\s+)?import\s+.*{re.escape(import_name)}'
        results = self.search_pattern(pattern, file_pattern, context_lines=0)
        for result in results:
            result.match_type = 'import'
        return results

    def _get_context(self, lines: List[str], index: int, num_lines: int) -> List[str]:
        """Get context lines around a match"""
        if num_lines > 0:
            # Lines after
            start = index + 1
            end = min(index + 1 + num_lines, len(lines))
        else:
            # Lines before
            start = max(0, index + num_lines)
            end = index

        return [line.rstrip() for line in lines[start:end]]

    def analyze_structure(self, file_pattern: str = "*.py") -> Dict[str, Any]:
        """
        Analyze codebase structure.

        Returns:
            Dictionary with structure information
        """
        files = self.find_files(file_pattern)

        analysis = {
            "total_files": len(files),
            "directories": set(),
            "file_types": {},
            "total_lines": 0,
            "files_by_directory": {}
        }

        for file_path in files:
            # Directory structure
            rel_path = file_path.relative_to(self.root_dir)
            if rel_path.parent != Path('.'):
                analysis["directories"].add(str(rel_path.parent))

                dir_name = str(rel_path.parent)
                if dir_name not in analysis["files_by_directory"]:
                    analysis["files_by_directory"][dir_name] = []
                analysis["files_by_directory"][dir_name].append(str(rel_path))

            # File type
            ext = file_path.suffix
            analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1

            # Line count
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    analysis["total_lines"] += sum(1 for _ in f)
            except (UnicodeDecodeError, PermissionError):
                pass

        analysis["directories"] = sorted(analysis["directories"])
        return analysis


def format_results(results: List[SearchResult], format_type: str = "text") -> str:
    """Format search results for output"""
    if format_type == "json":
        return json.dumps([asdict(r) for r in results], indent=2)

    elif format_type == "text":
        if not results:
            return "No matches found."

        output = []
        output.append(f"Found {len(results)} matches:\n")

        for result in results:
            output.append(f"\n{result.file_path}:{result.line_number}")

            if result.context_before:
                output.append("  ...")
                for line in result.context_before:
                    output.append(f"  {line}")

            output.append(f"> {result.line_content}")

            if result.context_after:
                for line in result.context_after:
                    output.append(f"  {line}")
                output.append("  ...")

        return "\n".join(output)

    elif format_type == "summary":
        if not results:
            return "No matches found."

        # Group by file
        by_file = {}
        for result in results:
            if result.file_path not in by_file:
                by_file[result.file_path] = []
            by_file[result.file_path].append(result.line_number)

        output = [f"Found {len(results)} matches in {len(by_file)} files:\n"]
        for file_path, line_numbers in sorted(by_file.items()):
            lines_str = ", ".join(f"L{n}" for n in sorted(line_numbers)[:5])
            if len(line_numbers) > 5:
                lines_str += f" ... (+{len(line_numbers) - 5} more)"
            output.append(f"  {file_path}: {lines_str}")

        return "\n".join(output)

    return str(results)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--pattern", "-p",
        help="Regex pattern to search for"
    )

    parser.add_argument(
        "--class", "-c",
        dest="class_name",
        help="Search for class definition"
    )

    parser.add_argument(
        "--function", "-f",
        dest="function_name",
        help="Search for function definition"
    )

    parser.add_argument(
        "--import", "-i",
        dest="import_name",
        help="Search for import statements"
    )

    parser.add_argument(
        "--file-pattern",
        default="*",
        help="File pattern to search (default: *)"
    )

    parser.add_argument(
        "--dir", "-d",
        default=".",
        help="Root directory to search (default: current directory)"
    )

    parser.add_argument(
        "--format",
        choices=["text", "json", "summary"],
        default="text",
        help="Output format (default: text)"
    )

    parser.add_argument(
        "--context",
        type=int,
        default=2,
        help="Lines of context to show (default: 2)"
    )

    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze codebase structure"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point"""
    try:
        args = parse_arguments()

        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        searcher = CodebaseSearcher(root_dir=args.dir)

        if args.analyze:
            analysis = searcher.analyze_structure(args.file_pattern)
            if args.format == "json":
                # Convert sets to lists for JSON serialization
                analysis["directories"] = list(analysis["directories"])
                print(json.dumps(analysis, indent=2))
            else:
                print(f"Codebase Analysis:")
                print(f"  Total files: {analysis['total_files']}")
                print(f"  Total lines: {analysis['total_lines']}")
                print(f"  Directories: {len(analysis['directories'])}")
                print(f"\nFile types:")
                for ext, count in sorted(analysis['file_types'].items()):
                    print(f"  {ext or '(no extension)'}: {count}")
            return 0

        # Perform search
        results = []

        if args.pattern:
            results = searcher.search_pattern(
                args.pattern,
                args.file_pattern,
                args.context
            )
        elif args.class_name:
            results = searcher.search_class(args.class_name, args.file_pattern)
        elif args.function_name:
            results = searcher.search_function(args.function_name, args.file_pattern)
        elif args.import_name:
            results = searcher.search_import(args.import_name, args.file_pattern)
        else:
            parser.error("Must specify --pattern, --class, --function, or --import")

        # Output results
        output = format_results(results, args.format)
        print(output)

        return 0

    except KeyboardInterrupt:
        logger.info("Search cancelled by user")
        return 130

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=args.verbose if 'args' in locals() else False)
        return 1


if __name__ == "__main__":
    sys.exit(main())
