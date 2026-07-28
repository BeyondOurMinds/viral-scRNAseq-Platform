def test_cli_imports():
    # Basic smoke test to ensure the CLI entry point imports cleanly.
    from viral_platform.gui import ViralApp

    assert ViralApp is not None


def test_extract_prefix_accepts_geo_counts_filename():
    from viral_platform.io.loaders import _extract_prefix

    assert _extract_prefix("GSE158055_covid19_counts.mtx.gz") == "GSE158055_covid19_"


def test_prefixed_10x_discovery_accepts_counts_matrix(tmp_path, monkeypatch):
    from viral_platform.io import loaders

    sample_prefix = "GSE158055_covid19_"
    for name in (
        f"{sample_prefix}counts.mtx.gz",
        f"{sample_prefix}barcodes.tsv.gz",
        f"{sample_prefix}features.tsv.gz",
    ):
        (tmp_path / name).write_text("placeholder", encoding="utf-8")

    loaded_paths = []

    class DummyAnnData:
        def __init__(self):
            self.uns = {}

    def fake_load_prefixed_10x_sample(matrix_path):
        loaded_paths.append(matrix_path.name)
        return DummyAnnData()

    monkeypatch.setattr(loaders, "_load_prefixed_10x_sample", fake_load_prefixed_10x_sample)

    adata = loaders._load_prefixed_10x_samples(tmp_path)

    assert adata is not None
    assert adata.uns["sample_count"] == 1
    assert loaded_paths == [f"{sample_prefix}counts.mtx.gz"]

    # testing commit