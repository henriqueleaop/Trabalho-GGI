from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from steam_dashboard.collector import load_monitor_targets, run_collector
from steam_dashboard.paths import DEFAULT_CCU_HISTORY, DEFAULT_MONITOR_CANDIDATES, ensure_directories


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Coleta snapshots de jogadores atuais da Steam.")
    parser.add_argument(
        "--source",
        default=str(DEFAULT_MONITOR_CANDIDATES),
        help="CSV com apps monitorados. Use o arquivo gerado na preparacao.",
    )
    parser.add_argument(
        "--history",
        default=str(DEFAULT_CCU_HISTORY),
        help="Arquivo CSV onde o historico sera salvo.",
    )
    parser.add_argument(
        "--mode",
        choices=["once", "demo", "academic"],
        default="once",
        help="Modo de coleta: unica, demonstracao ou academico.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Numero de iteracoes. Em academic e demo, o valor padrao do modo sobrescreve se nao for informado.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=None,
        help="Intervalo entre snapshots. Demo usa 300s e academic usa 3600s.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Quantidade maxima de apps monitorados.",
    )
    parser.add_argument(
        "--api-key-env",
        default="STEAM_API_KEY",
        help="Nome da variavel de ambiente com a Steam API key, se utilizada.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    ensure_directories()

    if args.mode == "demo":
        interval_seconds = args.interval_seconds or 300
        iterations = args.iterations if args.iterations != 1 else 6
    elif args.mode == "academic":
        interval_seconds = args.interval_seconds or 3600
        iterations = args.iterations if args.iterations != 1 else 24
    else:
        interval_seconds = args.interval_seconds or 0
        iterations = args.iterations

    targets = load_monitor_targets(Path(args.source), limit=args.limit)
    if not targets:
        raise SystemExit("Nenhum app monitorado encontrado. Rode o script de preparacao primeiro.")

    total_rows = run_collector(
        targets=targets,
        history_path=Path(args.history),
        interval_seconds=interval_seconds,
        iterations=iterations,
        api_key_env=args.api_key_env,
    )

    print(f"Snapshots gravados: {total_rows}")
    print(f"Historico atualizado em: {args.history}")


if __name__ == "__main__":
    main()
