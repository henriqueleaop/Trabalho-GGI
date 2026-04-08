from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from steam_dashboard.paths import (
    DEFAULT_MONITOR_CANDIDATES,
    DEFAULT_PROCESSED_CSV,
    DEFAULT_PROCESSED_PARQUET,
    ensure_directories,
)
from steam_dashboard.transform import (
    prepare_games_dataframe,
    sample_monitor_candidates,
    write_processed_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepara a base analitica de jogos da Steam.")
    parser.add_argument("--input", required=True, help="Caminho do CSV bruto de jogos.")
    parser.add_argument(
        "--output-csv",
        default=str(DEFAULT_PROCESSED_CSV),
        help="Caminho do CSV processado.",
    )
    parser.add_argument(
        "--output-parquet",
        default=str(DEFAULT_PROCESSED_PARQUET),
        help="Caminho do parquet processado.",
    )
    parser.add_argument(
        "--monitor-output",
        default=str(DEFAULT_MONITOR_CANDIDATES),
        help="Caminho do CSV com jogos monitorados pelo coletor.",
    )
    parser.add_argument(
        "--monitor-limit",
        type=int,
        default=20,
        help="Quantidade de apps monitorados na coleta operacional.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    ensure_directories()

    input_path = Path(args.input)
    output_csv = Path(args.output_csv)
    output_parquet = Path(args.output_parquet)
    monitor_output = Path(args.monitor_output)

    df = prepare_games_dataframe(input_path)
    write_processed_outputs(df, output_csv=output_csv, output_parquet=output_parquet)

    monitor_df = sample_monitor_candidates(df, limit=args.monitor_limit)
    monitor_output.parent.mkdir(parents=True, exist_ok=True)
    monitor_df.to_csv(monitor_output, index=False)

    print(f"Jogos validos processados: {len(df):,}")
    print(f"CSV processado: {output_csv}")
    print(f"Parquet processado: {output_parquet}")
    print(f"Candidatos monitorados: {monitor_output} ({len(monitor_df)} apps)")


if __name__ == "__main__":
    main()
