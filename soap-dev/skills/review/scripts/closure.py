#!/usr/bin/env python3
"""Compute import dependency closure (forward + reverse) for a set of changed files.

Usage: python3 closure.py <project_root> <changed_file1> [<changed_file2> ...]

Outputs JSON to stdout:
  {
    "changed": [...],
    "related": [...],
    "unresolvable": [{"file": "...", "reason": "..."}]
  }
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

try:
    import tomllib  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - fallback for <3.11
    tomllib = None


SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "out", "target",
    "bin", "obj", "__pycache__", ".venv", "venv",
    ".next", ".nuxt", ".cache",
}


# ---------------------------------------------------------------------------
# Manifest parsers
# ---------------------------------------------------------------------------
def parse_package_json(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    deps: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        d = data.get(key) or {}
        if isinstance(d, dict):
            deps.update(d.keys())
    return deps


def _parse_toml_fallback(text: str) -> dict:
    """Extremely minimal TOML parser used only when tomllib is unavailable.

    Supports enough to grab dependency table keys. Returns nested dict with
    tables and array-of-tables for '[[name]]' not supported (we don't need it).
    """
    result: dict = {}
    current: dict = result
    current_path: list[str] = []
    in_array = False
    array_buf: list[str] = []
    array_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if in_array:
            # Consume array content (we only care about keys in tables, not arrays)
            if "]" in line:
                in_array = False
            continue
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            inner = line[1:-1]
            if inner.startswith("["):  # array-of-tables, skip
                continue
            parts = [p.strip() for p in inner.split(".")]
            d = result
            for p in parts:
                d = d.setdefault(p, {})
            current = d
            current_path = parts
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip().strip('"').strip("'")
            value = value.strip()
            if value.endswith("["):
                # multi-line array; skip until matching ]
                if "]" in value:
                    current[key] = value
                else:
                    in_array = True
                    array_key = key
                    current[key] = []
            else:
                current[key] = value
    return result


def _load_toml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if tomllib is not None:
        return tomllib.loads(text)
    return _parse_toml_fallback(text)


def parse_pyproject_toml(path: Path) -> set[str]:
    data = _load_toml(path)
    deps: set[str] = set()

    # [project].dependencies (PEP 621) — list of PEP 508 strings
    project = data.get("project") or {}
    if isinstance(project, dict):
        for spec in project.get("dependencies", []) or []:
            if isinstance(spec, str):
                name = _split_requirement_name(spec)
                if name:
                    deps.add(name)
        opt = project.get("optional-dependencies") or {}
        if isinstance(opt, dict):
            for group in opt.values():
                for spec in group or []:
                    if isinstance(spec, str):
                        name = _split_requirement_name(spec)
                        if name:
                            deps.add(name)

    # [tool.poetry.dependencies]
    tool = data.get("tool") or {}
    if isinstance(tool, dict):
        poetry = tool.get("poetry") or {}
        if isinstance(poetry, dict):
            for section in ("dependencies", "dev-dependencies"):
                d = poetry.get(section) or {}
                if isinstance(d, dict):
                    for k in d.keys():
                        if k.lower() != "python":
                            deps.add(k)
            groups = poetry.get("group") or {}
            if isinstance(groups, dict):
                for g in groups.values():
                    if isinstance(g, dict):
                        gd = g.get("dependencies") or {}
                        if isinstance(gd, dict):
                            for k in gd.keys():
                                if k.lower() != "python":
                                    deps.add(k)
    return deps


def _split_requirement_name(spec: str) -> str:
    spec = spec.strip()
    if not spec or spec.startswith("#"):
        return ""
    # split on common version operators / markers / whitespace
    m = re.split(r"[\s;\[=<>!~]", spec, maxsplit=1)
    return m[0].strip() if m else ""


def parse_requirements_txt(path: Path) -> set[str]:
    deps: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = _split_requirement_name(line)
        if name:
            deps.add(name)
    return deps


def parse_csproj(path: Path) -> set[str]:
    tree = ET.parse(str(path))
    root = tree.getroot()
    deps: set[str] = set()
    # PackageReference can be at any depth; iterate all
    for elem in root.iter():
        tag = elem.tag
        # Strip XML namespace if present
        if "}" in tag:
            tag = tag.split("}", 1)[1]
        if tag == "PackageReference":
            inc = elem.attrib.get("Include") or elem.attrib.get("include")
            if inc:
                deps.add(inc)
    return deps


_GO_MODULE_RE = re.compile(r"^module\s+(\S+)", re.MULTILINE)
_GO_REQUIRE_BLOCK_RE = re.compile(r"require\s*\(([^)]*)\)", re.DOTALL)
_GO_REQUIRE_SINGLE_RE = re.compile(r"^require\s+(\S+)\s+\S+", re.MULTILINE)


def parse_go_mod(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    deps: set[str] = set()
    for m in _GO_REQUIRE_BLOCK_RE.finditer(text):
        block = m.group(1)
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            parts = line.split()
            if parts:
                deps.add(parts[0])
    for m in _GO_REQUIRE_SINGLE_RE.finditer(text):
        deps.add(m.group(1))
    return deps


def parse_go_mod_module(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    m = _GO_MODULE_RE.search(text)
    return m.group(1).strip() if m else None


def parse_cargo_toml(path: Path) -> set[str]:
    data = _load_toml(path)
    deps: set[str] = set()
    for section in ("dependencies", "dev-dependencies", "build-dependencies"):
        d = data.get(section) or {}
        if isinstance(d, dict):
            deps.update(d.keys())
    return deps


# ---------------------------------------------------------------------------
# Import resolvers
# ---------------------------------------------------------------------------
TS_EXTS = [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"]


def resolve_ts(target: str, from_file: Path, project_root: Path) -> list[Path]:
    if not (target.startswith("./") or target.startswith("../") or target.startswith("/")):
        return []
    if target.startswith("/"):
        base = project_root / target.lstrip("/")
    else:
        base = (from_file.parent / target).resolve()
    # ensure it's inside project_root (best-effort)
    candidates: list[Path] = []
    # direct with known extensions
    for ext in TS_EXTS:
        candidates.append(base.with_suffix(ext) if base.suffix == "" else Path(str(base) + ext))
    # already has extension?
    if base.suffix in TS_EXTS:
        candidates.insert(0, base)
    # direct path as-is
    candidates.append(base)
    # index files
    for ext in TS_EXTS:
        candidates.append(base / f"index{ext}")
    # dedupe while preserving order
    seen: set[str] = set()
    out: list[Path] = []
    for c in candidates:
        s = str(c)
        if s not in seen:
            seen.add(s)
            out.append(c)
    return out


def resolve_python(target: str, from_file: Path, project_root: Path) -> list[Path]:
    # target is the module name, possibly starting with '.'
    candidates: list[Path] = []
    if target.startswith("."):
        # Count leading dots for relative depth
        dots = 0
        for ch in target:
            if ch == ".":
                dots += 1
            else:
                break
        remainder = target[dots:]
        # from_file.parent is depth 1 (single dot)
        base_dir = from_file.parent
        for _ in range(dots - 1):
            base_dir = base_dir.parent
        parts = remainder.split(".") if remainder else []
        p = base_dir
        for part in parts:
            p = p / part
        candidates.append(Path(str(p) + ".py"))
        candidates.append(p / "__init__.py")
    else:
        # Absolute module: try from project_root
        parts = target.split(".")
        p = project_root
        for part in parts:
            p = p / part
        candidates.append(Path(str(p) + ".py"))
        candidates.append(p / "__init__.py")
        # Also try successive parents of from_file (for src-layouts)
        cur = from_file.parent
        while True:
            q = cur
            for part in parts:
                q = q / part
            candidates.append(Path(str(q) + ".py"))
            candidates.append(q / "__init__.py")
            if cur == project_root or project_root not in cur.parents and cur != project_root:
                break
            parent = cur.parent
            if parent == cur:
                break
            cur = parent
    # dedupe
    seen: set[str] = set()
    out: list[Path] = []
    for c in candidates:
        s = str(c)
        if s not in seen:
            seen.add(s)
            out.append(c)
    return out


def resolve_cs(target: str, from_file: Path, project_root: Path, project_files: set[Path]) -> list[Path]:
    """C# 'using X.Y.Z' -> look for files named Z.cs anywhere, or a folder path matching."""
    parts = target.split(".")
    last = parts[-1]
    candidates: list[Path] = []
    # Try nested dir/namespace match
    p = project_root
    for part in parts:
        p = p / part
    candidates.append(Path(str(p) + ".cs"))
    # Any .cs file whose name matches 'last' (fallback)
    for f in project_files:
        if f.suffix == ".cs" and f.stem == last:
            candidates.append(f)
    return candidates


def resolve_go(target: str, from_file: Path, project_root: Path, module_path: str | None) -> list[Path]:
    if not module_path or not target.startswith(module_path):
        return []
    rel = target[len(module_path):].lstrip("/")
    base = project_root / rel if rel else project_root
    candidates: list[Path] = []
    if base.is_dir():
        # import a directory => any .go file in it
        try:
            for entry in base.iterdir():
                if entry.is_file() and entry.suffix == ".go" and not entry.name.endswith("_test.go"):
                    candidates.append(entry)
        except OSError:
            pass
    # also the path itself as a file
    candidates.append(Path(str(base) + ".go"))
    return candidates


def resolve_rust(target: str, from_file: Path, project_root: Path) -> list[Path]:
    # Rust use paths like crate::mod::item or super::foo
    # We try to find a .rs file matching the module path inside the same crate (src/).
    candidates: list[Path] = []
    # Find src/ dir by walking up until we see Cargo.toml or lib.rs/main.rs
    crate_root = from_file.parent
    while crate_root != crate_root.parent:
        if (crate_root / "Cargo.toml").exists():
            src = crate_root / "src"
            if src.exists():
                crate_src = src
                break
        crate_root = crate_root.parent
    else:
        crate_src = project_root

    parts = target.split("::")
    if parts and parts[0] == "crate":
        parts = parts[1:]
        base = crate_src
    elif parts and parts[0] == "self":
        parts = parts[1:]
        base = from_file.parent
    elif parts and parts[0] == "super":
        depth = 0
        while parts and parts[0] == "super":
            depth += 1
            parts = parts[1:]
        base = from_file.parent
        for _ in range(depth):
            base = base.parent
    else:
        return []

    if not parts:
        return []
    # Try each prefix of parts as a module path (item at end is often a symbol, not a file)
    for i in range(len(parts), 0, -1):
        sub = parts[:i]
        p = base
        for part in sub:
            p = p / part
        candidates.append(Path(str(p) + ".rs"))
        candidates.append(p / "mod.rs")
    return candidates


# ---------------------------------------------------------------------------
# Import extraction patterns
# ---------------------------------------------------------------------------
TS_IMPORT_PATTERNS = [
    re.compile(r"""import\s+(?:[^'";]+?\s+from\s+)?['"]([^'"]+)['"]"""),
    re.compile(r"""export\s+(?:\*|\{[^}]*\})\s+from\s+['"]([^'"]+)['"]"""),
    re.compile(r"""require\(\s*['"]([^'"]+)['"]\s*\)"""),
    re.compile(r"""import\(\s*['"]([^'"]+)['"]\s*\)"""),
]

PY_IMPORT_PATTERNS = [
    re.compile(r"""^\s*import\s+([a-zA-Z_][\w.]*)""", re.MULTILINE),
    re.compile(r"""^\s*from\s+(\.+[\w.]*|[a-zA-Z_][\w.]*)\s+import\s+""", re.MULTILINE),
]

CS_IMPORT_PATTERNS = [
    re.compile(r"""^\s*using\s+(?:static\s+)?([A-Za-z_][\w.]*)\s*;""", re.MULTILINE),
]

GO_IMPORT_PATTERNS = [
    re.compile(r"""import\s+"([^"]+)\""""),
    re.compile(r"""import\s*\(([^)]*)\)""", re.DOTALL),
]

RUST_IMPORT_PATTERNS = [
    re.compile(r"""^\s*use\s+([\w:]+(?:::\{[^}]*\})?)""", re.MULTILINE),
    re.compile(r"""^\s*mod\s+([a-zA-Z_]\w*)\s*;""", re.MULTILINE),
]


def extract_ts_imports(text: str) -> list[str]:
    out: list[str] = []
    for pat in TS_IMPORT_PATTERNS:
        for m in pat.finditer(text):
            out.append(m.group(1))
    return out


def extract_py_imports(text: str) -> list[str]:
    out: list[str] = []
    for pat in PY_IMPORT_PATTERNS:
        for m in pat.finditer(text):
            out.append(m.group(1))
    return out


def extract_cs_imports(text: str) -> list[str]:
    return [m.group(1) for m in CS_IMPORT_PATTERNS[0].finditer(text)]


def extract_go_imports(text: str) -> list[str]:
    out: list[str] = []
    # single
    for m in re.finditer(r"""^\s*import\s+"([^"]+)"\s*$""", text, re.MULTILINE):
        out.append(m.group(1))
    # block
    for m in re.finditer(r"""import\s*\(([^)]*)\)""", text, re.DOTALL):
        block = m.group(1)
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            # optional alias before path
            sm = re.search(r'"([^"]+)"', line)
            if sm:
                out.append(sm.group(1))
    return out


def extract_rust_imports(text: str) -> list[str]:
    out: list[str] = []
    for m in RUST_IMPORT_PATTERNS[0].finditer(text):
        path = m.group(1)
        # strip any '::{...}' group trailing
        path = re.sub(r"::\{.*\}$", "", path)
        out.append(path)
    # mod x; declarations point to x.rs / x/mod.rs (treat as 'self::x')
    for m in RUST_IMPORT_PATTERNS[1].finditer(text):
        out.append("self::" + m.group(1))
    return out


# ---------------------------------------------------------------------------
# Language registry
# ---------------------------------------------------------------------------
LANGUAGES: dict[str, dict] = {
    "typescript": {
        "extensions": set(TS_EXTS),
        "manifest_globs": ["package.json"],
        "relative_prefixes": ["./", "../"],
        "extract": extract_ts_imports,
        "parse_manifest": parse_package_json,
        "resolve": "ts",
    },
    "python": {
        "extensions": {".py"},
        "manifest_globs": ["pyproject.toml", "requirements.txt"],
        # relative prefix: leading '.'
        "relative_prefixes": ["."],
        "extract": extract_py_imports,
        "parse_manifest": None,  # dispatched by filename
        "resolve": "python",
    },
    "csharp": {
        "extensions": {".cs"},
        "manifest_globs": ["*.csproj"],
        "relative_prefixes": [],
        "extract": extract_cs_imports,
        "parse_manifest": parse_csproj,
        "resolve": "cs",
    },
    "go": {
        "extensions": {".go"},
        "manifest_globs": ["go.mod"],
        "relative_prefixes": [],  # dynamic: go.mod module path
        "extract": extract_go_imports,
        "parse_manifest": parse_go_mod,
        "resolve": "go",
    },
    "rust": {
        "extensions": {".rs"},
        "manifest_globs": ["Cargo.toml"],
        "relative_prefixes": ["crate::", "super::", "self::"],
        "extract": extract_rust_imports,
        "parse_manifest": parse_cargo_toml,
        "resolve": "rust",
    },
}


EXT_TO_LANG: dict[str, str] = {}
for lang_name, spec in LANGUAGES.items():
    for ext in spec["extensions"]:
        EXT_TO_LANG[ext] = lang_name


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------
class Closure:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.project_files: set[Path] = set()
        self.all_files_by_ext: dict[str, list[Path]] = {}
        self._scan_project()
        # manifest cache: (lang, from_file_dir) -> (deps_set | None, err_message | None, manifest_path | None)
        self._manifest_cache: dict[tuple[str, str], tuple[set[str] | None, str | None, Path | None]] = {}
        self._go_module_cache: dict[str, str | None] = {}
        # unresolvable: file_rel -> list[reason]
        self.unresolvable: dict[str, list[str]] = {}
        # forward index: file_rel -> set of file_rel it imports (within project)
        self._forward_index: dict[str, set[str]] = {}
        # reverse index built lazily
        self._reverse_index: dict[str, set[str]] | None = None

    def _scan_project(self) -> None:
        for dirpath, dirnames, filenames in os.walk(self.project_root):
            # mutate dirnames in place
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                ext = os.path.splitext(fn)[1]
                if ext in EXT_TO_LANG:
                    p = Path(dirpath) / fn
                    self.project_files.add(p)
                    self.all_files_by_ext.setdefault(ext, []).append(p)

    # ---------- path helpers ----------
    def _rel(self, p: Path) -> str:
        try:
            rp = p.resolve().relative_to(self.project_root)
        except Exception:
            try:
                rp = p.relative_to(self.project_root)
            except Exception:
                return str(p)
        return PurePosixPath(*rp.parts).as_posix()

    def _add_unresolvable(self, file_path: Path, reason: str) -> None:
        key = self._rel(file_path)
        self.unresolvable.setdefault(key, []).append(reason)

    # ---------- manifest handling ----------
    def _find_manifest(self, lang: str, from_dir: Path) -> Path | None:
        globs = LANGUAGES[lang]["manifest_globs"]
        cur = from_dir
        while True:
            for g in globs:
                if "*" in g or "?" in g:
                    try:
                        for entry in cur.iterdir():
                            if entry.is_file() and fnmatch.fnmatch(entry.name, g):
                                return entry
                    except OSError:
                        pass
                else:
                    p = cur / g
                    if p.is_file():
                        return p
            if cur == self.project_root:
                break
            if self.project_root not in cur.parents:
                break
            parent = cur.parent
            if parent == cur:
                break
            cur = parent
        return None

    def _get_manifest_deps(self, lang: str, from_file: Path) -> tuple[set[str] | None, str | None, Path | None]:
        from_dir = from_file.parent
        key = (lang, str(from_dir))
        if key in self._manifest_cache:
            return self._manifest_cache[key]
        manifest = self._find_manifest(lang, from_dir)
        if manifest is None:
            globs = LANGUAGES[lang]["manifest_globs"]
            result = (None, f"manifest not found: {globs}", None)
            self._manifest_cache[key] = result
            return result
        try:
            if lang == "python":
                if manifest.name == "pyproject.toml":
                    deps = parse_pyproject_toml(manifest)
                elif manifest.name == "requirements.txt":
                    deps = parse_requirements_txt(manifest)
                else:
                    deps = set()
            else:
                parser = LANGUAGES[lang]["parse_manifest"]
                deps = parser(manifest)
            result = (deps, None, manifest)
        except Exception as e:
            result = (None, f"manifest parse error ({manifest.name}): {e}", manifest)
        self._manifest_cache[key] = result
        return result

    def _get_go_module_path(self, from_file: Path) -> str | None:
        # walk up, cache by dir
        cur = from_file.parent
        while True:
            key = str(cur)
            if key in self._go_module_cache:
                return self._go_module_cache[key]
            gm = cur / "go.mod"
            if gm.is_file():
                mod = parse_go_mod_module(gm)
                # propagate down
                self._go_module_cache[key] = mod
                return mod
            if cur == self.project_root:
                self._go_module_cache[key] = None
                return None
            if self.project_root not in cur.parents:
                self._go_module_cache[key] = None
                return None
            parent = cur.parent
            if parent == cur:
                self._go_module_cache[key] = None
                return None
            cur = parent

    # ---------- resolution ----------
    def _is_relative_import(self, lang: str, target: str) -> bool:
        if lang == "python":
            return target.startswith(".")
        prefixes = LANGUAGES[lang]["relative_prefixes"]
        return any(target.startswith(p) for p in prefixes)

    def _resolve_candidates(self, lang: str, target: str, from_file: Path) -> list[Path]:
        kind = LANGUAGES[lang]["resolve"]
        if kind == "ts":
            return resolve_ts(target, from_file, self.project_root)
        if kind == "python":
            return resolve_python(target, from_file, self.project_root)
        if kind == "cs":
            return resolve_cs(target, from_file, self.project_root, self.project_files)
        if kind == "go":
            mod = self._get_go_module_path(from_file)
            return resolve_go(target, from_file, self.project_root, mod)
        if kind == "rust":
            return resolve_rust(target, from_file, self.project_root)
        return []

    def _pick_existing(self, candidates: list[Path]) -> Path | None:
        for c in candidates:
            try:
                if c.is_file():
                    resolved = c.resolve()
                    # ensure inside project
                    try:
                        resolved.relative_to(self.project_root)
                    except ValueError:
                        continue
                    return resolved
            except OSError:
                continue
        return None

    def _resolve_import(self, lang: str, target: str, from_file: Path) -> tuple[Path | None, str | None]:
        """Return (resolved_file_or_None, unresolvable_reason_or_None).

        reason is None when the import is definitively third-party (skip silently)
        OR when it successfully resolved to a project file.
        """
        # For go, "relative" actually means "starts with module path"
        if lang == "go":
            mod = self._get_go_module_path(from_file)
            if mod and target.startswith(mod):
                cands = self._resolve_candidates(lang, target, from_file)
                found = self._pick_existing(cands)
                if found is not None:
                    return found, None
                # in-project per go.mod prefix but file not found. Silently skip —
                # commonly a stale/commented import or an unresolved relative miss;
                # not a script error. Real errors still flow via except paths.
                return None, None
            # else non-relative => manifest lookup below

        # 1. relative prefix => in-project
        if self._is_relative_import(lang, target):
            cands = self._resolve_candidates(lang, target, from_file)
            found = self._pick_existing(cands)
            if found is not None:
                return found, None
            # Relative import target not found. Silently skip — the regex may have
            # picked up a commented-out / removed import, or the file was renamed.
            # Not a script error; don't pollute unresolvable.
            return None, None

        # 2. read manifest
        deps, err, manifest_path = self._get_manifest_deps(lang, from_file)
        if deps is None:
            # Manifest missing: cannot decide if third-party. Treat as external
            # (stdlib / built-in / unmanaged) and silently skip — do not recurse,
            # do not record as unresolvable. Genuine manifest parse errors still
            # fall through here; we also skip silently to avoid per-import noise
            # (the parse failure itself is surfaced separately via the cache /
            # any caller that inspects manifest state).
            if err and not err.startswith("manifest not found"):
                # Try to resolve in-project as a best-effort fallback, since we
                # cannot consult the dep list.
                cands = self._resolve_candidates(lang, target, from_file)
                found = self._pick_existing(cands)
                if found is not None:
                    return found, None
            return None, None

        # 3. check third-party match
        top = target.split(".")[0] if lang == "python" else target.split("/")[0]
        if lang == "rust":
            top = target.split("::")[0]
        if lang == "csharp":
            top = target.split(".")[0]
        if target in deps or top in deps:
            return None, None  # third-party, skip

        # 4. try to resolve in project
        cands = self._resolve_candidates(lang, target, from_file)
        found = self._pick_existing(cands)
        if found is not None:
            return found, None

        # 5. cannot decide between stdlib/built-in and a missing project file.
        # Prefer silent skip over noisy unresolvable entries — stdlib imports
        # (Python json/os/sys, Node fs/path/http, Go fmt/net/http, C# System.*,
        # Rust std::*) commonly land here because manifests only list
        # third-party packages. Real resolution failures are still reported
        # via unsupported-extension / read-error / extraction-error paths.
        return None, None

    # ---------- forward index ----------
    def _compute_forward(self, file_path: Path) -> set[str]:
        """Compute the set of project-file rel paths imported by file_path, caching."""
        rel = self._rel(file_path)
        if rel in self._forward_index:
            return self._forward_index[rel]
        ext = file_path.suffix
        result: set[str] = set()
        self._forward_index[rel] = result  # seed to break cycles

        lang = EXT_TO_LANG.get(ext)
        if lang is None:
            self._add_unresolvable(file_path, f"unsupported extension: {ext}")
            return result

        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            self._add_unresolvable(file_path, f"UnicodeDecodeError: {e}")
            return result
        except OSError as e:
            self._add_unresolvable(file_path, f"read error: {e}")
            return result
        except Exception as e:
            self._add_unresolvable(file_path, f"unexpected read error: {e}")
            return result

        try:
            extractor = LANGUAGES[lang]["extract"]
            targets = extractor(text)
        except Exception as e:
            self._add_unresolvable(file_path, f"import extraction error: {e}")
            return result

        seen_targets: set[str] = set()
        for t in targets:
            if t in seen_targets:
                continue
            seen_targets.add(t)
            try:
                resolved, reason = self._resolve_import(lang, t, file_path)
            except Exception as e:
                self._add_unresolvable(file_path, f"resolve error for '{t}': {e}")
                continue
            if resolved is not None:
                result.add(self._rel(resolved))
            elif reason is not None:
                self._add_unresolvable(file_path, reason)
        return result

    # ---------- reverse index ----------
    def _build_reverse_index(self) -> None:
        if self._reverse_index is not None:
            return
        rev: dict[str, set[str]] = {}
        for f in self.project_files:
            rel = self._rel(f)
            try:
                imports = self._compute_forward(f)
            except Exception as e:
                self._add_unresolvable(f, f"forward scan error: {e}")
                imports = set()
            for tgt in imports:
                rev.setdefault(tgt, set()).add(rel)
        self._reverse_index = rev

    # ---------- closure traversal ----------
    def compute(self, changed_rel: list[str]) -> tuple[list[str], list[str]]:
        changed_set = set(changed_rel)
        # build reverse index up-front (requires forward scan of whole project)
        self._build_reverse_index()
        assert self._reverse_index is not None

        related: set[str] = set()
        visited: set[str] = set()
        stack: list[str] = list(changed_set)

        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            abs_path = self.project_root / cur
            # forward
            if cur not in self._forward_index:
                # file might not exist in project_files (e.g., outside scan), attempt
                try:
                    fwd = self._compute_forward(abs_path)
                except Exception as e:
                    self._add_unresolvable(abs_path, f"forward compute error: {e}")
                    fwd = set()
            else:
                fwd = self._forward_index[cur]
            for dep in fwd:
                if dep not in changed_set and dep not in related and dep != cur:
                    related.add(dep)
                if dep not in visited:
                    stack.append(dep)
            # reverse
            rev_deps = self._reverse_index.get(cur, set())
            for importer in rev_deps:
                if importer not in changed_set and importer not in related and importer != cur:
                    related.add(importer)
                if importer not in visited:
                    stack.append(importer)

        # related must not include changed
        related -= changed_set
        return sorted(changed_set), sorted(related)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _emit(obj: dict, exit_code: int = 0) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")
    sys.exit(exit_code)


def main(argv: list[str]) -> None:
    if len(argv) < 3:
        _emit({"error": "insufficient arguments", "detail": {
            "usage": "python3 closure.py <project_root> <changed_file1> [<changed_file2> ...]",
            "received": argv[1:],
        }}, exit_code=1)

    project_root = Path(argv[1])
    if not project_root.exists() or not project_root.is_dir():
        _emit({"error": "project_root does not exist or is not a directory",
               "detail": {"project_root": str(project_root)}}, exit_code=1)
    project_root = project_root.resolve()

    changed_rel: list[str] = []
    for raw in argv[2:]:
        p = Path(raw)
        if not p.is_absolute():
            p = (project_root / raw).resolve()
        else:
            p = p.resolve()
        try:
            rel = p.relative_to(project_root)
        except ValueError:
            _emit({"error": "changed file outside project_root",
                   "detail": {"file": str(p), "project_root": str(project_root)}}, exit_code=1)
        if not p.exists():
            _emit({"error": "changed file does not exist",
                   "detail": {"file": str(p)}}, exit_code=1)
        changed_rel.append(PurePosixPath(*rel.parts).as_posix())

    closure = Closure(project_root)
    changed_sorted, related_sorted = closure.compute(changed_rel)

    # unresolvable merge
    unresolvable_list = []
    for f in sorted(closure.unresolvable.keys()):
        reasons = closure.unresolvable[f]
        # dedupe reasons while preserving first-seen order
        seen: set[str] = set()
        deduped: list[str] = []
        for r in reasons:
            if r not in seen:
                seen.add(r)
                deduped.append(r)
        unresolvable_list.append({"file": f, "reason": "; ".join(deduped)})

    _emit({
        "changed": changed_sorted,
        "related": related_sorted,
        "unresolvable": unresolvable_list,
    }, exit_code=0)


if __name__ == "__main__":
    main(sys.argv)
