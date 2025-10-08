#!/usr/bin/env python3
"""
Jinja renderer for patterns (with graceful fallback).

Provides a single convenience function:
    render_template_file(template_path, context, output_path=None)

- If Jinja2 is available, uses it to render the file.
- If not, falls back to Python's string.Template with ${var} placeholders.

Example:
    from prompt_systems.tools.render import render_template_file
    render_template_file("templates/charter.md.tmpl", {"title": "My Task"}, "charter.md")
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import importlib
try:
    jinja2 = importlib.import_module("jinja2")  # type: ignore
    _HAS_JINJA = True
except Exception:
    import string
    jinja2 = None  # type: ignore
    _HAS_JINJA = False


def render_template_file(template_path: str, context: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """Render a template file with the provided context.

    Args:
        template_path: Path to the template file.
        context: Variables to substitute.
        output_path: If provided, write rendered text to this path.

    Returns:
        The rendered string.
    """
    template_path = os.path.abspath(template_path)
    template_dir = os.path.dirname(template_path)
    template_name = os.path.basename(template_path)

    if _HAS_JINJA:
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False, trim_blocks=True, lstrip_blocks=True)  # type: ignore[attr-defined]
        tpl = env.get_template(template_name)
        rendered = tpl.render(**context)
    else:
        # Very basic fallback: ${var} replacement
        with open(template_path, "r", encoding="utf-8") as f:
            tpl_text = f.read()
        rendered = string.Template(tpl_text).safe_substitute(**context)

    if output_path:
        out_dir = os.path.dirname(os.path.abspath(output_path))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)

    return rendered


__all__ = ["render_template_file"]
