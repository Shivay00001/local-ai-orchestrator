import 'package:dio/dio.dart';
import '../models/hardware.dart';
import '../models/agent.dart';

class DaemonRepository {
  final Dio _dio = Dio(BaseOptions(baseUrl: 'http://127.0.0.1:8000'));

  Future<HardwareInfo> getHardware() async {
    try {
      final response = await _dio.get('/system/hardware');
      return HardwareInfo.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to fetch hardware info: $e');
    }
  }

  Future<AgentResponse> sendAgentTask(String task) async {
    try {
      final response = await _dio.post('/agent/task', data: {'task': task});
      // Daemon returns: {"agent": "...", "content": "...", "metadata": ...}
      // Or AgentResponse wrapper as defined in API
      return AgentResponse.fromJson(response.data);
    } catch (e) {
      return AgentResponse(agentName: 'Error', content: 'Connection failed: $e');
    }
  }
  
  Future<bool> checkHealth() async {
    try {
      final response = await _dio.get('/health');
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
