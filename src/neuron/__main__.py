"""
CLI Entry Point for PROJECT: NEURON
Enables launching the Interactive Chat UI via `python -m neuron`.
"""

import argparse
from neuron.ui.server import run


def main():
    parser = argparse.ArgumentParser(description="PROJECT: NEURON — Edge Micro-AI Ecosystem")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    args = parser.parse_args()

    run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
