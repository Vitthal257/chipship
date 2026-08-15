"""ChipShip Configuration & Model Resolution Helper.

Manages ~/.hermes/config.yaml, detects local models (Ollama, vLLM, LM Studio),
resolves active providers/endpoints, and handles interactive model setup.
"""

import os
import sys
import yaml
import urllib.request
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).resolve()
CONFIG_FILE = HERMES_HOME / "config.yaml"
ENV_FILE = HERMES_HOME / ".env"


def ensure_hermes_home():
    HERMES_HOME.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """Load configuration from ~/.hermes/config.yaml."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        content = CONFIG_FILE.read_text()
        return yaml.safe_load(content) or {}
    except Exception as exc:
        logger.warning("Failed to load %s: %s", CONFIG_FILE, exc)
        return {}


def save_config(cfg: Dict[str, Any]) -> None:
    """Save configuration to ~/.hermes/config.yaml."""
    ensure_hermes_home()
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)


def check_local_ollama() -> Optional[Dict[str, Any]]:
    """Check if local Ollama server is running on localhost:11434."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                models = [m.get("name") for m in data.get("models", [])]
                return {
                    "running": True,
                    "endpoint": "http://localhost:11434/v1",
                    "models": models,
                    "provider": "ollama",
                }
    except Exception:
        pass
    return None


def check_local_vllm() -> Optional[Dict[str, Any]]:
    """Check if local vLLM / LM Studio server is running on localhost:8000 or localhost:1234."""
    for port in [8000, 1234]:
        try:
            url = f"http://localhost:{port}/v1/models"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    models = [m.get("id") for m in data.get("data", [])]
                    return {
                        "running": True,
                        "endpoint": f"http://localhost:{port}/v1",
                        "models": models,
                        "provider": "vllm" if port == 8000 else "lmstudio",
                    }
        except Exception:
            pass
    return None


def get_active_model_info() -> Dict[str, Any]:
    """Resolve active model, provider, base_url, and API key status."""
    cfg = load_config()
    
    # 1. Environment Overrides
    env_model = os.environ.get("HERMES_MODEL") or os.environ.get("OPENAI_MODEL")
    env_provider = os.environ.get("HERMES_PROVIDER")
    env_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("HERMES_BASE_URL")
    
    model_cfg = cfg.get("model", {})
    
    model_name = env_model or model_cfg.get("default") or "hermes-3-llama-3.1-8b"
    provider = env_provider or model_cfg.get("provider") or "auto"
    base_url = env_url or model_cfg.get("base_url") or ""

    # Detect API Keys
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    # Check local servers if unconfigured or requested
    local_ollama = check_local_ollama()
    local_vllm = check_local_vllm()

    is_local = False
    status_msg = "Configured"

    if "localhost" in base_url or "127.0.0.1" in base_url or provider in ("ollama", "vllm", "lmstudio"):
        is_local = True
        status_msg = "Local Server Active"
    elif openrouter_key or provider == "openrouter":
        provider = "openrouter"
        if not base_url:
            base_url = "https://openrouter.ai/api/v1"
        status_msg = "OpenRouter Cloud API Key Active" if openrouter_key else "OpenRouter Configured"
    elif anthropic_key or provider == "anthropic":
        provider = "anthropic"
        status_msg = "Anthropic API Key Active" if anthropic_key else "Anthropic Configured"
    elif openai_key or provider == "openai":
        provider = "openai"
        status_msg = "OpenAI API Key Active" if openai_key else "OpenAI Configured"
    elif local_ollama:
        is_local = True
        provider = "ollama"
        base_url = local_ollama["endpoint"]
        if local_ollama["models"]:
            model_name = local_ollama["models"][0]
        status_msg = f"Auto-detected local Ollama ({len(local_ollama['models'])} models found)"
    elif local_vllm:
        is_local = True
        provider = local_vllm["provider"]
        base_url = local_vllm["endpoint"]
        if local_vllm["models"]:
            model_name = local_vllm["models"][0]
        status_msg = f"Auto-detected local {provider.upper()} server"
    else:
        status_msg = "Unconfigured / Default Fallback"

    return {
        "model_name": model_name,
        "provider": provider,
        "base_url": base_url or "https://openrouter.ai/api/v1",
        "is_local": is_local,
        "status_msg": status_msg,
        "local_ollama": local_ollama,
        "local_vllm": local_vllm,
    }


def configure_model_interactive(console) -> Dict[str, Any]:
    """Interactive wizard to configure local or cloud AI models."""
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.table import Table

    info = get_active_model_info()

    console.print("\n[bold gold1]⚡ CHIPSHIP MODEL SETUP & PROVIDER CONFIGURATION WIZARD[/bold gold1]\n")
    
    table = Table(title="Currently Active Configuration", border_style="cyan")
    table.add_column("Property", style="bold white")
    table.add_column("Value", style="cyan")
    table.add_row("Model Name", info["model_name"])
    table.add_row("Provider", info["provider"])
    table.add_row("Endpoint URL", info["base_url"])
    table.add_row("Status", info["status_msg"])
    console.print(table)

    console.print("\n[bold cyan]Select an AI Engine Provider Option:[/bold cyan]")
    console.print("  [bold yellow][1][/bold yellow] Local Ollama Server (http://localhost:11434/v1)")
    console.print("  [bold yellow][2][/bold yellow] Local vLLM / LM Studio Server (http://localhost:8000/v1)")
    console.print("  [bold yellow][3][/bold yellow] OpenRouter Cloud API (https://openrouter.ai/api/v1)")
    console.print("  [bold yellow][4][/bold yellow] Anthropic Claude API")
    console.print("  [bold yellow][5][/bold yellow] OpenAI API (https://api.openai.com/v1)")
    console.print("  [bold yellow][6][/bold yellow] Custom Local or Remote OpenAI-Compatible Endpoint")
    console.print("  [bold yellow][0][/bold yellow] Cancel / Keep Current Configuration\n")

    choice = Prompt.ask("Enter option number", choices=["0", "1", "2", "3", "4", "5", "6"], default="0")

    if choice == "0":
        console.print("[dim]Configuration unchanged.[/dim]")
        return info

    cfg = load_config()
    if "model" not in cfg:
        cfg["model"] = {}

    if choice == "1":
        ollama = info["local_ollama"] or check_local_ollama()
        default_m = ollama["models"][0] if (ollama and ollama.get("models")) else "llama3.1"
        model_input = Prompt.ask("Enter Ollama model name", default=default_m)
        cfg["model"]["default"] = model_input
        cfg["model"]["provider"] = "ollama"
        cfg["model"]["base_url"] = "http://localhost:11434/v1"
        console.print(f"[bold green]✔ Configured Local Ollama with model '{model_input}'![/bold green]")

    elif choice == "2":
        vllm = info["local_vllm"] or check_local_vllm()
        default_m = vllm["models"][0] if (vllm and vllm.get("models")) else "Qwen2.5-Coder-32B-Instruct"
        endpoint_input = Prompt.ask("Enter server endpoint URL", default="http://localhost:8000/v1")
        model_input = Prompt.ask("Enter model name", default=default_m)
        cfg["model"]["default"] = model_input
        cfg["model"]["provider"] = "vllm"
        cfg["model"]["base_url"] = endpoint_input
        console.print(f"[bold green]✔ Configured Local vLLM/LM Studio server '{endpoint_input}' with model '{model_input}'![/bold green]")

    elif choice == "3":
        model_input = Prompt.ask("Enter OpenRouter model name", default="hermes-3-llama-3.1-8b")
        api_key = Prompt.ask("Enter OpenRouter API Key (or press Enter to skip if set in env)", password=True, default="")
        cfg["model"]["default"] = model_input
        cfg["model"]["provider"] = "openrouter"
        cfg["model"]["base_url"] = "https://openrouter.ai/api/v1"
        if api_key:
            os.environ["OPENROUTER_API_KEY"] = api_key
            env_content = f"OPENROUTER_API_KEY={api_key}\n"
            ENV_FILE.write_text(env_content)
        console.print(f"[bold green]✔ Configured OpenRouter with model '{model_input}'![/bold green]")

    elif choice == "4":
        model_input = Prompt.ask("Enter Anthropic model name", default="claude-3-5-sonnet-20241022")
        api_key = Prompt.ask("Enter Anthropic API Key (or press Enter to skip if set in env)", password=True, default="")
        cfg["model"]["default"] = model_input
        cfg["model"]["provider"] = "anthropic"
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
            ENV_FILE.write_text(f"ANTHROPIC_API_KEY={api_key}\n")
        console.print(f"[bold green]✔ Configured Anthropic with model '{model_input}'![/bold green]")

    elif choice == "5":
        model_input = Prompt.ask("Enter OpenAI model name", default="gpt-4o")
        api_key = Prompt.ask("Enter OpenAI API Key (or press Enter to skip if set in env)", password=True, default="")
        cfg["model"]["default"] = model_input
        cfg["model"]["provider"] = "openai"
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            ENV_FILE.write_text(f"OPENAI_API_KEY={api_key}\n")
        console.print(f"[bold green]✔ Configured OpenAI with model '{model_input}'![/bold green]")

    elif choice == "6":
        endpoint_input = Prompt.ask("Enter custom base_url", default="http://localhost:8000/v1")
        model_input = Prompt.ask("Enter model name", default="custom-model")
        cfg["model"]["default"] = model_input
        cfg["model"]["provider"] = "custom"
        cfg["model"]["base_url"] = endpoint_input
        console.print(f"[bold green]✔ Configured Custom Endpoint '{endpoint_input}' with model '{model_input}'![/bold green]")

    save_config(cfg)
    return get_active_model_info()
