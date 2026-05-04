import openpyxl

def read_config_file(config_path: str) -> list[dict]:
    """
    Reads config xlsx and returns list of enabled rows as dicts.
    Returns empty list if path is None or file unreadable.
    """
    if not config_path:
        return []

    try:
        wb = openpyxl.load_workbook(config_path, read_only=True)
        ws = wb.active

        headers = None
        rows = []

        for row in ws.iter_rows(values_only=True):
            if headers is None:
                headers = [str(h).strip() if h else "" for h in row]
                continue
            if all(cell is None for cell in row):
                continue
            row_dict = dict(zip(headers, row))
            rows.append(row_dict)

        return rows

    except Exception as e:
        print(f"Warning: Could not read config file {config_path}: {e}")
        return []