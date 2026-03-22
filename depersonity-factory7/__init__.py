from .videohelpersuite.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
import folder_paths
from .videohelpersuite.server import server
from .videohelpersuite import documentation
from .videohelpersuite import latent_preview

DEPERSONITY_PREFIX = "Depersonity_"
DEPERSONITY_CATEGORY = "Depersonity"


def _apply_depersonity_mappings(node_class_mappings, node_display_name_mappings):
    updated_class_mappings = {}
    updated_display_name_mappings = {}

    for key, cls in node_class_mappings.items():
        updated_key = key if key.startswith(DEPERSONITY_PREFIX) else f"{DEPERSONITY_PREFIX}{key}"
        updated_class_mappings[updated_key] = cls
        try:
            cls.CATEGORY = DEPERSONITY_CATEGORY
        except Exception:
            pass

        if key in node_display_name_mappings:
            updated_display_name_mappings[updated_key] = node_display_name_mappings[key]

    return updated_class_mappings, updated_display_name_mappings


# VHS frontend hooks key off legacy VHS_* names in JS.
# Keep legacy keys as primary, and add Depersonity aliases for compatibility.
_ORIGINAL_NODE_CLASS_MAPPINGS = dict(NODE_CLASS_MAPPINGS)
_ORIGINAL_NODE_DISPLAY_NAME_MAPPINGS = dict(NODE_DISPLAY_NAME_MAPPINGS)

for _cls in NODE_CLASS_MAPPINGS.values():
    try:
        _cls.CATEGORY = DEPERSONITY_CATEGORY
    except Exception:
        pass

_DEPERSONITY_NODE_CLASS_MAPPINGS, _DEPERSONITY_NODE_DISPLAY_NAME_MAPPINGS = _apply_depersonity_mappings(
    _ORIGINAL_NODE_CLASS_MAPPINGS,
    _ORIGINAL_NODE_DISPLAY_NAME_MAPPINGS,
)

NODE_CLASS_MAPPINGS.update(_DEPERSONITY_NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(_DEPERSONITY_NODE_DISPLAY_NAME_MAPPINGS)

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
documentation.format_descriptions(_ORIGINAL_NODE_CLASS_MAPPINGS)
