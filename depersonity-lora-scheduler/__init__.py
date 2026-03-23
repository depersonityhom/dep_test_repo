from .nodes.adaptive_lora_scheduler import AdaptiveLoraScheduler

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


NODE_CLASS_MAPPINGS = {"AdaptiveLoraScheduler": AdaptiveLoraScheduler}

NODE_DISPLAY_NAME_MAPPINGS = {"AdaptiveLoraScheduler": "Adaptive LoRA Scheduler"}

NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = _apply_depersonity_mappings(
    NODE_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS,
)

WEB_DIRECTORY = "./web"

print("\033[94mAdaptive LoRA Scheduler Node: \033[92mLoaded\033[0m")
