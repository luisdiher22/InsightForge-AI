import pandas as pd
from pandas.errors import EmptyDataError, ParserError


def load_dataframe(file, filename=None):
    name = filename or getattr(file, "name", "")

    if name.endswith(".xlsx"):
        file.seek(0)
        try:
            dataframe = pd.read_excel(file)
        except Exception as exc:
            raise ValueError("Este dataset necesita revisión") from exc

        if dataframe.empty:
            raise ValueError("Este dataset necesita revisión")

        return dataframe

    file.seek(0)

    try:
        dataframe = pd.read_csv(file, encoding="utf-8")
    except UnicodeDecodeError:
        file.seek(0)
        dataframe = pd.read_csv(file, encoding="latin1")
    except (EmptyDataError, ParserError, ValueError, OSError) as exc:
        raise ValueError("Este dataset necesita revisión") from exc

    if dataframe.empty:
        raise ValueError("Este dataset necesita revisión")

    return dataframe