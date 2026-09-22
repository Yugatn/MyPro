"""MyPro Evidence Core CLI."""
from __future__ import annotations
import json
from pathlib import Path
import typer
from core.project import Project
from core.import_layer.otio_adapter import OTIOAdapter

app=typer.Typer(help="MyPro Evidence Core CLI",no_args_is_help=True)


@app.command("init")
def init(project_dir: Path):
    p=Project.create(project_dir)
    typer.echo(f"project: {p.read_manifest().project_id}")


@app.command("probe-cmd")
def probe_cmd(path: Path):
    """Placeholder until FFprobe integration is installed."""
    if not path.exists():
        raise typer.BadParameter(f"file does not exist: {path}")
        typer.echo(json.dumps({"path":str(path),"size":path.stat().st_size},ensure_ascii=False,indent=2))


@app.command("import-project")
def import_project(path: Path, project_dir: Path, dry_run: bool=True):
    """Import external project as evidence; never mutates montage state."""
    p=Project(project_dir)
    if not path.exists():
        raise typer.BadParameter(f"file does not exist: {path}")
    adapter=OTIOAdapter()
    if path.suffix.lower() not in adapter.supported_extensions:
        typer.echo(f"unsupported: {path.suffix}",err=True)
        raise typer.Exit(2)
    result=adapter.import_project(path)
    payload=result.as_dict()
    payload["proposal"]={"action":"import_project","merge_strategy":"replace","reversible":True}
    if not dry_run:
        p.log.append(type="proposal.import_project",actor=f"adapter:{adapter.adapter_id}@{adapter.adapter_version}",payload=payload)
    typer.echo(json.dumps(result.manifest.as_dict(),ensure_ascii=False,indent=2))
    typer.echo("proposal recorded" if not dry_run else "dry-run: no project mutation")


@app.command("backup")
def backup(project_dir: Path, label: str="manual"):
    digest=Project(project_dir).backup(label=label)
    typer.echo(f"backup: {digest}")


@app.command("verify")
def verify(project_dir: Path):
    p=Project(project_dir)
    events=list(p.log.iter_events())
    ok=True
    for ref in p.backups_dir.glob("*.ref"):
        from core.identity import ContentHash
        ok=p.verify_backup(ContentHash.parse(ref.read_text().strip())) and ok
    typer.echo(f"events: {len(events)}, tip: {p.log.tip_hash}")
    typer.echo("OK" if ok else "FAILED")
    raise typer.Exit(0 if ok else 1)


@app.command("restore")
def restore(project_dir: Path,digest: str,target: Path):
    from core.identity import ContentHash
    restored=Project(project_dir).restore_backup(ContentHash.parse(digest),target=target)
    typer.echo(f"restored to {restored.root}")


def main():
    app()


if __name__=="__main__":
    main()
