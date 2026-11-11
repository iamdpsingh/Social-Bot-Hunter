"""CLI commands for training and evaluating bot detection ML models."""

from __future__ import annotations

import argparse
import sys

from sbh.detection.ml.serialization import ModelRegistry, format_model_card_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Social Bot Hunter ML evaluation CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("eval", help="Evaluate currently registered production model")
    subparsers.add_parser("info", help="Display metadata of registered model artifact")

    args = parser.parse_args(argv)
    registry = ModelRegistry.get_instance()
    _, _, meta = registry.get_default_model()

    if args.command in ("eval", "info", None):
        print(format_model_card_markdown(meta))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
