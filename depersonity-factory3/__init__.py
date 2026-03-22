from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

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


NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = _apply_depersonity_mappings(
    NODE_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS,
)

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
