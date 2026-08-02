import re


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
BIOLOGICAL_ID_TOKENS = {"donor", "patient", "participant", "subject", "individual"}


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


def sample_column_score(column_name):
    """Score likely sample columns from their metadata names.

    This deliberately avoids inspecting every value in an AnnData column.  Column
    names are stable metadata and make the automatic choice explainable; users
    can still choose a different column in the UI when their dataset uses an
    unusual convention.
    """
    normalized_name = normalize_column_name(column_name)
    sample_named = is_sample_named_column(column_name)
    tokens = set(split_identifier_tokens(column_name))

    if looks_like_identifier_column(column_name) and not sample_named:
        return 0

    if normalized_name == "sampleid" or (sample_named and has_standalone_id_token(column_name)):
        return 4000

    if sample_named:
        return 3000

    if has_standalone_id_token(column_name) and tokens.intersection(BIOLOGICAL_ID_TOKENS):
        return 2000

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
        score = sample_column_score(column)
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
