from pathlib import Path

import pandas as pd


def write_parquet(rows: list[dict[str, str]], path: Path) -> None:
    df = pd.DataFrame(rows, dtype="string")
    df = df[sorted(df.columns)]
    df = df.sort_values(by=list(df.columns)).reset_index(drop=True)

    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)