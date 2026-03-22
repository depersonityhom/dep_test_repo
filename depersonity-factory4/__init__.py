from .nodes.ApiRequestNode import *
from .nodes.JsonParserNode import *
from .nodes.JsonBuilderNode import *
from .nodes.EmptyImageNode import *
from .nodes.LoadImageFromUrlNode import *
from .nodes.TextToImageNode import *
from .nodes.SaveVideoRGBA import *
from .nodes.RemoveEmptyLinesNode import *
from .nodes.MultilinePromptNode import *
from .nodes.OSSUploadNode import *
from .nodes.LoadAudioFromUrlNode import *
from .nodes.CombineImageAudioToVideoNode import *

DEPERSONITY_PREFIX = "Depersonity_"
DEPERSONITY_CATEGORY = "Depersonity"

NODE_CONFIG = {
    # Network nodes
    "API Request Node": {"class": APIRequestNode, "name": "API Request Node"},
    # Data processing nodes
    "JSON Parser Node": {"class": JsonParserNode, "name": "JSON解析器"},
    "JSON Builder Node": {"class": JsonBuilderNode, "name": "JSON构建器"},
    "RemoveEmptyLinesNode": {"class": RemoveEmptyLinesNode, "name": "Remove Empty Lines 🗑️"},
    # Text processing nodes
    "MultilinePromptNode": {"class": MultilinePromptNode, "name": "Multiline Prompt 📝"},
    # Cloud storage nodes
    "OSSUploadNode": {"class": OSSUploadNode, "name": "OSS Upload 📤"},
    # Image processing nodes
    "LoadImageFromUrlNode": {"class": LoadImageFromUrlNode, "name": "LoadImageFromUrlNode"},
    "TextToImageNode": {"class": TextToImageNode, "name": "Text To Image"},
    # Video processing nodes
    "SaveVideoRGBA": {"class": SaveVideoRGBA, "name": "Save Video (RGBA)"},
    "CombineImageAudioToVideoNode": {"class": CombineImageAudioToVideoNode, "name": "Combine Image+Audio → Video"},
    # Utility nodes
    "Empty Image Node": {"class": EmptyImageNode, "name": "Empty Image Node"},
    # Audio processing nodes
    "LoadAudioFromUrlNode": {"class": LoadAudioFromUrlNode, "name": "Load Audio From URL"},
}

NODE_CLASS_MAPPINGS = {k: v["class"] for k, v in NODE_CONFIG.items()}
NODE_DISPLAY_NAME_MAPPINGS = {k: v["name"] for k, v in NODE_CONFIG.items()}


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


# Keep legacy keys for old workflows, add Depersonity aliases for new naming.
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

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
