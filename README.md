# Yet Another Monorepo Plugin
YAMP is an *opinionated* Poetry (>= 2.0.0) plugin that helps managing a "pinned" monorepo with centralized versioning. 

The default behavior is that the Single Source of Version Truth is the root `pyproject.toml`.

> [!WARNING]
> 🚧 **WIP**, not ready yet!
> 
> Some core features as path-dependency rewrite are missing.


> [!IMPORTANT]
> YAMP is tailored to a very specific need, so it may not be a good fit for a more general "monorepo" approach.
> 
> It may be suitable if:
> - You're maintaining multiple related but decoupled Python packages (e.g., internal libs) in one repo.
> 
> - You want tight version control and easy building without complex/custom tooling.
> 
> - You want *path dependency* rewriting to pin inter-project dependencies. 
>

## TODO
 - proper test matrix (Poetry)
 - WIP: path dependency rewrite
 - projects-install/init command
 - ...

## Project structure
```
.
├───pyproject.toml  <== root pyproject.toml
┆
└───<projects-dir>  <== projects directory
     |
     ├───proj-1
     │   ├───pyproject.toml
     │   └─── ...
     ├───proj-2
     │   ├───pyproject.toml
     ┆   └─── ...
     └───proj-3
         ├───pyproject.toml
         └─── ...
```

## Configuration (`pyproject.toml`)
```toml
[tool.poetry-yet-another-monorepo-plugin]
projects-dir = "src"
exclude-projects = [
    "proj-c",
]
```
| Setting            |   Description   |  Default   |
|--------------------|-----------------|------------|
| `projects-dir`     | The directory where projects are located.             | `"projects"`         |
| `exclude-projects` | A list of *regex* patterns to match against project names for exclusion. | `[]`         |

## Commands

> [!IMPORTANT]
> - All commands support the `-v|vv|vvv` verbosity options.
> - All commands that apply changes support a `--dry-run` flag to preview the changes without committing them.

---

#### `poetry list-projects`

Lists all projects in the monorepo `projects-dir`.

---

#### `poetry build-projects-pinned [--version-override] [--sync-versions]`

This is the equivalent of calling `poetry build --project <proj-dir>` for every project in `projects-dir`, with the difference that **the build version is pinned to the version**
in **the root `pyproject.toml`**. The version in each project's individual `pyproject.toml` is therefore *ignored*. 

If `--sync-versions` is specified, the version of every project is synced with the build version.

> The command also supports the same options as `poetry build`.

> [!NOTE]
> If a PEP-621 `[project]` table is found, the version will be read from `project.version`; otherwise, it will fall back to `tool.poetry.version` for retro-compatibility.

> [!TIP]
> The build version can be overridden by setting one of the following:
>  1. `--version-override` option (takes precedence)
>  2. `YAMP_VERSION_OVERRIDE` environment variable

---

#### `poetry set-projects-version [--version-override]`

Syncs the *version* of all projects in the monorepo to the version in **the root `pyproject.toml`**, from either `project.version` or `tool.poetry.version` (checked in this order).

> [!TIP]
> The version can be overridden by setting one of the following:
>  1. `--version-override` option (takes precedence)
>  2. `YAMP_VERSION_OVERRIDE` environment variable

> [!CAUTION]
> The version is **written** to the `pyproject.toml` of every (non-excluded) project in the `projects-dir`. 
> 
> If a PEP-621 `[project]` table is found, the version will be written to `project.version`; otherwise, to `tool.poetry.version` for retro-compatibility.
>
---
