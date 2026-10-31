# 🚀 ComfyUI Automation Engine

A Python-based automation pipeline for programmatically controlling ComfyUI via its API. Designed for batch image generation, e-commerce product photography scaling, and AI workflow integration.

## 🌟 Features
- **API-First Architecture:** Bypasses the UI to interact directly with the ComfyUI backend via WebSockets and HTTP.
- **Batch Processing:** Automatically iterates through lists of prompts (from CSV or arrays) to generate hundreds of images unattended.
- **Dynamic Workflow Injection:** Modifies workflow parameters (prompts, seeds, CFG scales) on the fly without manual UI interaction.
- **Secure Configuration:** Uses `.env` for server address management.

## 🛠️ Tech Stack
- Python 3.10+
- WebSockets (`websocket-client`)
- ComfyUI API

## 🚀 Usage
1. Ensure ComfyUI is running locally (`http://127.0.0.1:8188`).
2. Export your workflow from ComfyUI using "Save (API Format)" and name it `workflow_api.json`.
3. Update the `PROMPTS` list in `comfyui_automation.py`.
4. Run: `python comfyui_automation.py`

## 💼 Use Cases
- Automated generation of marketing assets from product CSVs.
- Headless AI image generation servers wrapped in FastAPI.
- Custom node development and pipeline testing.