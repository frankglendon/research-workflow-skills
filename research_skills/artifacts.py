"""Output transactions and Microsoft Office validation."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid
import zipfile
from lxml import etree
from .contracts import GateError, fingerprint


def validate_office(path):
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.endswith(".xml"):
                continue
            root = etree.fromstring(archive.read(name))
            for parent in root.iter():
                if etree.QName(parent).localname not in {"spPr", "grpSpPr", "rPr", "defRPr", "endParaRPr", "tcPr", "txBody"}:
                    continue
                names = [etree.QName(c).localname for c in parent if isinstance(c.tag, str)]
                for singleton in {"effectLst", "effectDag", "solidFill", "gradFill", "bodyPr"}:
                    if names.count(singleton) > 1:
                        raise GateError("Duplicate OOXML singleton element")
    dotnet = shutil.which("dotnet") or "/usr/local/share/dotnet/dotnet"
    if not Path(dotnet).is_file():
        raise GateError("Microsoft .NET 10 SDK is required for Office validation")
    source = Path(__file__).parent / "validation"
    cache = Path(os.environ.get("RESEARCH_VALIDATOR_CACHE", Path.home() / ".cache/research-workflow-skills/validator"))
    dll = cache / "bin/OpenXmlValidate.dll"
    version = fingerprint((source / "Program.cs").read_bytes() + (source / "OpenXmlValidate.csproj").read_bytes())
    if not dll.exists() or not (cache / "version").exists() or (cache / "version").read_text() != version:
        cache.mkdir(parents=True, exist_ok=True)
        for filename in ("Program.cs", "OpenXmlValidate.csproj"):
            shutil.copy2(source / filename, cache / filename)
        result = subprocess.run([dotnet, "build", str(cache / "OpenXmlValidate.csproj"),
            "-o", str(cache / "bin"), "--nologo", "-v", "q", "--ignore-failed-sources"],
            capture_output=True, text=True, timeout=180)
        if result.returncode:
            raise GateError("Open XML SDK validator build failed")
        (cache / "version").write_text(version)
    result = subprocess.run([dotnet, str(dll), str(Path(path).resolve())],
                            capture_output=True, text=True, timeout=60)
    try:
        count = json.loads(result.stdout)["errors"]
    except (ValueError, KeyError):
        raise GateError("Open XML SDK validator returned no result") from None
    if result.returncode or count:
        raise GateError(f"Open XML SDK validation failed: {count} errors")
    return {"openxml_errors": 0}


def export_artifact(output, builder, *, tool, inputs, config, counts=None):
    output = Path(output).resolve()
    sidecar = output.with_suffix(output.suffix + ".manifest.json")
    if output.exists() or sidecar.exists():
        raise GateError("Output already exists; choose a new path")
    if output in [Path(p).resolve() for p in inputs]:
        raise GateError("Source files cannot be overwritten")
    input_hashes = [fingerprint(Path(p).read_bytes()) for p in inputs]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=".research-") as directory:
        pending = Path(directory) / output.name
        run_id = str(uuid.uuid4())
        builder(pending, run_id)
        if pending.suffix.lower() == ".xlsx":
            from .ooxml import normalize_xlsx
            normalize_xlsx(pending)
        elif pending.suffix.lower() == ".pptx":
            from .ooxml import normalize_pptx
            normalize_pptx(pending)
        office = validate_office(pending)
        if input_hashes != [fingerprint(Path(p).read_bytes()) for p in inputs]:
            raise GateError("Source changed during export; repeat review with the current input")
        manifest = {"schema_version": 1, "engine_version": "0.1.0", "tool": tool,
            "run_id": run_id, "input_sha256": input_hashes,
            "config_sha256": fingerprint(config), "output_sha256": fingerprint(pending.read_bytes()),
            "gates": {"required_review": "passed", "office": "passed"},
            "counts": counts or {}, **office}
        receipt = Path(directory) / sidecar.name
        receipt.write_text(json.dumps(manifest, indent=2) + "\n")
        os.link(pending, output)
        try:
            os.link(receipt, sidecar)
        except Exception:
            output.unlink()
            raise
    return manifest
