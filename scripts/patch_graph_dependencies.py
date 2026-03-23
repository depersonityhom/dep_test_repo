import json
from pathlib import Path


def add_output_link(node: dict, out_slot: int, link_id: int) -> None:
    outputs = node.get("outputs")
    if not isinstance(outputs, list) or out_slot >= len(outputs):
        raise ValueError(f"node {node.get('id')} has no output slot {out_slot}")
    out = outputs[out_slot]
    if not isinstance(out, dict):
        raise ValueError(f"node {node.get('id')} output slot {out_slot} is not a dict")
    links = out.get("links")
    if not isinstance(links, list):
        links = []
        out["links"] = links
    if link_id not in links:
        links.append(link_id)


def main() -> None:
    path = Path(__file__).resolve().parents[1] / "depersonity.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    nodes = [n for n in data.get("nodes", []) if isinstance(n, dict) and isinstance(n.get("id"), int)]
    by = {n["id"]: n for n in nodes}

    last_link = int(data.get("last_link_id") or 0)

    def new_link_id() -> int:
        nonlocal last_link
        last_link += 1
        return last_link

    # 1) Make sampler depend on real producers (avoid GetNode global store dependency)
    sampler = by[273]

    # Model: WanVideoSetLoRAs (78 out0) -> WanVideoSampler (273 in0)
    link_model = new_link_id()
    add_output_link(by[78], 0, link_model)
    sampler["inputs"][0]["link"] = link_model

    # Image embeds: WanVideoAnimateEmbeds (624 out0) -> WanVideoSampler (273 in1)
    link_embeds = new_link_id()
    add_output_link(by[624], 0, link_embeds)
    sampler["inputs"][1]["link"] = link_embeds

    # 2) Make final video outputs depend on TSColorMatch output (avoid GetNode global store dependency)
    # TSColorMatch out0 -> VHS_VideoCombine images
    link_out_mp4 = new_link_id()
    link_out_preview = new_link_id()
    add_output_link(by[638], 0, link_out_mp4)
    add_output_link(by[638], 0, link_out_preview)

    for nid, img_link in [(652, link_out_mp4), (651, link_out_preview)]:
        n = by[nid]
        if isinstance(n.get("inputs"), list) and n["inputs"]:
            n["inputs"][0]["link"] = img_link

    # Audio: VHS_LoadVideo audio output -> VHS_VideoCombine audio input
    load_video = by[583]
    audio_slot = None
    for idx, out in enumerate(load_video.get("outputs", []) or []):
        if isinstance(out, dict) and out.get("type") == "AUDIO":
            audio_slot = idx
            break
    if audio_slot is None:
        raise RuntimeError("VHS_LoadVideo audio output not found")

    link_audio_mp4 = new_link_id()
    link_audio_preview = new_link_id()
    add_output_link(load_video, audio_slot, link_audio_mp4)
    add_output_link(load_video, audio_slot, link_audio_preview)

    for nid, aud_link in [(652, link_audio_mp4), (651, link_audio_preview)]:
        n = by[nid]
        if isinstance(n.get("inputs"), list) and len(n["inputs"]) > 1:
            n["inputs"][1]["link"] = aud_link

    data["last_link_id"] = last_link
    path.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
    print(f"Patched depersonity.json: last_link_id={last_link}")


if __name__ == "__main__":
    main()

