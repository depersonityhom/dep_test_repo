from .nodes.save_load_pose import TSSavePoseDataAsPickle, TSLoadPoseDataPickle
from .nodes.openpose_smoother import KPSSmoothPoseDataAndRender
from .nodes.load_video_batch import LoadVideoBatchListFromDir
from .nodes.rename_files import RenameFilesInDir
from .nodes.color_match import TSColorMatchSequentialBias
from .nodes.preview_image_metadata import PreviewImageNoMetadata
from .nodes.video_combine_metadata import TSVideoCombineNoMetadata
from .nodes.upscaler import TSUpscaler
from .nodes.downscaler import TSDownscaler
from .nodes.denoise import TSDenoise
from .nodes.group_mode_toggle import TSGroupModeToggle
from .nodes.rich_note import TSRichNote

DEPERSONITY_CATEGORY = "Depersonity"

# Меняем зеленую верхнюю подпись у всех нод без правки каждого файла.
for _cls in [
    TSSavePoseDataAsPickle,
    TSLoadPoseDataPickle,
    KPSSmoothPoseDataAndRender,
    LoadVideoBatchListFromDir,
    RenameFilesInDir,
    TSColorMatchSequentialBias,
    PreviewImageNoMetadata,
    TSVideoCombineNoMetadata,
    TSUpscaler,
    TSDownscaler,
    TSDenoise,
    TSGroupModeToggle,
    TSRichNote,
]:
    _cls.CATEGORY = DEPERSONITY_CATEGORY

NODE_CLASS_MAPPINGS = {
    "Depersonity_TSSavePoseDataAsPickle": TSSavePoseDataAsPickle,
    "Depersonity_TSLoadPoseDataPickle": TSLoadPoseDataPickle,
    "Depersonity_TSPoseDataSmoother": KPSSmoothPoseDataAndRender,
    "Depersonity_TSLoadVideoBatchListFromDir": LoadVideoBatchListFromDir,
    "Depersonity_TSRenameFilesInDir": RenameFilesInDir,
    "Depersonity_TSColorMatch": TSColorMatchSequentialBias,
    "Depersonity_TSPreviewImageNoMetadata": PreviewImageNoMetadata,
    "Depersonity_TSVideoCombineNoMetadata": TSVideoCombineNoMetadata,
    "Depersonity_TSUpscaler": TSUpscaler,
    "Depersonity_TSDownscaler": TSDownscaler,
    "Depersonity_TSDenoise": TSDenoise,
    "Depersonity_TSGroupModeToggle": TSGroupModeToggle,
    "Depersonity_TSRichNote": TSRichNote,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Depersonity_TSSavePoseDataAsPickle": "Depersonity Save Pose Data (PKL)",
    "Depersonity_TSLoadPoseDataPickle": "Depersonity Load Pose Data (PKL)",
    "Depersonity_TSPoseDataSmoother": "Depersonity Pose Data Smoother",
    "Depersonity_TSLoadVideoBatchListFromDir": "Depersonity Load Video Batch List From Dir",
    "Depersonity_TSRenameFilesInDir": "Depersonity Rename Files In Dir",
    "Depersonity_TSColorMatch": "Depersonity Color Match",
    "Depersonity_TSPreviewImageNoMetadata": "Depersonity Preview Image No Metadata",
    "Depersonity_TSVideoCombineNoMetadata": "Depersonity Video Combine No Metadata",
    "Depersonity_TSUpscaler": "Depersonity Upscaler",
    "Depersonity_TSDownscaler": "Depersonity Downscaler",
    "Depersonity_TSDenoise": "Depersonity Denoise",
    "Depersonity_TSGroupModeToggle": "Depersonity Group Mode Toggle",
    "Depersonity_TSRichNote": "Depersonity Rich Note",
}

WEB_DIRECTORY = "web"
