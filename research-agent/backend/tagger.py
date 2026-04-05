"""
tagger.py
Tags papers using keyword matching as a fast fallback,
or uses LLM tags already extracted in the extractor step.
"""

KEYWORD_MAP = {
    "LLM": [
        "large language model", "llm", "gpt", "language model",
        "transformer", "instruction tuning", "chat", "text generation"
    ],
    "Agents": [
        "agent", "agentic", "autonomous", "tool use", "planning",
        "multi-agent", "workflow", "react", "chain-of-thought"
    ],
    "RAG": [
        "retrieval", "rag", "retrieval-augmented", "knowledge base",
        "document retrieval", "vector store", "indexing"
    ],
    "Computer Vision": [
        "image", "vision", "visual", "object detection", "segmentation",
        "diffusion", "vit", "convolutional", "video", "recognition"
    ],
    "NLP": [
        "natural language", "nlp", "text classification", "sentiment",
        "named entity", "question answering", "summarization"
    ],
    "Multimodal": [
        "multimodal", "vision-language", "vlm", "audio", "cross-modal",
        "clip", "image-text", "speech"
    ],
    "Efficiency": [
        "efficient", "compression", "pruning", "quantization",
        "distillation", "latency", "small model", "lightweight", "fast"
    ],
    "Robotics": [
        "robot", "robotics", "manipulation", "embodied", "navigation",
        "control", "simulation"
    ],
    "Reasoning": [
        "reasoning", "logic", "math", "theorem", "proof", "arithmetic",
        "chain of thought", "step-by-step"
    ],
    "Fine-tuning": [
        "fine-tun", "lora", "rlhf", "dpo", "alignment", "peft",
        "instruction follow", "adaptation"
    ],
    "Benchmarks": [
        "benchmark", "evaluation", "dataset", "leaderboard",
        "metric", "assessment"
    ],
    "Safety": [
        "safety", "alignment", "bias", "fairness", "toxicity",
        "adversarial", "jailbreak", "red team"
    ],
    "Diffusion": [
        "diffusion", "stable diffusion", "score matching",
        "denoising", "generative model", "ddpm"
    ],
}


def tag_paper(paper: dict) -> dict:
    """
    If LLM already provided tags, validate and return them.
    Otherwise fall back to keyword matching.
    """
    existing_tags = paper.get("tags", [])
    valid_tags = set(KEYWORD_MAP.keys()) | {"Other"}

    # Validate LLM tags
    validated = [t for t in existing_tags if t in valid_tags]

    if validated:
        paper["tags"] = validated
        return paper

    # Keyword fallback
    text = f"{paper.get('title', '')} {paper.get('summary', '')}".lower()
    matched = []
    for tag, keywords in KEYWORD_MAP.items():
        if any(kw in text for kw in keywords):
            matched.append(tag)

    paper["tags"] = matched if matched else ["Other"]
    return paper


if __name__ == "__main__":
    sample = {
        "title": "Efficient LoRA Fine-tuning for LLMs",
        "summary": "We propose an efficient fine-tuning approach using low-rank adaptation...",
        "tags": [],
    }
    result = tag_paper(sample)
    print("Tags:", result["tags"])
