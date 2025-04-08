---
# 🖥️ Rendering Worker

This repository is part of the **RenderBros** distributed rendering platform. The `rendering-worker` is a node application responsible for performing rendering tasks assigned by a central dispatcher in a decentralized rendering network.

## 🚀 Overview

The `rendering-worker` is designed to:
- Fetch rendering jobs from a central queue or job manager.
- Execute rendering using Blender's headless mode (and with other supported engines ini future).
- Send back completed frames or tiles.
- Handle task validation, retries, and resource cleanup.

## 🔧 Features

- ⚙️ Automated job processing from remote dispatcher
- 🧪 Built-in verification of rendered output
- ♻️ Supports retries and error handling
- 📦 Lightweight and containerizable (Docker support)
- 🔐 Secure communication with central server (planned)

## 🏗️ Project Structure

```
rendering-worker/
├── .env.example
├── .gitignore
├── Dockerfile
├── main.py
├── requirements.txt
└── README.md
```

## 🔌 Requirements

- Node.js 18+
- Blender (CLI accessible in path)
- Docker (optional, for containerized deployment)

## ⚙️ Setup & Usage

```bash
git clone https://github.com/2BrokeGuys/rendering-worker.git
cd rendering-worker
cp .env.example .env   # configure environment variables
npm install
npm start
```

## 🐳 Docker

```bash
docker build -t rendering-worker .
docker run --env-file .env rendering-worker
```

## 📡 Communication

The worker polls or subscribes to job updates from the central dispatcher via HTTP/WebSocket. Completed jobs are returned with verification hashes to maintain integrity.

## 🛡️ Verification Model (Planned)

- Randomized tile/frame sampling for redundancy.
- Hash-based comparison of expected vs actual output.
- Penalization of incorrect renderers.

## 🛠️ Future Work

- Integration with decentralized storage (e.g., IPFS)
- GPU load detection & dynamic throttling
- Blockchain-based reward model (RenderBros credits)

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue to discuss what you'd like to change.

## 📄 License

MIT License

---
