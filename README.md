# Local Ai Orchestrator

Flutter desktop UI for local AI agent orchestration and hardware management

![Language](https://img.shields.io/badge/Language-Python-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Overview

Welcome to the **Local Ai Orchestrator** repository. This project is built to deliver a robust and scalable solution tailored to modern development standards.

## ✨ Features

- **High Performance:** Optimized for speed and efficiency.
- **Scalable Architecture:** Designed to grow with your needs.
- **Clean Codebase:** Follows best practices and industry standards.
- **Secure by Default:** Engineered with security in mind.

## 🛠️ Prerequisites

Ensure you have the following installed in your environment before proceeding:
- Appropriate runtime/compiler for `Python`
- Standard development tools

## 📦 Installation

Follow standard installation steps for `Python` to set up the project locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/Shivay00001/local-ai-orchestrator.git
   ```
2. Navigate to the project directory:
   ```bash
   cd local-ai-orchestrator
   ```
3. Install dependencies according to the standard `Python` ecosystem.

## 💻 Usage

The orchestrator daemon is a FastAPI service that binds **127.0.0.1 only** (by design — local, private).

### Dependencies

```bash
cd orchestrator-daemon
pip install -r requirements.txt                 # core API (light)
pip install -r requirements-embeddings.txt      # OPTIONAL: heavy embedding/RAG deps (chromadb, sentence-transformers, torch)
```

**Embedding endpoints need torch.** The `/project/index`, `/project/query`, and `/agent/task`
endpoints use ChromaDB + sentence-transformers (torch) for RAG. These are loaded *lazily*:
the API boots and serves all other endpoints (`/health`, `/ollama/*`, `/system/hardware`,
`/models/recommended`, …) without them. If you call an embedding endpoint without the optional
deps installed, it returns **HTTP 503** with an install hint instead of crashing at startup.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 📝 License

This project is licensed under standard terms.
