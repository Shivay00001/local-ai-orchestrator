from enum import Enum
from dataclasses import dataclass
from ..hardware.detection import HardwareProfile

class ModelTier(str, Enum):
    TINY = "Tiny (1-3B)"
    SMALL = "Small (7B)"
    MEDIUM = "Medium (13B)"
    LARGE = "Large (32B)"

@dataclass
class ModelRecommendation:
    tier: ModelTier
    reasoning: str
    max_memory_usage_gb: float

def select_model_tier(profile: HardwareProfile) -> ModelRecommendation:
    # Heuristics (Approximate VRAM needs for 4-bit quantization):
    # Tiny (3B): ~2.5 GB
    # Small (7B): ~5.5 GB
    # Medium (13B): ~9.5 GB
    # Large (32B): ~20.0 GB
    
    total_vram = 0.0
    # For now, simplistic approach: use total VRAM if consistent, else max of single card.
    # We'll stick to treating VRAM as a pool but be conservative.
    if profile.gpus:
        total_vram = sum(gpu.free_memory_mb for gpu in profile.gpus) / 1024.0
    
    # Reserve 4GB for OS/System if using RAM
    usable_ram = max(0.0, profile.ram_available_gb - 4.0)
    
    # Prefer GPU
    if total_vram > 2.0:
        available_memory = total_vram
        source = "VRAM"
    else:
        available_memory = usable_ram
        source = "System RAM (Slow)"
    
    if available_memory >= 22.0:
        return ModelRecommendation(ModelTier.LARGE, f"Available {source}: {available_memory:.1f}GB", 20.0)
    elif available_memory >= 10.0:
        return ModelRecommendation(ModelTier.MEDIUM, f"Available {source}: {available_memory:.1f}GB", 9.5)
    elif available_memory >= 6.0:
        return ModelRecommendation(ModelTier.SMALL, f"Available {source}: {available_memory:.1f}GB", 5.5)
    elif available_memory >= 3.0:
        return ModelRecommendation(ModelTier.TINY, f"Available {source}: {available_memory:.1f}GB", 2.5)
    else:
        # Fallback
        return ModelRecommendation(ModelTier.TINY, f"Critically low memory ({available_memory:.1f}GB). Restricted to Tiny.", 2.0)
