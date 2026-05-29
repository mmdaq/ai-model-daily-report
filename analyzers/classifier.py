from collectors.base import ModelRecord

# 五大类别（优先级从高到低匹配）
CATEGORY_TEXT_LLM = "text_llm"
CATEGORY_TEXT_TO_IMAGE = "text_to_image"
CATEGORY_IMAGE_TO_IMAGE = "image_to_image"
CATEGORY_TEXT_TO_VIDEO = "text_to_video"
CATEGORY_IMAGE_TO_VIDEO = "image_to_video"

CATEGORY_LABELS = {
    CATEGORY_TEXT_LLM: "文本大模型 (LLM)",
    CATEGORY_TEXT_TO_IMAGE: "文生图模型",
    CATEGORY_IMAGE_TO_IMAGE: "图生图模型",
    CATEGORY_TEXT_TO_VIDEO: "文生视频模型",
    CATEGORY_IMAGE_TO_VIDEO: "图生视频模型",
}

IMAGE_TO_VIDEO_KW = [
    "i2v", "image-to-video", "image2video", "img2video", "img-to-video", "图生视频",
]
TEXT_TO_VIDEO_KW = [
    "t2v", "text-to-video", "text2video", "txt2video", "文生视频", "text to video",
]
IMAGE_TO_IMAGE_KW = [
    "img2img", "image-to-image", "image2image", "controlnet", "ip-adapter",
    "ipadapter", "图生图", "inpaint", "outpaint",
]
TEXT_TO_IMAGE_KW = [
    "flux", "sdxl", "sd1.5", "sd3", "stable-diffusion", "stable_diffusion",
    "checkpoint", "txt2img", "text-to-image", "text2image", "diffusers",
    "lora", "locon", "pony", "illustrious", "文生图", "text-to-image",
]
TEXT_LLM_KW = [
    "gguf", "llm", "qwen", "deepseek", "mistral", "llama", "gemma", "phi",
    "internlm", "chatglm", "yi-", "baichuan", "gpt", "bert", "language-model",
    "text-generation", "instruct", "coder",
]


def _contains_any(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def _combined_text(record: ModelRecord) -> str:
    return " ".join(
        [
            record.model_name,
            record.model_type,
            record.description,
            " ".join(record.tags),
        ]
    ).lower()


def classify_category(record: ModelRecord) -> str:
    text = _combined_text(record)

    if _contains_any(text, IMAGE_TO_VIDEO_KW):
        return CATEGORY_IMAGE_TO_VIDEO
    if _contains_any(text, TEXT_TO_VIDEO_KW):
        return CATEGORY_TEXT_TO_VIDEO
    if _contains_any(text, IMAGE_TO_IMAGE_KW):
        return CATEGORY_IMAGE_TO_IMAGE
    if _contains_any(text, TEXT_TO_IMAGE_KW):
        return CATEGORY_TEXT_TO_IMAGE
    if record.is_gguf or _contains_any(text, TEXT_LLM_KW):
        return CATEGORY_TEXT_LLM

    if record.source_platform == "civitai":
        if record.model_type in ("checkpoint", "lora", "vae", "workflow"):
            return CATEGORY_TEXT_TO_IMAGE
    if record.source_platform == "github":
        if _contains_any(text, ["video", "wan", "animate"]):
            return CATEGORY_TEXT_TO_VIDEO
        if _contains_any(text, ["comfyui", "flux", "sdxl"]):
            return CATEGORY_TEXT_TO_IMAGE

    pipeline = (record.description or "").lower()
    if pipeline in ("text-generation", "text2text-generation", "question-answering"):
        return CATEGORY_TEXT_LLM
    if pipeline in ("text-to-image", "text-to-video", "image-to-video"):
        mapping = {
            "text-to-image": CATEGORY_TEXT_TO_IMAGE,
            "text-to-video": CATEGORY_TEXT_TO_VIDEO,
            "image-to-video": CATEGORY_IMAGE_TO_VIDEO,
        }
        return mapping.get(pipeline, CATEGORY_TEXT_LLM)

    return CATEGORY_TEXT_LLM


def classify(record: ModelRecord) -> ModelRecord:
    text = _combined_text(record)

    if record.is_gguf or _contains_any(text, ["gguf"]):
        record.is_gguf = 1

    record.model_type = classify_category(record)
    return record
