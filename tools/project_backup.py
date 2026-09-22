"""CLI backup and recovery utility."""

from __future__ import annotations

import argparse
from pathlib import Path

from core.backup import BackupStore
from core.identity import ContentHash
from core.project import Project


def main() -> int:
    parser = argparse.ArgumentParser(prog="mypro-backup")
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("project")
    create.add_argument("--label", default="manual")
    verify = sub.add_parser("verify")
    verify.add_argument("project")
    verify.add_argument("digest")
    restore = sub.add_parser("restore")
    restore.add_argument("project")
    restore.add_argument("digest")
    restore.add_argument("destination")
    args = parser.parse_args()

    project = Project(args.project)
    store = BackupStore(project.root)
    if args.command == "create":
        print(store.create(event_log=project.log, snapshots=project.snapshots, label=args.label))
        return 0

    digest = ContentHash.parse(args.digest)
    if args.command == "verify":
        ok = store.verify(event_log=project.log, snapshots=project.snapshots, digest=digest)
        print("OK" if ok else "FAILED")
        return 0 if ok else 1

    store.restore(target=args.destination, digest=digest, source_root=project.root)
    print(f"restored: {Path(args.destination)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
