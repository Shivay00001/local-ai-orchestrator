class AgentResponse {
  final String agentName;
  final String content;
  final Map<String, dynamic>? metadata;

  AgentResponse({
    required this.agentName,
    required this.content,
    this.metadata,
  });

  factory AgentResponse.fromJson(Map<String, dynamic> json) {
    return AgentResponse(
      agentName: json['agent'] ?? 'System',
      content: json['content'] ?? '',
      metadata: json['metadata'],
    );
  }
}
