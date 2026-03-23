import json
from pathlib import Path


def compact(src_path: Path, dst_path: Path) -> None:
    data = json.loads(src_path.read_text(encoding="utf-8"))
    extra = data.get("extra") if isinstance(data.get("extra"), dict) else {}
    keep_top = {
        "id": data.get("id"),
        "revision": data.get("revision", 0),
        "version": data.get("version", 0.4),
        "last_node_id": data.get("last_node_id"),
        "last_link_id": data.get("last_link_id"),
        "nodes": data.get("nodes", []),
        "links": data.get("links", []),
        "groups": data.get("groups", []),
        "config": data.get("config", {}),
        "extra": {"ds": extra.get("ds")} if isinstance(extra.get("ds"), dict) else {},
    }

    nodes = []
    for n in keep_top.get("nodes", []):
        node = {k: n.get(k) for k in ["id", "type", "pos", "size", "flags", "inputs", "outputs", "widgets_values", "title"] if k in n}
        if "pos" not in node or node["pos"] is None:
            node["pos"] = [0, 0]
        if "size" not in node or node["size"] is None:
            node["size"] = [210, 60]
        if "flags" not in node or node["flags"] is None:
            node["flags"] = {}
        if "inputs" not in node or node["inputs"] is None:
            node["inputs"] = []
        if "outputs" not in node or node["outputs"] is None:
            node["outputs"] = []
        if "widgets_values" not in node or node["widgets_values"] is None:
            node["widgets_values"] = []
        props = n.get("properties")
        if not isinstance(props, dict):
            props = {}
        filtered_props = {k: v for k, v in props.items() if k not in {"_cache", "ue_properties", "PS_cache"}}
        node["properties"] = filtered_props
        nodes.append(node)
    keep_top["nodes"] = nodes
    dst_path.write_text(json.dumps(keep_top, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    compact(root / "depersonity.json", root / "depersonity_compact.json")
    compact(root / "lite_version" / "depersonity_lite.json", root / "lite_version" / "depersonity_lite_compact.json")


if __name__ == "__main__":
    main()
