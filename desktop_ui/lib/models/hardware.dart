class HardwareInfo {
  final String os;
  final int cpuCoresPhysical;
  final double ramTotalGb;
  final double ramAvailableGb;

  HardwareInfo({
    required this.os,
    required this.cpuCoresPhysical,
    required this.ramTotalGb,
    required this.ramAvailableGb,
  });

  factory HardwareInfo.fromJson(Map<String, dynamic> json) {
    return HardwareInfo(
      os: json['os'] ?? 'Unknown',
      cpuCoresPhysical: json['cpu_cores_physical'] ?? 0,
      ramTotalGb: (json['ram_total_gb'] ?? 0).toDouble(),
      ramAvailableGb: (json['ram_available_gb'] ?? 0).toDouble(),
    );
  }
}
