import re
import pandas as pd
import os

def read_categories(file_path):
    """
    Read data/categories.csv (two columns: Description, Category) and
    return list of (pattern_lower, category) tuples.
    """
    file_path = str(file_path)
    # resolve relative to project root (one level above src)
    if not os.path.isabs(file_path):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        file_path = os.path.join(project_root, file_path)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"categories file not found at: {file_path}")

    df = pd.read_csv(file_path, dtype=str).fillna('')

    cols_lower = [c.strip().lower() for c in df.columns]

    # find Description and Category columns (case-insensitive), else fallback to first/second
    desc_col = df.columns[cols_lower.index('description')] if 'description' in cols_lower else (df.columns[0] if df.shape[1] >= 1 else None)
    cat_col = df.columns[cols_lower.index('category')] if 'category' in cols_lower else (df.columns[1] if df.shape[1] >= 2 else None)

    patterns = []
    for _, row in df.iterrows():
        pattern = str(row.get(desc_col, '')).strip().lower() if desc_col is not None else ''
        category = str(row.get(cat_col, '')).strip() if cat_col is not None else ''
        if pattern:
            patterns.append((pattern, category))
    return patterns

def read_exports(file_path):
    """
    Return DataFrame with columns: Date, AMT, DESCR, ACCT (all strings).
    Supports CSV and Excel (.xls/.xlsx). Handles files with leading metadata rows
    (e.g. "Account Name: ...") by locating the row that contains "Date" (case-insensitive)
    and using it as header. If no header row is found and the first column looks like dates,
    treat file as headerless with positions: col0=date, col1=amount, col3=description (if present).
    """
    file_path = str(file_path)
    basename = os.path.splitext(os.path.basename(file_path))[0]

    acct_map = {
        'chase2528': 'Chase Southwest',
        'chase1999': 'Chase Sapphire',
        'marketrate': 'Joint Savings',
        'account transactions': 'High Yield Savings',
    }

    def normalize(s):
        return re.sub(r'[^a-z]', '', str(s).lower())

    def map_account(name):
        n = normalize(name)
        for k, v in acct_map.items():
            if normalize(k) in n:
                return v
        return name

    ext = file_path.lower().rsplit('.', 1)[-1] if '.' in file_path else ''
    date_like_re = re.compile(r'^\s*\d{1,2}/\d{1,2}/\d{2,4}\s*$')
    header_word_re = re.compile(r'\bdate\b', re.I)

    if ext in ('xls', 'xlsx'):
        # prefer engine selection to avoid ambiguous pandas errors
        try:
            if ext == 'xls':
                # .xls requires xlrd
                raw = pd.read_excel(file_path, header=None, dtype=str, engine='xlrd').fillna('')
            else:
                # .xlsx prefers openpyxl
                raw = pd.read_excel(file_path, header=None, dtype=str, engine='openpyxl').fillna('')
        except Exception as e:
            msg = str(e).lower()
            if 'xlrd' in msg or "no module named 'xlrd'" in msg:
                raise ImportError("Missing optional dependency 'xlrd' for .xls support. Install with:\n  python -m pip install \"xlrd>=2.0.1\"") from e
            if 'openpyxl' in msg or "no module named 'openpyxl'" in msg:
                raise ImportError("Missing optional dependency 'openpyxl' for .xlsx support. Install with:\n  python -m pip install openpyxl") from e
            raise
        header_idx = None
        for i, row in raw.iterrows():
            # collect non-empty cell strings in this row (lowercased)
            cells = [str(c).strip().lower() for c in row if str(c).strip() != '']
            if not cells:
                continue
            # require a cell that's exactly/contains "date" and at least one of "description" or "amount"
            has_date = any(header_word_re.search(c) for c in cells)
            has_descr_or_amt = any('description' in c or 'amount' in c for c in cells)
            if has_date and has_descr_or_amt:
                header_idx = i
                break
        if header_idx is not None:
            df = raw.iloc[header_idx+1:].copy().reset_index(drop=True)
            df.columns = raw.iloc[header_idx].astype(str)
        else:
            # fallback to treating as headerless
            df = raw.copy().reset_index(drop=True)
    else:
        # CSV path: read normally and detect header-like row if pandas picked a date as column name
        df = pd.read_csv(file_path, dtype=str).fillna('')
        # if pandas set column names that look like dates, re-read headerless below (handled later)

    # If column names look like a date (pandas used first data row as header), treat as headerless
    cols = list(df.columns)
    first_col_is_date_like = any(isinstance(c, str) and date_like_re.match(c) for c in cols)
    if first_col_is_date_like or (len(cols) > 0 and isinstance(cols[0], str) and date_like_re.match(str(cols[0]))):
        # ensure headerless: re-read with header=None for CSV, or use current df as headerless from Excel branch
        if ext in ('xls', 'xlsx'):
            raw = pd.read_excel(file_path, header=None, dtype=str).fillna('')
        else:
            raw = pd.read_csv(file_path, header=None, dtype=str).fillna('')

        n = len(raw)
        date_s = raw.iloc[:, 0].astype(str)
        # Many checking/marketrate exports: col0=date, col1=amount, col2="*", col3=description
        if raw.shape[1] > 3:
            amt_s = raw.iloc[:, 1].astype(str)
            descr_s = raw.iloc[:, 3].astype(str)
        elif raw.shape[1] > 2:
            amt_s = raw.iloc[:, 1].astype(str)
            descr_s = raw.iloc[:, 2].astype(str)
        elif raw.shape[1] > 1:
            amt_s = raw.iloc[:, 1].astype(str)
            descr_s = pd.Series([''] * n)
        else:
            amt_s = pd.Series([''] * n)
            descr_s = pd.Series([''] * n)
        acct_s = pd.Series([map_account(basename)] * n)
        out = pd.DataFrame({'Date': date_s, 'AMT': amt_s, 'DESCR': descr_s, 'ACCT': acct_s})
        return out.astype(str)

    # Otherwise treat df as headered table: find date/amount/description columns by header name (case-insensitive)
    def find_col_by_names(df_cols, subs):
        for c in df_cols:
            low = str(c).strip().lower()
            for s in subs:
                if s in low:
                    return c
        return None

    date_col = find_col_by_names(df.columns, ['date', 'transaction date', 'post date'])
    amt_col = find_col_by_names(df.columns, ['amount', 'amt', 'debit', 'credit'])
    descr_col = find_col_by_names(df.columns, ['description', 'descr', 'memo', 'details', 'payee'])
    # sensible fallbacks if names not found
    if date_col is None:
        date_col = df.columns[0]
    if amt_col is None and df.shape[1] > 1:
        amt_col = df.columns[1]
    if descr_col is None:
        # prefer a column after date/amount, else second column
        for c in df.columns:
            if c not in (date_col, amt_col):
                descr_col = c
                break
        if descr_col is None and df.shape[1] > 2:
            descr_col = df.columns[2]

    # helper: ensure we always return a 1-D Series for a column selection
    def _col_as_series(df_obj, col, length):
        if col is None or col not in df_obj.columns:
            return pd.Series([''] * length)
        val = df_obj[col]
        # if selection produced a DataFrame (duplicate labels), take first column
        if getattr(val, 'ndim', 1) == 2:
            val = val.iloc[:, 0]
        return val.astype(str).reset_index(drop=True)

    n = len(df)
    date_s = _col_as_series(df, date_col, n)
    amt_s = _col_as_series(df, amt_col, n)
    descr_s = _col_as_series(df, descr_col, n)
    acct_s = pd.Series([map_account(basename)] * n)

    out = pd.DataFrame({'Date': date_s, 'AMT': amt_s, 'DESCR': descr_s, 'ACCT': acct_s})
    return out.astype(str)

