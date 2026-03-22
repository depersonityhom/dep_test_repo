import json
from pathlib import Path


def compact(src_path: Path, dst_path: Path) -> None:
    data = json.loads(src_path.read_text(encoding="utf-8"))
    keep_top = {k: data.get(k) for k in ["id", "revision", "last_node_id", "last_link_id", "nodes", "links"] if k in data}
    nodes = []
    for n in keep_top.get("nodes", []):
        nodes.append({k: n.get(k) for k in ["id", "type", "pos", "size", "flags", "inputs", "outputs", "widgets_values"] if k in n})
    keep_top["nodes"] = nodes
    dst_path.write_text(json.dumps(keep_top, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    compact(root / "depersonity.json", root / "depersonity_compact.json")
    compact(root / "lite_version" / "depersonity_lite.json", root / "lite_version" / "depersonity_lite_compact.json")


if __name__ == "__main__":
    main()

