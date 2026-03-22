#!/bin/bash
set -e
source /venv/main/bin/activate

# --- НАСТРОЙКИ ---
# Твой новый приватный склад моделей
MY_HF_REPO="https://huggingface.co/depersonity/wf_local/resolve/main"
HF_TOKEN="ВАШ_ТОКЕН_ЗДЕСЬ"

# Твой GitHub с нодами
ALLNODES_REPO="https://github.com/depersonityhom/dep.git"
ALLNODES_BRANCH="main"

WORKSPACE=${WORKSPACE:-/workspace}
COMFYUI_DIR="${WORKSPACE}/ComfyUI"

# --- СПИСКИ МОДЕЛЕЙ (уже с твоими именами файлов) ---
CLIP_MODELS=("$MY_HF_REPO/umt5_xxl_fp8_e4m3fn_scaled.safetensors")
CLIP_VISION_MODELS=("$MY_HF_REPO/clip_vision_h.safetensors")
VAE_MODELS=("$MY_HF_REPO/wan_2.1_vae.safetensors")
DIFFUSION_MODELS=("$MY_HF_REPO/Wan2_2-Animate-14B_fp8_scaled_e4m3fn_KJ_v2.safetensors")
CONTROLNET_MODELS=("$MY_HF_REPO/Wan21_Uni3C_controlnet_fp16.safetensors")

DETECTION_MODELS=(
    "$MY_HF_REPO/yolov10m.onnx"
    "$MY_HF_REPO/vitpose_h_wholebody_data.bin"
    "$MY_HF_REPO/vitpose_h_wholebody_model.onnx"
)

UPSCALER_MODELS=(
    "$MY_HF_REPO/low.pt"
    "$MY_HF_REPO/005_colorDN_DFWB_s128w8_SwinIR-M_noise15.pth"
)

LORAS=(
    "$MY_HF_REPO/lightx2v_I2V_14B_480p_cfg_step_distill_rank256_bf16.safetensors"
    "$MY_HF_REPO/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors"
    "$MY_HF_REPO/Wan2.2-Fun-A14B-InP-low-noise-HPS2.1.safetensors"
    "$MY_HF_REPO/Wan21_PusaV1_LoRA_14B_rank512_bf16.safetensors"
)

# Функция для "умной" загрузки (проверяет наличие файла перед скачиванием)
function provisioning_get_files() {
    local dir="$1"
    shift
    local files=("$@")
    mkdir -p "$dir"
    for url in "${files[@]}"; do
        local filename=$(basename "${url%%?*}")
        if [[ -f "${dir}/${filename}" ]] && [[ $(stat -c%s "${dir}/${filename}") -gt 1000000 ]]; then
            echo "✅ $filename уже на месте."
            continue
        fi
        echo "📥 Скачиваю $filename..."
        wget --header="Authorization: Bearer $HF_TOKEN" -q -c --content-disposition -P "$dir" "$url" || true
    done
}

# --- ОСНОВНОЙ ПРОЦЕСС ---

echo "🚀 Начинаю установку окружения..."

# 1. ComfyUI
if [[ ! -d "${COMFYUI_DIR}" ]]; then
    git clone https://github.com/comfyanonymous/ComfyUI.git "${COMFYUI_DIR}"
fi
cd "${COMFYUI_DIR}"
pip install --no-cache-dir -r requirements.txt

# 2. Твои Custom Nodes (из твоего GitHub)
rm -rf custom_nodes
git clone --depth 1 --branch "${ALLNODES_BRANCH}" "${ALLNODES_REPO}" custom_nodes
# Доп. нода SAM3 (если нужна)
git clone --depth 1 https://github.com/PozzettiAndrea/ComfyUI-SAM3 custom_nodes/ComfyUI-SAM3 || true

# Установка зависимостей для всех нод
find custom_nodes -type f -name requirements.txt -exec pip install --no-cache-dir -r {} \;

# 3. Твои модели (из твоего HF)
provisioning_get_files "models/clip" "${CLIP_MODELS[@]}"
provisioning_get_files "models/clip_vision" "${CLIP_VISION_MODELS[@]}"
provisioning_get_files "models/vae" "${VAE_MODELS[@]}"
provisioning_get_files "models/diffusion_models" "${DIFFUSION_MODELS[@]}"
provisioning_get_files "models/controlnet" "${CONTROLNET_MODELS[@]}"
provisioning_get_files "models/detection" "${DETECTION_MODELS[@]}"
provisioning_get_files "models/loras" "${LORAS[@]}"
provisioning_get_files "models/upscale_models" "${UPSCALER_MODELS[@]}"

echo "✨ Установка завершена! Запускаю ComfyUI..."
python main.py --listen 0.0.0.0 --port 8188
