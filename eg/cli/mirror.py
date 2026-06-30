"""Data-in-repo support: committed *.yml is the source; *.md is rendered on demand.

The repo commits ADR/BDD/CONTEXT as data (docs/adr/NNNN-slug.yml,
docs/bdd/NNNN-slug.yml, CONTEXT.yml). The rendered .md is git-ignored and
regenerated from the data whenever a legacy script (eg-tdd / eg-enforce) needs
it. No legacy reader is migrated; the wrappers render first.
"""
from __future__ import annotations

from pathlib import Path

import bdd_render
import precip_render
import store

GITIGNORE_HEADER = "# eg: rendered docs are generated from *.yml, do not commit"
GITIGNORE_LINES = ["docs/adr/*.md", "docs/bdd/*.md", "/CONTEXT.md"]


def ensure_gitignore(repo_root: Path) -> None:
    path = repo_root / ".gitignore"
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    have = {ln.strip() for ln in existing}
    missing = [ln for ln in GITIGNORE_LINES if ln not in have]
    if not missing:
        return
    block = ([""] if existing and existing[-1].strip() else []) + [GITIGNORE_HEADER, *missing]
    path.write_text("\n".join(existing + block) + "\n", encoding="utf-8")


def _render_one(data_path: Path) -> Path | None:
    data = store.load(data_path)
    if not isinstance(data, dict):
        return None
    schema = data.get("schema")
    md_path = data_path.with_suffix(".md")
    if schema == "eg-adr/v1":
        md_path.write_text(precip_render.render_adr(data), encoding="utf-8")
    elif schema == "eg-bdd/v1":
        md_path.write_text(bdd_render.render_bdd(data), encoding="utf-8")
    elif schema == "eg-context/v1":
        md_path = data_path.parent / "CONTEXT.md"
        md_path.write_text(precip_render.render_context(data), encoding="utf-8")
    else:
        return None
    return md_path


def render_all(repo_root: Path) -> list[Path]:
    """Regenerate every rendered .md from committed *.yml data."""
    out: list[Path] = []
    for sub in ("docs/adr", "docs/bdd"):
        d = repo_root / sub
        if d.is_dir():
            for yml in sorted(d.glob("*.yml")):
                rendered = _render_one(yml)
                if rendered:
                    out.append(rendered)
    ctx = repo_root / "CONTEXT.yml"
    if ctx.exists():
        rendered = _render_one(ctx)
        if rendered:
            out.append(rendered)
    if out:
        ensure_gitignore(repo_root)
    return out


def commit_doc(repo_root: Path, rel_dir: str, stem: str, data: dict) -> tuple[Path, Path]:
    """Write the data .yml (committed source) + render the sibling .md (ignored).
    rel_dir '' with stem 'CONTEXT' targets repo-root CONTEXT.yml / CONTEXT.md."""
    target_dir = repo_root / rel_dir if rel_dir else repo_root
    target_dir.mkdir(parents=True, exist_ok=True)
    yml_path = target_dir / f"{stem}.yml"
    store.dump(yml_path, data)
    md_path = _render_one(yml_path)
    ensure_gitignore(repo_root)
    return yml_path, md_path if md_path else yml_path.with_suffix(".md")
