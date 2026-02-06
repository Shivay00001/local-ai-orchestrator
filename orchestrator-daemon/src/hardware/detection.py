import platform
import psutil
from dataclasses import dataclass
from typing import List

try:
    import pynvml
    HAS_PYNVML = True
except ImportError:
    HAS_PYNVML = False

@dataclass
class GPUInfo:
    name: str
    total_memory_mb: int
    free_memory_mb: int
    driver_version: str
    cuda_version: str

@dataclass
class HardwareProfile:
    os: str
    cpu_cores_physical: int
    cpu_cores_logical: int
    ram_total_gb: float
    ram_available_gb: float
    gpus: List[GPUInfo]

def _get_cpu_info():
    return {
        "physical": psutil.cpu_count(logical=False) or 1,
        "logical": psutil.cpu_count(logical=True) or 1
    }

def _get_ram_info():
    vm = psutil.virtual_memory()
    return {
        "total_gb": round(vm.total / (1024**3), 2),
        "available_gb": round(vm.available / (1024**3), 2)
    }

def _get_nvidia_gpus() -> List[GPUInfo]:
    gpus = []
    if not HAS_PYNVML:
        return []
    
    try:
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        try:
            driver_ver = pynvml.nvmlSystemGetDriverVersion().decode("utf-8")
        except:
             driver_ver = "Unknown"
             
        try:
            cuda_ver_raw = pynvml.nvmlSystemGetCudaDriverVersion()
            cuda_ver = f"{cuda_ver_raw // 1000}.{(cuda_ver_raw % 1000) // 10}"
        except:
             cuda_ver = "Unknown"

        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle).decode("utf-8")
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            gpus.append(GPUInfo(
                name=name,
                total_memory_mb=int(mem_info.total / (1024**2)),
                free_memory_mb=int(mem_info.free / (1024**2)),
                driver_version=driver_ver,
                cuda_version=cuda_ver
            ))
        pynvml.nvmlShutdown()
    except Exception as e:
        print(f"Error detecting NVIDIA GPUs: {e}")
    
    return gpus

def detect_hardware() -> HardwareProfile:
    cpu = _get_cpu_info()
    ram = _get_ram_info()
    gpus = _get_nvidia_gpus()
    
    return HardwareProfile(
        os=platform.system() + " " + platform.release(),
        cpu_cores_physical=cpu["physical"],
        cpu_cores_logical=cpu["logical"],
        ram_total_gb=ram["total_gb"],
        ram_available_gb=ram["available_gb"],
        gpus=gpus
    )
