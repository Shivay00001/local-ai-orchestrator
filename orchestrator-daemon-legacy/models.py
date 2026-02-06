from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class ModelTier(Enum):
    TINY = "tiny"     # 1-3B
    SMALL = "small"   # 7B
    MEDIUM = "medium" # 13B
    LARGE = "large"   # 32B+

class ModelInfo(BaseModel):
    name: str
    tier: ModelTier
    vram_required_gb: float

# Built-in Tier Mappings (Ollama defaults)
TIER_MODELS = {
    ModelTier.TINY: "phi3:tiny",      # Phi-3 Mini (3.8B)
    ModelTier.SMALL: "llama3:8b",     # Llama 3 8B
    ModelTier.MEDIUM: "mistral:7b",   # Mistral 7B (often fits Small, but mapping here)
    ModelTier.LARGE: "command-r:latest" # Command R (35B)
}

class ModelSelector:
    @staticmethod
    def select_best_tier(hw_info):
        """
        Map hardware -> model tiers based on VRAM and System RAM.
        """
        total_vram_gb = 0
        if "gpus" in hw_info and hw_info["gpus"]:
            # Sum up VRAM if multiple, though usually we care about the primary
            total_vram_gb = sum(g["vram_mb"] for g in hw_info["gpus"]) / 1024
        
        system_ram_gb = hw_info["total_ram_gb"]

        # Heuristics:
        if total_vram_gb >= 24 or (total_vram_gb == 0 and system_ram_gb >= 64):
            return ModelTier.LARGE
        elif total_vram_gb >= 12 or (total_vram_gb == 0 and system_ram_gb >= 32):
            return ModelTier.MEDIUM
        elif total_vram_gb >= 6 or (total_vram_gb == 0 and system_ram_gb >= 16):
            return ModelTier.SMALL
        else:
            return ModelTier.TINY

    @staticmethod
    def get_model_for_tier(tier: ModelTier):
        return TIER_MODELS.get(tier, "phi3:tiny")
