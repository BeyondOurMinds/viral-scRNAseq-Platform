import re


ACCESSION_PATTERN = re.compile(
    r"^(?:GSM|GSE|SRR|SRS|SRX|ERR|ERS|ERX|DRR|DRS|DRX|SAMN|SAMEA)[A-Za-z0-9_.-]*$",
    re.IGNORECASE,
)
TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")
IDENTIFIER_TOKENS = {
    "barcode",
    "cellbarcode",
    "cellid",
    "cellname",
    "obsname",
    "index",
    "uuid",
    "identifier",
}


def normalize_column_name(value):
    """Normalize metadata column names for tolerant matching."""
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def split_identifier_tokens(column_name):
    """Split snake/camel-case names into lowercase tokens."""
    as_snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(column_name))
    return [token.lower() for token in re.split(r"[^A-Za-z0-9]+", as_snake) if token]


def is_sample_named_column(column_name):
    """Return True for columns whose names imply sample identity."""
    tokens = split_identifier_tokens(column_name)
    return "sample" in tokens or "sample" in str(column_name).lower()


def has_standalone_id_token(column_name):
    """Return True for names with an ID token (for example PatientID/patient_id)."""
    return "id" in split_identifier_tokens(column_name)


def looks_like_identifier_column(column_name):
    """Return True when a column resembles a per-cell technical identifier."""
    normalized = normalize_column_name(column_name)
    tokens = split_identifier_tokens(column_name)
    return normalized in IDENTIFIER_TOKENS or any(token in IDENTIFIER_TOKENS for token in tokens)


def _non_empty_string_values(series):
    values = [str(value).strip() for value in series.dropna().tolist()]
    return [value for value in values if value]


def _values_look_list_like(series):
    values = _non_empty_string_values(series)
    if not values:
        return False
    list_like = [value for value in values if value.startswith("[") and value.endswith("]")]
    return (len(list_like) / float(len(values))) >= 0.8


def _values_look_like_accessions(series):
    values = _non_empty_string_values(series)
    if not values:
        return False
    return all(bool(ACCESSION_PATTERN.match(value)) for value in values)


def _values_are_simple_tokens(series):
    values = _non_empty_string_values(series)
    if not values:
        return False
    return all(bool(TOKEN_PATTERN.match(value)) for value in values)


def sample_column_score(column_name, series=None):
    """Score candidate sample columns using name and content-based tiers.

    Tiers:
    1) explicit sample-id naming
    2) sample-named column with accession-like values
    3) sample-named column with compact token values
    4) standalone ID token columns
    """
    normalized_name = normalize_column_name(column_name)
    sample_named = is_sample_named_column(column_name)

    if looks_like_identifier_column(column_name) and not sample_named:
        return 0

    if series is not None and _values_look_list_like(series):
        return 0

    if normalized_name == "sampleid" or (sample_named and has_standalone_id_token(column_name)):
        return 4000

    if series is not None and sample_named and _values_look_like_accessions(series):
        return 3000

    if series is not None and sample_named and _values_are_simple_tokens(series):
        return 2000

    if has_standalone_id_token(column_name):
        return 1000

    return 0


def rank_sample_columns(columns, obs_df=None, metadata_sample_columns=None, min_score=1):
    """Return candidate sample columns sorted by descending score and source order."""
    metadata_sample_columns = metadata_sample_columns or []
    combined = list(metadata_sample_columns) + list(columns)

    unique_columns = []
    seen = set()
    for column in combined:
        key = normalize_column_name(column)
        if key in seen:
            continue
        seen.add(key)
        unique_columns.append(column)

    scored = []
    for index, column in enumerate(unique_columns):
        series = None
        if obs_df is not None and column in obs_df.columns:
            series = obs_df[column]
        score = sample_column_score(column, series=series)
        if score >= min_score:
            scored.append((column, score, index))

    scored.sort(key=lambda item: (-item[1], item[2]))
    return [column for column, _, _ in scored]


def resolve_sample_column(columns, metadata_sample_columns=None, obs_df=None, min_score=1000):
    """Return best sample column candidate or None when no confident match exists."""
    ranked = rank_sample_columns(
        columns,
        obs_df=obs_df,
        metadata_sample_columns=metadata_sample_columns,
        min_score=min_score,
    )
    return ranked[0] if ranked else None
