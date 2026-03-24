#!/bin/bash
set -e
export TERM=xterm
# Глушим лишние вопросы от Git
export GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -q"

# --- ЦВЕТА ---
NC='\033[0m'; GREEN='\033[1;32m'; YELLOW='\033[1;33m'; 
MAGENTA='\033[1;35m'; CYAN='\033[1;36m'; WHITE='\033[1;37m'; GRAY='\033[0;90m'

# --- НАСТРОЙКИ ---
WORKSPACE="/workspace"
COMFYUI_DIR="${WORKSPACE}/ComfyUI"
VENV_PATH="${WORKSPACE}/venv"
MY_REPO_URL="https://huggingface.co/depersonity/wf_local/resolve/main"
LIVEPORTRAIT_REPO_URL="https://huggingface.co/Kijai/LivePortrait_safetensors/resolve/main"
SAM2_REPO_URL="https://huggingface.co/Kijai/sam2-safetensors/resolve/main"
CODEFORMER_URL="https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth"
GFPGAN_URL="https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth"
FACEDT_RESNET50_URL="https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth"
FACEDT_MOBILENET_URL="https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_mobilenet0.25_Final.pth"
FACEDT_YOLOV5L_URL="https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/yolov5l-face.pth"
FACEDT_YOLOV5N_URL="https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/yolov5n-face.pth"
FACEPARSING_URL="https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/parsing_parsenet.pth"
INSIGHTFACE_BUFFALO_URL="https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"

# Твой обновленный репозиторий
DEP_NODES_REPO="https://github.com/depersonityhom/dep_test_repo.git"
EXTRA_NODES=("https://github.com/PozzettiAndrea/ComfyUI-SAM3")

# Режим тишины (по умолчанию выключен, чтобы не скрывать причины падений)
QUIET="${QUIET:-0}"
if [[ "$QUIET" == "1" ]]; then
    exec 3>&2
    exec 2>/dev/null
fi

# --- ФУНКЦИИ ---
function log_step() {
    echo -e "\n${MAGENTA}───[ STEP $1 ]──────────────────────────────────────────${NC}"
    echo -e "${WHITE}  🚀 $2${NC}"
}

function status_msg() {
    echo -ne "${CYAN}[⚙️]${NC} $1..."
}

function status_ok() {
    echo -e " ${GREEN}[DONE]${NC}"
}

function download_resource() {
    local dir="$1"
    local url="$2"
    local desc="$3"
    local fname=$(basename "$url")
    mkdir -p "$dir"
    
    if [[ -f "$dir/$fname" ]]; then
        echo -e "${GRAY}[✔] $desc${NC}"
    else
        echo -ne "${YELLOW}[📥]${NC} $desc..."
        if [[ -n "$HF_TOKEN" ]]; then
            wget --header="Authorization: Bearer $HF_TOKEN" -q --show-progress=off -nc --content-disposition -P "$dir" "$url"
        else
            wget -q --show-progress=off -nc --content-disposition -P "$dir" "$url"
        fi
        echo -e " ${GREEN}[OK]${NC}"
    fi
}

function download_and_extract_zip() {
    local zip_dir="$1"
    local url="$2"
    local desc="$3"
    local fname=$(basename "$url")
    mkdir -p "$zip_dir"
    if [[ ! -f "$zip_dir/$fname" ]]; then
        echo -ne "${YELLOW}[📥]${NC} $desc..."
        if [[ -n "$HF_TOKEN" ]]; then
            wget --header="Authorization: Bearer $HF_TOKEN" -q --show-progress=off -nc --content-disposition -P "$zip_dir" "$url"
        else
            wget -q --show-progress=off -nc --content-disposition -P "$zip_dir" "$url"
        fi
        echo -e " ${GREEN}[OK]${NC}"
    fi
    python3 - <<PY
import zipfile
from pathlib import Path
zip_path = Path(r"$zip_dir") / "$fname"
with zipfile.ZipFile(zip_path, "r") as z:
    z.extractall(Path(r"$zip_dir"))
print("extracted", zip_path.name, "to", r"$zip_dir")
PY
}

# --- ПРОЦЕСС ---

log_step "01" "ПОДГОТОВКА ОКРУЖЕНИЯ"
if [[ ! -d "$VENV_PATH" ]]; then
    status_msg "Создание venv"
    python3 -m venv "$VENV_PATH"
    status_ok
fi
source "$VENV_PATH/bin/activate"

log_step "02" "РАЗВЕРТЫВАНИЕ ЯДРА"
if [[ ! -d "${COMFYUI_DIR}" ]]; then
    status_msg "Клонирование ComfyUI"
    git clone https://github.com/comfyanonymous/ComfyUI.git "${COMFYUI_DIR}" -q
    status_ok
fi
cd "${COMFYUI_DIR}"

status_msg "Установка зависимостей ядра"
pip install --upgrade pip -q
pip install -r requirements.txt -q
# Node Manager для полного UI
pip install -U --pre comfyui-manager -q || true
status_ok

log_step "03" "СИНХРОНИЗАЦИЯ ТВОИХ НОД (DEPERSONITY)"
nodes_dir="${COMFYUI_DIR}/custom_nodes"
workflow_dir="${COMFYUI_DIR}/user/default/workflows"
temp_repo="/tmp/dep_test_repo"

mkdir -p "$workflow_dir"

status_msg "Загрузка обновлений из GitHub"
rm -rf "$temp_repo"
git clone --depth 1 "$DEP_NODES_REPO" "$temp_repo" -q
status_ok

status_msg "Установка нод в custom_nodes (каждая папка отдельно)"
mkdir -p "$nodes_dir"

# Ставим как отдельные custom_nodes директории (так ComfyUI подхватывает WEB_DIRECTORY и JS-расширения)
DEP_NODE_DIRS=(
    "ComfyUI-Manager"
    "depersonity-lora-scheduler"
    "depersonity-kjnodes"
    "depersonity-sam2-segmentation"
    "depersonity-zmg-nodes"
    "depersonity-wanvideo-wrapper"
    "depersonity-wananimate-preprocess"
    "depersonity-videohelpersuite"
    "depersonity-ts-utils"
    "depersonity-liveportrait"
    "depersonity-impact-pack"
    "depersonity-facerestore-cf"
)

for d in "${DEP_NODE_DIRS[@]}"; do
    if [[ -d "$temp_repo/$d" ]]; then
        rm -rf "$nodes_dir/$d"
        cp -rf "$temp_repo/$d" "$nodes_dir/$d" 2>/dev/null || true
        rm -rf "$nodes_dir/$d/.git" 2>/dev/null || true
    fi
done

# Доп. python-скрипты (если есть)
if [[ -f "$temp_repo/websocket_image_save.py" ]]; then
    cp -f "$temp_repo/websocket_image_save.py" "$nodes_dir/websocket_image_save.py" 2>/dev/null || true
fi

# Копируем JSON в workflows для удобства запуска
find "$temp_repo" -maxdepth 1 -name "*.json" -exec cp {} "$workflow_dir/" \; 2>/dev/null || true
find "$temp_repo/lite_version" -maxdepth 1 -name "*.json" -exec cp {} "$workflow_dir/" \; 2>/dev/null || true

# Установка зависимостей всех включенных нод
while IFS= read -r -d '' req; do
    pip install -q --no-cache-dir -r "$req" || true
done < <(find "$nodes_dir" -maxdepth 2 -type f -name "requirements.txt" -print0)
status_ok

log_step "04" "ДОПОЛНИТЕЛЬНЫЕ РАСШИРЕНИЯ"
for repo in "${EXTRA_NODES[@]}"; do
    name="${repo##*/}"
    if [[ ! -d "${nodes_dir}/${name}" ]]; then
        status_msg "Установка $name"
        git clone --depth 1 "${repo}" "${nodes_dir}/${name}" -q
        [[ -f "${nodes_dir}/${name}/requirements.txt" ]] && pip install -q --no-cache-dir -r "${nodes_dir}/${name}/requirements.txt"
        status_ok
    fi
done

log_step "05" "МОДЕЛИ (Depersonity/wf_local)"
# WanVideo wrapper читает модели из:
# - models/diffusion_models (основная модель)
# - models/vae
# - models/text_encoders (UMT5)
# - models/clip_vision
# - models/controlnet
# - models/loras
# WanAnimate preprocess читает из models/detection
# TS utils denoise читает из models/upscale_models
# Face restore читает из models/facerestore_models

# Основные модели WanVideo
download_resource "models/text_encoders" "$MY_REPO_URL/umt5_xxl_fp8_e4m3fn_scaled.safetensors" "UMT5 (text encoder)"
download_resource "models/clip_vision" "$MY_REPO_URL/clip_vision_h.safetensors" "CLIP Vision"
download_resource "models/vae" "$MY_REPO_URL/wan_2.1_vae.safetensors" "Wan VAE"
download_resource "models/diffusion_models" "$MY_REPO_URL/Wan2_2-Animate-14B_fp8_scaled_e4m3fn_KJ_v2.safetensors" "Wan main model"
download_resource "models/controlnet" "$MY_REPO_URL/Wan21_Uni3C_controlnet_fp16.safetensors" "Uni3C ControlNet"

# LoRA (кладём в models/loras)
download_resource "models/loras" "$MY_REPO_URL/lightx2v_I2V_14B_480p_cfg_step_distill_rank256_bf16.safetensors" "LoRA: distill (lightx2v)"
download_resource "models/loras" "$MY_REPO_URL/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors" "LoRA: 4steps high-noise"
download_resource "models/loras" "$MY_REPO_URL/Wan21_PusaV1_LoRA_14B_rank512_bf16.safetensors" "LoRA: PusaV1"
download_resource "models/loras" "$MY_REPO_URL/Wan2.2-Fun-A14B-InP-low-noise-HPS2.1.safetensors" "LoRA: low-noise"

# Детекторы для pose/face preprocess (models/detection)
download_resource "models/detection" "$MY_REPO_URL/vitpose_h_wholebody_model.onnx" "ViTPose wholebody (onnx)"
download_resource "models/detection" "$MY_REPO_URL/vitpose_h_wholebody_data.bin" "ViTPose data (bin)"
download_resource "models/detection" "$MY_REPO_URL/yolov10m.onnx" "YOLOv10m (onnx)"

# SAM2 (models/sam2)
download_resource "models/sam2" "$SAM2_REPO_URL/sam2.1_hiera_base_plus-fp16.safetensors" "SAM2.1 base+ (fp16)"

# LivePortrait модели (models/liveportrait)
download_resource "models/liveportrait" "$LIVEPORTRAIT_REPO_URL/appearance_feature_extractor.safetensors" "LivePortrait: appearance_feature_extractor"
download_resource "models/liveportrait" "$LIVEPORTRAIT_REPO_URL/motion_extractor.safetensors" "LivePortrait: motion_extractor"
download_resource "models/liveportrait" "$LIVEPORTRAIT_REPO_URL/warping_module.safetensors" "LivePortrait: warping_module"
download_resource "models/liveportrait" "$LIVEPORTRAIT_REPO_URL/spade_generator.safetensors" "LivePortrait: spade_generator"
download_resource "models/liveportrait" "$LIVEPORTRAIT_REPO_URL/stitching_retargeting_module.safetensors" "LivePortrait: stitching_retargeting_module"
download_resource "models/liveportrait" "$LIVEPORTRAIT_REPO_URL/landmark.onnx" "LivePortrait: landmark.onnx (CropperInsightFace)"
download_resource "models/liveportrait" "$LIVEPORTRAIT_REPO_URL/landmark_model.pth" "LivePortrait: landmark_model.pth"

# Animal mode (опционально)
download_resource "models/liveportrait/animal" "$LIVEPORTRAIT_REPO_URL/animal/appearance_feature_extractor.safetensors" "LivePortrait animal: appearance_feature_extractor"
download_resource "models/liveportrait/animal" "$LIVEPORTRAIT_REPO_URL/animal/motion_extractor.safetensors" "LivePortrait animal: motion_extractor"
download_resource "models/liveportrait/animal" "$LIVEPORTRAIT_REPO_URL/animal/warping_module.safetensors" "LivePortrait animal: warping_module"
download_resource "models/liveportrait/animal" "$LIVEPORTRAIT_REPO_URL/animal/spade_generator.safetensors" "LivePortrait animal: spade_generator"
download_resource "models/liveportrait/animal" "$LIVEPORTRAIT_REPO_URL/animal/stitching_retargeting_module.safetensors" "LivePortrait animal: stitching_retargeting_module"

# Denoise модель (SwinIR) для TSDenoise (models/upscale_models)
download_resource "models/upscale_models" "$MY_REPO_URL/005_colorDN_DFWB_s128w8_SwinIR-M_noise15.pth" "SwinIR denoise (noise15)"

# Прочее (если понадобится)
download_resource "models/promptmodels" "$MY_REPO_URL/low.pt" "promptmodels low.pt"

# Face restore models (models/facerestore_models)
download_resource "models/facerestore_models" "$CODEFORMER_URL" "CodeFormer model (codeformer.pth)"
download_resource "models/facerestore_models" "$GFPGAN_URL" "GFPGANv1.4 (optional)"

# Face detection/parsing for face restore (models/facedetection)
download_resource "models/facedetection" "$FACEDT_RESNET50_URL" "Face detection: retinaface_resnet50"
download_resource "models/facedetection" "$FACEDT_MOBILENET_URL" "Face detection: retinaface_mobile0.25"
download_resource "models/facedetection" "$FACEDT_YOLOV5L_URL" "Face detection: yolov5l-face"
download_resource "models/facedetection" "$FACEDT_YOLOV5N_URL" "Face detection: yolov5n-face"
download_resource "models/facedetection" "$FACEPARSING_URL" "Face parsing: parsenet"

# InsightFace models (models/insightface/buffalo_l) - required if using InsightFace cropper/detector
if [[ ! -d "models/insightface/buffalo_l" ]]; then
    download_and_extract_zip "models/insightface" "$INSIGHTFACE_BUFFALO_URL" "InsightFace buffalo_l (zip)"
fi

log_step "06" "СТАРТ"
echo -e "${GREEN}✨ Все файлы из репозитория успешно перенесены в custom_nodes.${NC}"
echo -e "${GRAY}------------------------------------------------------------${NC}"
echo -e "${YELLOW}ComfyUI будет запущен как сервер и скрипт будет \"висеть\" пока сервер работает — это нормально.${NC}"
echo -e "${YELLOW}GUI откроется по адресу: http://0.0.0.0:8188${NC}"
echo -e "${GRAY}Если хочешь запустить в фоне и вернуть контроль терминала: RUN_IN_BACKGROUND=1 ./setup.sh${NC}"

# В ноутбуках по умолчанию запускаем в фоне, чтобы cell не \"висел\"
if [[ -z "${RUN_IN_BACKGROUND+x}" ]]; then
    if [[ -n "${COLAB_RELEASE_TAG:-}" || -n "${JPY_PARENT_PID:-}" || -n "${JUPYTERHUB_USER:-}" ]]; then
        RUN_IN_BACKGROUND=1
    else
        RUN_IN_BACKGROUND=0
    fi
fi

# Возвращаем ошибки в консоль (если включали QUIET)
if [[ "$QUIET" == "1" ]]; then
    exec 2>&3
fi
if [[ "${RUN_IN_BACKGROUND}" == "1" ]]; then
    nohup python3 main.py --listen 0.0.0.0 --port 8188 --enable-cors-header --enable-manager > "${WORKSPACE}/comfyui.log" 2>&1 &
    echo -e "${GREEN}✅ ComfyUI запущен в фоне. Логи: ${WORKSPACE}/comfyui.log${NC}"
else
    python3 main.py --listen 0.0.0.0 --port 8188 --enable-cors-header --enable-manager 2>&1 | tee "${WORKSPACE}/comfyui.log"
fi
