def test_cli_imports():
    # Basic smoke test to ensure the CLI entry point imports cleanly.
    from viral_platform.gui import ViralApp

    assert ViralApp is not None


def test_viral_app_uses_container_bind_settings(monkeypatch, caplog):
    from viral_platform.gui import ViralApp

    calls = {}

    class DummyLogger:
        disabled = False
        propagate = True

    class DummyServer:
        logger = DummyLogger()

    class DummyApp:
        def __init__(self):
            self.server = DummyServer()

        def run(self, **kwargs):
            calls.update(kwargs)

    app = object.__new__(ViralApp)
    app.app = DummyApp()

    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "8050")

    with caplog.at_level("INFO"):
        ViralApp.run(app)

    assert calls == {
        "host": "0.0.0.0",
        "port": 8050,
        "debug": False,
        "use_reloader": False,
        "dev_tools_hot_reload": False,
    }
    assert "http://localhost:8050/" in caplog.text


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
            import pandas as pd
            self.uns = {}
            self.obs = pd.DataFrame({"sample_id": ["sample_1"]}, index=["cell_1"])

    def fake_load_prefixed_10x_sample(matrix_path):
        loaded_paths.append(matrix_path.name)
        return DummyAnnData()

    monkeypatch.setattr(loaders, "_load_prefixed_10x_sample", fake_load_prefixed_10x_sample)

    adata = loaders._load_prefixed_10x_samples(tmp_path)

    assert adata is not None
    assert adata.uns["sample_count"] == 1
    assert loaded_paths == [f"{sample_prefix}counts.mtx.gz"]


def test_isg_payload_normalizer_handles_single_set_result():
    from viral_platform.callbacks.isg_callbacks import _normalize_automatic_detection_payload

    detected = {
        "features": ["ENSG00000123456"],
        "genes": ["ISG15"],
        "matched_features_by_gene": {"ISG15": ["ENSG00000123456"]},
    }

    normalized = _normalize_automatic_detection_payload(detected, "Interferon")

    assert normalized == {"Interferon": detected}

    # testing commit