import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../repositories/daemon_repository.dart';
import '../models/hardware.dart';
import '../models/agent.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  final DaemonRepository _repository = DaemonRepository();
  final TextEditingController _chatController = TextEditingController();
  final List<AgentResponse> _messages = [];
  bool _isLoading = false;
  HardwareInfo? _hardwareInfo;

  @override
  void initState() {
    super.initState();
    _fetchHardware();
  }

  Future<void> _fetchHardware() async {
    try {
      final info = await _repository.getHardware();
      setState(() => _hardwareInfo = info);
    } catch (e) {
      debugPrint('Error: $e');
    }
  }

  Future<void> _sendMessage() async {
    final text = _chatController.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add(AgentResponse(agentName: 'User', content: text));
      _isLoading = true;
      _chatController.clear();
    });

    try {
      final response = await _repository.sendAgentTask(text);
      setState(() => _messages.add(response));
    } catch (e) {
      setState(() => _messages.add(AgentResponse(agentName: 'Error', content: e.toString())));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          // Left Panel: Explorer (Placeholder)
          Container(
            width: 250,
            color: Colors.grey[900],
            child: Column(
              children: [
                const SizedBox(height: 20),
                const Text('Project Explorer', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                const Divider(color: Colors.grey),
                Expanded(
                  child: Center(
                    child: Text('File Tree\n(Coming Phase 5)', style: TextStyle(color: Colors.grey[600]), textAlign: TextAlign.center),
                  ),
                ),
                if (_hardwareInfo != null)
                  _buildHardwareStatus(_hardwareInfo!),
              ],
            ),
          ),
          // Right Panel: Chat
          Expanded(
            child: Column(
              children: [
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.all(20),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      final msg = _messages[index];
                      final isUser = msg.agentName == 'User';
                      return Align(
                        alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                        child: Container(
                          margin: const EdgeInsets.symmetric(vertical: 8),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: isUser ? Colors.blue[800] : Colors.grey[800],
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(msg.agentName, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.white70)),
                              const SizedBox(height: 4),
                              SelectableText(msg.content, style: const TextStyle(color: Colors.white)),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
                if (_isLoading) const LinearProgressIndicator(),
                Padding(
                  padding: const EdgeInsets.all(20),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _chatController,
                          decoration: const InputDecoration(
                            hintText: 'Ask the agent (e.g. "Explain Code", "Refactor")',
                            border: OutlineInputBorder(),
                            fillColor: Colors.black12,
                            filled: true,
                          ),
                          onSubmitted: (_) => _sendMessage(),
                        ),
                      ),
                      const SizedBox(width: 10),
                      IconButton(
                        icon: const Icon(Icons.send),
                        onPressed: _sendMessage,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHardwareStatus(HardwareInfo info) {
    return Container(
      padding: const EdgeInsets.all(10),
      color: Colors.black26,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('GPU: Unknown', style: const TextStyle(color: Colors.greenAccent, fontSize: 12)),
          Text('RAM: ${info.ramAvailableGb}GB / ${info.ramTotalGb}GB', style: const TextStyle(color: Colors.white70, fontSize: 12)),
          Text('CPU: ${info.cpuCoresPhysical} Cores', style: const TextStyle(color: Colors.white70, fontSize: 12)),
        ],
      ),
    );
  }
}
