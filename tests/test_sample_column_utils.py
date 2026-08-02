from viral_platform.utils.sample_column_utils import rank_sample_columns, resolve_sample_column


def test_resolve_sample_column_prefers_explicit_sample_id():
    columns = ["cell_barcode", "Sample_geo_accession", "sample_id", "donor_id"]

    assert resolve_sample_column(columns) == "sample_id"


def test_rank_sample_columns_excludes_technical_identifiers():
    columns = ["barcode", "cell_id", "sample", "patient_id"]

    assert rank_sample_columns(columns) == ["sample", "patient_id"]


def test_geo_accession_beats_sample_characteristics():
    columns = ["Sample_characteristics_ch1", "Sample_geo_accession"]

    assert resolve_sample_column(columns) == "Sample_geo_accession"


def test_sample_detection_does_not_scan_column_values():
    # The resolver accepts this opaque object because values are intentionally
    # not inspected when choosing a metadata column.
    opaque_obs = object()

    assert resolve_sample_column(["Sample"], obs_df=opaque_obs) == "Sample"
