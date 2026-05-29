import re
from typing import Optional

from analyzers.classifier import (
    CATEGORY_IMAGE_TO_IMAGE,
    CATEGORY_IMAGE_TO_VIDEO,
    CATEGORY_LABELS,
    CATEGORY_TEXT_LLM,
    CATEGORY_TEXT_TO_IMAGE,
    CATEGORY_TEXT_TO_VIDEO,
)
from analyzers.gguf_analyzer import extract_quant, extract_size_gb
from collectors.base import ModelRecord

PARAM_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*[Bb](?:illion)?|\b(\d+(?:\.\d+)?)[Bb]\b",
)

PLATFORM_LABELS = {
    "huggingface": "HUGGINGFACE",
    "github": "GITHUB",
    "civitai": "CIVITAI",
    "modelscope": "MODELSCOPE",
}


def extract_params_billion(name: str) -> Optional[str]:
    match = PARAM_PATTERN.search(name)
    if not match:
        return None
    value = match.group(1) or match.group(2)
    if not value:
        return None
    num = float(value)
    if num == int(num):
        return f"{int(num)} Billion Params"
    return f"{num} Billion Params"


def _slug_for_ollama(name: str) -> str:
    base = name.split("/")[-1] if "/" in name else name
    base = re.sub(r"-?GGUF.*$", "", base, flags=re.IGNORECASE)
    base = re.sub(r"[-_](Q\d+.*|IQ\d+.*)$", "", base, flags=re.IGNORECASE)
    base = base.lower().replace("_", "-")
    param = PARAM_PATTERN.search(name)
    if param:
        p = param.group(1) or param.group(2)
        short = base.split("-")[0] if "-" in base else base
        return f"{short}:{p}b" if p else short
    return base.lower()[:40]


def recommend_vram(model: dict) -> str:
    category = model.get("category", "")
    size_gb = extract_size_gb(model.get("model_size", "") or model.get("model_name", ""))
    params = extract_params_billion(model.get("model_name", ""))

    if category == CATEGORY_TEXT_LLM:
        if size_gb is not None:
            vram = max(4, int(size_gb * 1.2))
            return f"{vram}GB VRAM（适合 RTX 3060 12G 及以上）"
        if params:
            num = float(re.search(r"[\d.]+", params).group())
            if num <= 7:
                return "8GB VRAM（适合 RTX 4060 8G 及以上）"
            if num <= 14:
                return "12GB VRAM（适合 RTX 3060 12G 及以上）"
            if num <= 32:
                return "16GB VRAM（适合 RTX 4060Ti 16G 及以上）"
            return "24GB+ VRAM（适合 RTX 3090 / 4090）"
        return "8GB+ VRAM（视量化方式而定）"

    if category == CATEGORY_TEXT_TO_IMAGE:
        name = model.get("model_name", "").lower()
        if "flux" in name:
            return "12GB VRAM（适合 RTX 3060 12G / 4070 及以上）"
        if "sdxl" in name or "xl" in name:
            return "8GB VRAM（适合 RTX 3060 12G 及以上）"
        return "6GB VRAM（适合 RTX 3060 / 4060 及以上）"

    if category == CATEGORY_IMAGE_TO_IMAGE:
        return "10GB VRAM（ControlNet 额外占用，建议 3060 12G 及以上）"

    if category == CATEGORY_TEXT_TO_VIDEO:
        return "16GB VRAM（建议 RTX 4060Ti 16G / 3090 及以上）"

    if category == CATEGORY_IMAGE_TO_VIDEO:
        return "12GB VRAM（建议 RTX 3060 12G / 4070Ti 及以上）"

    return "视具体配置而定"


def generate_summary(model: dict) -> str:
    category = model.get("category", "")
    platform = PLATFORM_LABELS.get(model.get("source_platform", ""), "AI平台")
    name = model.get("model_name", "")

    summaries = {
        CATEGORY_TEXT_LLM: (
            f"此项发布源自 {platform}。该模型主要负责大语言模型（LLM）核心推理，"
            f"具备优秀的通用对话与指令跟随能力，支持本地 GGUF 量化部署，"
            f"可有效降低显存占用，适合日常对话、代码辅助与知识问答场景。"
        ),
        CATEGORY_TEXT_TO_IMAGE: (
            f"此项发布源自 {platform}。该模型专注于文生图（Text-to-Image）生成，"
            f"可根据文字描述生成高质量图像，适用于插画创作、概念设计、"
            f"ComfyUI / Stable Diffusion 工作流部署。"
        ),
        CATEGORY_IMAGE_TO_IMAGE: (
            f"此项发布源自 {platform}。该模型支持图生图（Image-to-Image）变换，"
            f"可基于参考图进行风格迁移、重绘与细节增强，"
            f"适合 ControlNet、Img2Img 等进阶创作流程。"
        ),
        CATEGORY_TEXT_TO_VIDEO: (
            f"此项发布源自 {platform}。该模型支持文生视频（Text-to-Video），"
            f"可根据文字描述直接生成视频片段，适用于短视频创作、"
            f"动画预演与内容生产自动化。"
        ),
        CATEGORY_IMAGE_TO_VIDEO: (
            f"此项发布源自 {platform}。该模型支持图生视频（Image-to-Video），"
            f"可将静态图片转化为动态视频，保持角色与场景一致性，"
            f"适合 Wan2.1、Animate 等图转视频工作流。"
        ),
    }
    base = summaries.get(category, f"此项发布源自 {platform}，模型名称：{name}。")
    if model.get("description") and len(model["description"]) > 10:
        desc = model["description"][:120]
        return f"{base} 补充说明：{desc}"
    return base


def generate_run_command(model: dict) -> tuple[str, str]:
    """返回 (命令标题, 命令内容)"""
    category = model.get("category", "")
    name = model.get("model_name", "")
    url = model.get("download_url", "")

    if category == CATEGORY_TEXT_LLM and model.get("is_gguf"):
        slug = _slug_for_ollama(name)
        return "OLLAMA 运行命令", f"ollama run {slug}"

    if category == CATEGORY_TEXT_LLM:
        hf_name = name if "/" in name else name
        return "本地加载命令", f"llama-cpp-python 或 ollama 加载 {hf_name}"

    if category == CATEGORY_TEXT_TO_IMAGE:
        return "推荐部署方式", "ComfyUI / Stable Diffusion WebUI + 对应 Checkpoint/LoRA"

    if category == CATEGORY_IMAGE_TO_IMAGE:
        return "推荐部署方式", "ComfyUI Img2Img 或 ControlNet 工作流"

    if category in (CATEGORY_TEXT_TO_VIDEO, CATEGORY_IMAGE_TO_VIDEO):
        return "推荐部署方式", "ComfyUI + Wan2.1 / CogVideo 等工作流节点"

    return "前往仓库", url


def build_tags(model: dict) -> list[dict]:
    tags = []
    if model.get("is_gguf"):
        tags.append({"text": "GGUF", "style": "gray"})
    if model.get("quant_method"):
        tags.append({"text": model["quant_method"], "style": "green"})
    params = extract_params_billion(model.get("model_name", ""))
    if params:
        tags.append({"text": params, "style": "purple"})
    if model.get("model_size"):
        tags.append({"text": model["model_size"], "style": "blue"})
    if model.get("model_type") == "lora" or "lora" in model.get("model_name", "").lower():
        tags.append({"text": "LoRA", "style": "orange"})
    if not tags:
        tags.append({"text": model.get("source_platform", "model").upper(), "style": "gray"})
    return tags


def enrich_model_card(model: dict) -> dict:
    combined = " ".join([model.get("model_name", ""), model.get("description", "")])
    if not model.get("quant_method"):
        model["quant_method"] = extract_quant(combined)

    category = model.get("category") or model.get("model_type", CATEGORY_TEXT_LLM)
    model["category"] = category
    model["category_label"] = CATEGORY_LABELS.get(category, category)
    model["platform_label"] = PLATFORM_LABELS.get(
        model.get("source_platform", ""), model.get("source_platform", "").upper()
    )
    model["tags"] = build_tags(model)
    model["brain_summary"] = generate_summary(model)
    model["vram_recommend"] = recommend_vram(model)
    cmd_title, cmd_body = generate_run_command(model)
    model["cmd_title"] = cmd_title
    model["cmd_body"] = cmd_body
    return model
