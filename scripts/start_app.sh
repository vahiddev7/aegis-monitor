#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

python - "${PROJECT_ROOT}" "$@" <<'PY'
import ast
import json
import keyword
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path


def fail(message):
    raise SystemExit(f"Error: {message}")


def find_list_assignment(source, variable_name):
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = [
                target.id
                for target in node.targets
                if isinstance(target, ast.Name)
            ]
            if variable_name in names and isinstance(node.value, ast.List):
                return node.value
    fail(f"Could not find a list assignment for {variable_name}.")


def insert_list_entry(source, variable_name, entry):
    list_node = find_list_assignment(source, variable_name)
    if any(
        isinstance(item, ast.Constant) and item.value == entry
        for item in list_node.elts
    ):
        return source

    lines = source.splitlines(keepends=True)
    line_index = list_node.lineno - 1
    line = lines[line_index]
    bracket_index = line.find("[", list_node.col_offset)
    if bracket_index < 0:
        fail(f"Could not locate the opening bracket for {variable_name}.")

    absolute_offset = sum(len(item) for item in lines[:line_index]) + bracket_index
    updated = source[: absolute_offset + 1] + f"\n    {entry}," + source[absolute_offset + 1 :]
    ast.parse(updated)
    return updated


def ensure_url_import(source):
    tree = ast.parse(source)
    imports = [
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "django.urls"
    ]
    if imports:
        node = imports[0]
        names = {item.name for item in node.names}
        if any(
            item.name in {"include", "path"}
            and item.asname is not None
            for item in node.names
        ):
            fail("The django.urls include/path imports must not be aliased.")
        missing = [name for name in ("include", "path") if name not in names]
        if not missing:
            return source
        if node.lineno != node.end_lineno:
            fail("The django.urls import spans multiple lines; update it manually.")
        lines = source.splitlines(keepends=True)
        line = lines[node.lineno - 1]
        marker = "import"
        position = line.find(marker)
        if position < 0:
            fail("Could not safely update the django.urls import.")
        line = line[: position + len(marker)] + " " + ", ".join(missing) + "," + line[position + len(marker) :]
        lines[node.lineno - 1] = line
        updated = "".join(lines)
        ast.parse(updated)
        return updated

    insertion_line = 0
    body = tree.body
    index = 0
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        insertion_line = body[0].end_lineno
        index = 1
    while index < len(body):
        node = body[index]
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            insertion_line = node.end_lineno
            index += 1
        else:
            break
    lines = source.splitlines(keepends=True)
    lines.insert(insertion_line, "from django.urls import include, path\n")
    updated = "".join(lines)
    ast.parse(updated)
    return updated


def ensure_route_is_free(source, route):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        is_path_call = (
            isinstance(function, ast.Name) and function.id == "path"
        ) or (
            isinstance(function, ast.Attribute) and function.attr == "path"
        )
        if is_path_call and node.args:
            first = node.args[0]
            if isinstance(first, ast.Constant) and first.value == route:
                fail(f"URL route {route!r} is already registered.")


def atomic_write(path, content):
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
        os.chmod(temporary_name, stat.S_IMODE(path.stat().st_mode))
        os.replace(temporary_name, path)
    except Exception:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
        raise


def main():
    if len(sys.argv) not in (3, 4):
        fail("Usage: ./scripts/start_app.sh <app_name> [verbose_name]")

    project_root = Path(sys.argv[1]).resolve()
    app_name = sys.argv[2]
    verbose_name = sys.argv[3] if len(sys.argv) == 4 else ""

    if not re.fullmatch(r"[a-z][a-z0-9_]*", app_name) or keyword.iskeyword(app_name):
        fail("app name must be a non-keyword Python identifier using lowercase letters, numbers, and underscores.")

    apps_dir = project_root / "apps"
    app_dir = apps_dir / app_name
    if not apps_dir.is_dir():
        fail(f"Apps directory does not exist: {apps_dir}")
    if app_dir.exists() or any(
        child.name.lower() == app_name.lower() for child in apps_dir.iterdir()
    ):
        fail(f"App {app_name!r} already exists or conflicts by case.")

    if not verbose_name:
        verbose_name = " ".join(part.capitalize() for part in app_name.split("_"))

    settings_path = project_root / "config" / "settings" / "base.py"
    urls_path = project_root / "config" / "urls.py"
    if not settings_path.is_file() or not urls_path.is_file():
        fail("Expected config/settings/base.py and config/urls.py to exist.")

    original_settings = settings_path.read_text(encoding="utf-8")
    original_urls = urls_path.read_text(encoding="utf-8")

    app_config = f"apps.{app_name}"
    settings_source = insert_list_entry(
        original_settings, "INSTALLED_APPS", json.dumps(app_config)
    )

    route = f"api/{app_name}/"
    ensure_route_is_free(original_urls, route)
    urls_source = ensure_url_import(original_urls)
    urls_source = insert_list_entry(
        urls_source,
        "urlpatterns",
        f'path("{route}", include("{app_config}.urls"))',
    )

    app_class = "".join(part.capitalize() for part in app_name.split("_")) + "Config"
    temporary_app = Path(
        tempfile.mkdtemp(prefix=f".{app_name}.", dir=apps_dir)
    )
    created_app = False
    settings_written = False
    urls_written = False

    try:
        (temporary_app / "models").mkdir()
        (temporary_app / "migrations").mkdir()
        tests_dir = temporary_app / "tests"
        tests_dir.mkdir()

        for package in ("", "models", "migrations", "tests"):
            (temporary_app / package / "__init__.py").touch()

        for test_type in ("unit", "integration", "e2e"):
            test_dir = tests_dir / test_type
            test_dir.mkdir()
            (test_dir / "__init__.py").touch()

        (temporary_app / "apps.py").write_text(
            "from django.apps import AppConfig\n\n\n"
            f"class {app_class}(AppConfig):\n"
            '    default_auto_field = "django.db.models.BigAutoField"\n'
            f'    name = "apps.{app_name}"\n'
            f"    verbose_name = {json.dumps(verbose_name)}\n",
            encoding="utf-8",
        )
        (temporary_app / "admin.py").write_text("", encoding="utf-8")
        (temporary_app / "urls.py").write_text(
            "urlpatterns = []\n", encoding="utf-8"
        )

        os.replace(temporary_app, app_dir)
        created_app = True
        atomic_write(settings_path, settings_source)
        settings_written = True
        atomic_write(urls_path, urls_source)
        urls_written = True
    except Exception:
        if settings_written:
            atomic_write(settings_path, original_settings)
        if urls_written:
            atomic_write(urls_path, original_urls)
        if created_app and app_dir.exists():
            shutil.rmtree(app_dir)
        if temporary_app.exists():
            shutil.rmtree(temporary_app)
        raise

    print(f"Created app {app_name!r} at {app_dir}")
    print(f"Registered {app_config} and /{route} in project settings.")
    print("Add services, selectors, serializers, permissions, and views only when needed.")
    print("Define models and run migrations before using database-backed features.")


if __name__ == "__main__":
    main()
PY
