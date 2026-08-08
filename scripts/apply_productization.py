from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "src" / "ares" / "cli.py"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "productize-apply.yml"
SELF_PATH = Path(__file__).resolve()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    text = CLI_PATH.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "import json\nimport secrets\nfrom pathlib import Path\n",
        "import json\nimport platform\nimport secrets\nimport sys\nfrom pathlib import Path\n",
        "diagnostic imports",
    )
    text = replace_once(
        text,
        'app = typer.Typer(help=f"{APP_NAME} autonomous testing suite", invoke_without_command=True)',
        'app = typer.Typer(help=f"{APP_NAME} operator-supervised security assessment runtime", invoke_without_command=True)',
        "product help text",
    )
    text = replace_once(
        text,
        'mission_app = typer.Typer(help="Swarm testing missions")',
        'mission_app = typer.Typer(help="Policy-bound assessment missions")',
        "mission help text",
    )

    old_doctor = '''@app.command("doctor")
def doctor() -> None:
    """Show runtime configuration and tool registry status."""
    snapshot = build_doctor_snapshot(registry=build_registry())
    for key, value in snapshot.items():
        typer.echo(f"{key}: {value}")
'''
    new_doctor = '''def _product_doctor_snapshot() -> dict[str, Any]:
    return {
        "ares_version": __version__,
        "distribution": "bluedot-ares",
        **build_doctor_snapshot(registry=build_registry()),
    }


@app.command("doctor")
def doctor(
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Emit machine-readable JSON diagnostics.",
    ),
) -> None:
    """Show runtime configuration and tool registry status."""
    snapshot = _product_doctor_snapshot()
    if as_json:
        typer.echo(json.dumps(snapshot, indent=2, sort_keys=True))
        return
    for key, value in snapshot.items():
        typer.echo(f"{key}: {value}")


@app.command("support-bundle")
def support_bundle(
    out: str = typer.Option(
        "ares-support-bundle.json",
        "--out",
        "-o",
        help="Path for the redacted JSON support bundle.",
    ),
) -> None:
    """Write redacted runtime diagnostics without credentials or engagement data."""
    output_path = Path(out).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "redaction": "Credentials and engagement records are excluded.",
        "runtime": {
            "ares_version": __version__,
            "distribution": "bluedot-ares",
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "doctor": _product_doctor_snapshot(),
    }
    write_private_text(
        output_path,
        json.dumps(payload, indent=2, sort_keys=True) + "\\n",
        private_parent=False,
    )
    typer.echo(f"Support bundle written to: {output_path.resolve()}")
'''
    text = replace_once(text, old_doctor, new_doctor, "doctor commands")

    old_nested_option = '''    approve_high_risk: bool = typer.Option(False, "--approve-high-risk", help="Approve exploit/post-exploitation tasks in the supplied graph"),
    autonomous: bool = typer.Option(False, "--autonomous", help="Use governed model planning with the autonomous-recon profile"),
'''
    new_nested_option = '''    approve_high_risk: bool = typer.Option(False, "--approve-high-risk", help="Approve exploit/post-exploitation tasks in the supplied graph"),
    approval_receipts_file: str | None = typer.Option(
        None,
        "--approval-receipts",
        help="Mode-0600 JSON approval receipts bound to advanced tasks",
    ),
    autonomous: bool = typer.Option(False, "--autonomous", help="Use governed model planning with the autonomous-recon profile"),
'''
    text = replace_once(
        text,
        old_nested_option,
        new_nested_option,
        "nested approval receipt option",
    )

    old_forward = '''        approve_high_risk=approve_high_risk,
        autonomous=autonomous,
'''
    new_forward = '''        approve_high_risk=approve_high_risk,
        approval_receipts_file=approval_receipts_file,
        autonomous=autonomous,
'''
    text = replace_once(
        text,
        old_forward,
        new_forward,
        "nested approval receipt forwarding",
    )

    if text.count("--approval-receipts") != 2:
        raise RuntimeError("expected direct and nested approval receipt options")
    if "@app.command(\"support-bundle\")" not in text:
        raise RuntimeError("support-bundle command was not inserted")

    ast.parse(text, filename=str(CLI_PATH))
    CLI_PATH.write_text(text, encoding="utf-8")

    WORKFLOW_PATH.unlink(missing_ok=True)
    SELF_PATH.unlink(missing_ok=True)
    scripts_dir = ROOT / "scripts"
    try:
        scripts_dir.rmdir()
    except OSError:
        pass

    print("Applied Ares 1.1 CLI productization patch.")


if __name__ == "__main__":
    main()
