import importlib.util
import re
import sys
from pathlib import Path


def _safe_module_name(name: str) -> str:
    return re.sub(r"[^0-9A-Za-z_]", "_", name)


def _load_package_from_dir(pkg_dir: Path):
    init_path = pkg_dir / "__init__.py"
    if not init_path.exists():
        return {}, {}

    module_name = f"depersonity_bundle_{_safe_module_name(pkg_dir.name)}"
    spec = importlib.util.spec_from_file_location(
        module_name,
        init_path,
        submodule_search_locations=[str(pkg_dir)],
    )
    if spec is None or spec.loader is None:
        return {}, {}

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    class_map = getattr(module, "NODE_CLASS_MAPPINGS", None) or {}
    display_map = getattr(module, "NODE_DISPLAY_NAME_MAPPINGS", None) or {}
    if not isinstance(class_map, dict):
        class_map = {}
    if not isinstance(display_map, dict):
        display_map = {}
    return class_map, display_map


_ROOT = Path(__file__).resolve().parent
_PACKAGES = [
    "depersonity-lora-scheduler",
    "depersonity-kjnodes",
    "depersonity-sam2-segmentation",
    "depersonity-zmg-nodes",
    "depersonity-wanvideo-wrapper",
    "depersonity-wananimate-preprocess",
    "depersonity-videohelpersuite",
    "depersonity-ts-utils",
    "depersonity-liveportrait",
    "depersonity-impact-pack",
    "depersonity-facerestore-cf",
    "ComfyUI-Manager",
]

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

for _pkg in _PACKAGES:
    _dir = _ROOT / _pkg
    if not _dir.exists():
        continue
    try:
        _cm, _dm = _load_package_from_dir(_dir)
    except Exception:
        continue
    NODE_CLASS_MAPPINGS.update(_cm)
    NODE_DISPLAY_NAME_MAPPINGS.update(_dm)

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

