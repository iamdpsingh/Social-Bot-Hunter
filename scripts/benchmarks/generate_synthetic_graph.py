#!/usr/bin/env python3
"""Benchmark script: generate_synthetic_graph."""

from __future__ import annotations

import argparse
import time


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI generator for synthetic graph topologies")
    parser.add_argument("--iterations", type=int, default=100, help="Number of benchmark iterations")
    args = parser.parse_args()

    print(f"Running generate_synthetic_graph benchmark for {args.iterations} iterations...")
    t0 = time.perf_counter()
    # Simulated execution workload
    total = sum(i * i for i in range(args.iterations * 1000))
    elapsed = time.perf_counter() - t0

    print(f"Completed in {elapsed:.4f}s (checksum={total})")


if __name__ == "__main__":
    main()
