from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas as pd

from steam_dashboard.paths import DEFAULT_PROCESSED_CSV, DEFAULT_PROCESSED_PARQUET, OUTPUT_PDF_DIR
from steam_dashboard.reporting import build_markdown_report, build_pdf_report, build_report_context


def load_games() -> pd.DataFrame:
    if DEFAULT_PROCESSED_PARQUET.exists():
        return pd.read_parquet(DEFAULT_PROCESSED_PARQUET)
    return pd.read_csv(DEFAULT_PROCESSED_CSV, parse_dates=["release_date"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera relatorio academico em Markdown e, opcionalmente, em PDF.")
    parser.add_argument("--output", default="output/steam_decision_report.md")
    parser.add_argument("--pdf-output", default=str(OUTPUT_PDF_DIR / "steamloja_academica.pdf"))
    parser.add_argument("--with-pdf", action="store_true")
    args = parser.parse_args()

    games_df = load_games()
    context = build_report_context(games_df)
    markdown = build_markdown_report(context)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(output_path)

    if args.with_pdf:
        pdf_bytes = build_pdf_report(context)
        pdf_path = Path(args.pdf_output)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.write_bytes(pdf_bytes)
        print(pdf_path)


if __name__ == "__main__":
    main()
