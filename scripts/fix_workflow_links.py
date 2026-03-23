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

    kept_links = []
    removed = 0

    for l in _as_list(data.get("links")):
        if not (isinstance(l, list) and len(l) >= 6):
            removed += 1
            continue
        link_id, origin_id, origin_slot, target_id, target_slot, link_type = l[:6]
        if not all(isinstance(x, int) for x in [link_id, origin_id, origin_slot, target_id, target_slot]):
            removed += 1
            continue

        origin = node_by_id.get(origin_id)
        target = node_by_id.get(target_id)
        if origin is None or target is None:
            removed += 1
            continue

        origin_outputs = origin.get("outputs", [])
        target_inputs = target.get("inputs", [])
        if not (0 <= origin_slot < len(origin_outputs)):
            removed += 1
            continue
        if not (0 <= target_slot < len(target_inputs)):
            removed += 1
            continue

        out = origin_outputs[origin_slot]
        inp = target_inputs[target_slot]
        if not isinstance(out, dict) or not isinstance(inp, dict):
            removed += 1
            continue

        out_links = out.get("links")
        if not isinstance(out_links, list):
            out_links = []
            out["links"] = out_links
        if link_id not in out_links:
            out_links.append(link_id)

        inp["link"] = link_id

        kept_links.append([link_id, origin_id, origin_slot, target_id, target_slot, link_type])

    kept_ids = {l[0] for l in kept_links}

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
