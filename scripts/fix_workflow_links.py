import json
from pathlib import Path


def _as_list(value):
    return value if isinstance(value, list) else []


def fix_workflow(path: Path) -> tuple[int, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes = [n for n in _as_list(data.get("nodes")) if isinstance(n, dict) and isinstance(n.get("id"), int)]
    node_by_id = {n["id"]: n for n in nodes}

    for n in nodes:
        if not isinstance(n.get("inputs"), list):
            n["inputs"] = []
        if not isinstance(n.get("outputs"), list):
            n["outputs"] = []

    # Rebuild links from node->outputs (origin) + node->inputs (targets).
    # This fixes two classes of issues:
    # 1) links pointing to non-existent slots (we drop them)
    # 2) missing link records in data["links"] even though inputs/outputs reference them (we reconstruct them)
    origin_by_link = {}
    for nid, n in node_by_id.items():
        for o_slot, out in enumerate(n.get("outputs", [])):
            if not isinstance(out, dict):
                continue
            for link_id in _as_list(out.get("links")):
                if isinstance(link_id, int) and link_id not in origin_by_link:
                    origin_by_link[link_id] = (nid, o_slot, out.get("type"))

    kept_links = []
    removed = 0
    kept_ids = set()

    for t_id, t in node_by_id.items():
        for t_slot, inp in enumerate(t.get("inputs", [])):
            if not isinstance(inp, dict):
                continue
            link_id = inp.get("link")
            if not isinstance(link_id, int):
                continue
            origin_info = origin_by_link.get(link_id)
            if origin_info is None:
                inp["link"] = None
                removed += 1
                continue
            o_id, o_slot, out_type = origin_info
            origin = node_by_id.get(o_id)
            if origin is None:
                inp["link"] = None
                removed += 1
                continue

            origin_outputs = origin.get("outputs", [])
            if not (0 <= o_slot < len(origin_outputs)):
                inp["link"] = None
                removed += 1
                continue
            target_inputs = t.get("inputs", [])
            if not (0 <= t_slot < len(target_inputs)):
                inp["link"] = None
                removed += 1
                continue

            out = origin_outputs[o_slot]
            if not isinstance(out, dict):
                inp["link"] = None
                removed += 1
                continue

            # Ensure origin output contains this link id
            out_links = out.get("links")
            if not isinstance(out_links, list):
                out_links = []
                out["links"] = out_links
            if link_id not in out_links:
                out_links.append(link_id)

            # Keep link type consistent with the target input type if possible
            link_type = inp.get("type") or out_type or "UNKNOWN"
            kept_links.append([link_id, o_id, o_slot, t_id, t_slot, link_type])
            kept_ids.add(link_id)

    for n in nodes:
        for inp in n.get("inputs", []):
            if not isinstance(inp, dict):
                continue
            link = inp.get("link")
            if isinstance(link, int) and link not in kept_ids:
                inp["link"] = None

        for out in n.get("outputs", []):
            if not isinstance(out, dict):
                continue
            links = out.get("links")
            if not isinstance(links, list):
                continue
            out["links"] = [lid for lid in links if isinstance(lid, int) and lid in kept_ids]

    data["nodes"] = nodes
    data["links"] = kept_links
    data["last_link_id"] = max([data.get("last_link_id", 0)] + [l[0] for l in kept_links]) if kept_links else data.get("last_link_id", 0)
    data["last_node_id"] = max([data.get("last_node_id", 0)] + [n["id"] for n in nodes]) if nodes else data.get("last_node_id", 0)

    path.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
    return removed, len(kept_links)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    targets = [
        root / "depersonity.json",
        root / "lite_version" / "depersonity_lite.json",
    ]
    for p in targets:
        if not p.exists():
            continue
        removed, kept = fix_workflow(p)
        print(f"{p.name}: kept={kept} removed={removed}")


if __name__ == "__main__":
    main()
