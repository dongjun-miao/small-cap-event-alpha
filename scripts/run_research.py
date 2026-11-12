"""Run the canonical small-cap event-alpha research pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_alpha.pipeline import run_pipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="Directory containing the five *_research_v1.csv files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "output" / "tables",
    )
    parser.add_argument(
        "--reuse-event-samples",
        action="store_true",
        help="Reuse existing compressed event samples in the output directory.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_pipeline(
        arguments.data_dir,
        arguments.output_dir,
        reuse_event_samples=arguments.reuse_event_samples,
    )
