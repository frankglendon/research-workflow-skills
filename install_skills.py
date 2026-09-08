"""Link this checkout's five skills into a host's skill directory."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=Path.home() / ".codex/skills")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    sources = sorted((root / "skills").iterdir())
    for source in sources:
        destination = args.target / source.name
        if destination.exists() or destination.is_symlink():
            if destination.resolve() != source.resolve():
                raise SystemExit(f"Existing skill would be replaced: {source.name}")
    args.target.mkdir(parents=True, exist_ok=True)
    for source in sources:
        destination = args.target / source.name
        if not destination.is_symlink():
            destination.symlink_to(source.resolve(), target_is_directory=True)
        print(source.name)


if __name__ == "__main__":
    main()
