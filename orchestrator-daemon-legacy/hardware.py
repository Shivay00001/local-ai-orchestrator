import psutil
import platform
import logging
import time

logger = logging.getLogger(__name__)

class HardwareDetector:
    @staticmethod
    def get_system_info():
        info = {
            "os": platform.system(),
            "os_release": platform.release(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True),
            "total_ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "available_ram_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        }
        
        # GPU Detection (Windows/WMI focus as per user OS)
        if platform.system() == "Windows":
            info["gpus"] = HardwareDetector._get_windows_gpu_info()
        else:
            info["gpus"] = [] # Placeholder for other OS
            
        return info

    @staticmethod
    def _get_windows_gpu_info():
        gpus = []
        try:
            import wmi
            w = wmi.WMI()
            for controller in w.Win32_VideoController():
                # Note: Win32_VideoController AdapterRAM is often inaccurate for modern GPUs (32-bit limit)
                # We will try to get more accurate info via other means if needed, 
                # but for now, we'll use this as a baseline.
                gpu_info = {
                    "name": controller.Name,
                    "driver_version": controller.DriverVersion,
                    "vram_mb": controller.AdapterRAM / (1024**2) if controller.AdapterRAM else 0
                }
                gpus.append(gpu_info)
        except Exception as e:
            logger.error(f"Failed to detect GPU via WMI: {e}")
            
        return gpus

    @staticmethod
    def safe_profiling_pass():
        """
        Measured overhead/pressure test.
        In Phase 1, we just log current state, but future implementation 
        will involve loading a tiny model via Ollama and measuring delta.
        """
        logger.info("Starting safe profiling pass...")
        initial_mem = psutil.virtual_memory().percent
        time.sleep(1) # Simulated measurement
        final_mem = psutil.virtual_memory().percent
        logger.info(f"System memory delta during profile: {final_mem - initial_mem}%")
        return True
