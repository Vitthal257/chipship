#!/usr/bin/env python3
"""
ChipShip CLI - Custom EDA Agent Interface
A tailored entry point for the Hermes Agent focused strictly on EDA and hardware verification loops.
"""

import os
import sys
import argparse
import logging
from typing import Optional

# Setup basic logging to see errors or status in the CLI if needed
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("chipship_cli")

try:
    from run_agent import AIAgent
except ImportError:
    print("Error: run_agent could not be imported. Please ensure you are running this from the correct environment.", file=sys.stderr)
    sys.exit(1)

from eda_agent.moderator import EdaVerificationModerator

def main():
    parser = argparse.ArgumentParser(
        description="ChipShip EDA Custom CLI",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Modes
    parser.add_argument("--ai", action="store_true", help="Run the autonomous AI moderation loop for verification")
    parser.add_argument("--query", "-q", type=str, help="Single query to execute (then exit)")
    
    # Verification Parameters (used with --ai)
    parser.add_argument("--files", nargs="*", help="RTL files to verify")
    parser.add_argument("--top_module", type=str, help="Top module name for simulation")
    parser.add_argument("--tb_type", type=str, default="cpp", choices=["cpp", "cocotb"], help="Testbench type")
    parser.add_argument("--max_iterations", type=int, default=5, help="Max iterations for the AI loop")
    
    args = parser.parse_args()
    
    # Suppress verbose logs from the agent core unless we explicitly want them
    os.environ["HERMES_QUIET"] = "1"
    
    # Initialize the Hermes agent with our specific toolsets and platform hint
    # We enable `eda` (hardware verification), `terminal` (executing scripts/compilation), 
    # and `file` (reading/writing RTL).
    logger.info("Initializing ChipShip EDA Agent...")
    
    try:
        from cli import load_cli_config
        from hermes_cli.config import load_env
        from hermes_cli.runtime_provider import resolve_runtime_provider
        from hermes_cli.fallback_config import get_fallback_chain

        load_env()
        cli_config = load_cli_config()
        model_config = cli_config.get("model", {})
        cfg_provider = model_config.get("provider")
        cfg_model = model_config.get("default") or model_config.get("name") or ""
        
        runtime = resolve_runtime_provider(
            requested=cfg_provider,
            target_model=cfg_model,
        )
        provider = runtime.get("provider")
        api_key = runtime.get("api_key")
        base_url = runtime.get("base_url")
        credential_pool = runtime.get("credential_pool")
        
        fallback_model = get_fallback_chain(cli_config)
    except Exception as e:
        logger.warning(f"Could not load Hermes CLI config: {e}")
        provider = None
        cfg_model = ""
        base_url = None
        api_key = None
        fallback_model = None
        credential_pool = None

    logger.info(f"Initializing AIAgent with provider={provider}, model={cfg_model}, base_url={base_url}")

    agent = AIAgent(
        model=cfg_model,
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        fallback_model=fallback_model,
        credential_pool=credential_pool,
        enabled_toolsets=["eda", "terminal", "file"],
        platform="chipship-cli",
        quiet_mode=True,
        skip_context_files=True
    )
    
    if args.ai:
        if not args.files or not args.top_module:
            print("Error: --ai mode requires both --files and --top_module arguments.", file=sys.stderr)
            sys.exit(1)
            
        print(f"Starting Autonomous EDA Moderation Loop for top module: {args.top_module}")
        print(f"Target files: {args.files}")
        
        moderator = EdaVerificationModerator(work_dir=".")
        result = moderator.run_ai_moderated_loop(
            agent=agent,
            files=args.files,
            top_module=args.top_module,
            tb_type=args.tb_type,
            max_iterations=args.max_iterations,
        )
        
        print("\n=== AI Moderation Loop Completed ===")
        print(f"Converged (0 Errors): {result.get('converged')}")
        print(f"Total Iterations: {result.get('total_iterations')}")
        print(f"Total Duration: {result.get('total_duration_s')}s")
        print(f"Final Status: {result.get('final_status')}")
        
        sys.exit(0 if result.get("converged") else 1)

    elif args.query:
        print(f"ChipShip Query: {args.query}")
        response = agent.chat(args.query)
        print("\nResponse:\n", response)
        sys.exit(0)

    else:
        # Interactive Mode
        print("\nWelcome to the ChipShip EDA Assistant!")
        print("I am loaded with specialized hardware verification and simulation tools.")
        print("Type 'quit' or 'exit' to leave.\n")
        
        while True:
            try:
                query = input("ChipShip EDA> ")
                if query.strip().lower() in ["quit", "exit"]:
                    break
                if not query.strip():
                    continue
                    
                response = agent.chat(query)
                print(f"\n{response}\n")
                
            except (KeyboardInterrupt, EOFError):
                print("\nExiting ChipShip CLI...")
                break

if __name__ == "__main__":
    main()
