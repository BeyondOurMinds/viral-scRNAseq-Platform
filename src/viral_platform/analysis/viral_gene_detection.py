import re
from pathlib import Path

from viral_platform.state.dataset_store import get_dataset, get_working_dataset


VIRAL_SETS_PATH = Path("src/viral_platform/viral_gene_sets")


# def normalize_gene_name(gene):
#     """
#     Normalise a dataset feature name while preserving case.

#     Examples:
#         B958___BLLF1              -> BLLF1
#         LMP-2A(Exon_1)            -> LMP-2A
#         BLLF1-splice_variant      -> BLLF1
#     """

#     # Remove dataset prefixes
#     if "___" in gene:
#         gene = gene.split("___")[-1]

#     # Remove transcript annotations
#     gene = re.sub(r"\(.*?\)", "", gene)

#     # Remove common suffixes
#     gene = re.sub(r"-splice_variant$", "", gene)

#     return gene.strip()

def normalize_gene_name(gene, viral_names=None):
    """
        Normalize a viral-related feature name and optionally resolve to a known target.

        Use:
        - Canonicalizes feature names and, when a reference list is provided, attempts
            exact or bounded-substring resolution to a viral gene symbol.

        Interacts with:
        - find_viral_genes, find_custom_viral_genes, viral add-gene callback logic.

        Inputs:
        - gene (str): raw feature symbol from dataset.
        - viral_names (iterable[str]|None): optional lookup symbols.

        Outputs:
        - str: cleaned symbol or resolved lookup symbol.

    Examples:
        B958___BLLF1                          -> BLLF1
        LMP-2A(Exon_1)                        -> LMP-2A
        BLLF1-splice_variant                  -> BLLF1
        B958___Cp-EBNA1                       -> EBNA1
        ebv-miR-BART1-3p                      -> BART1
        FR_Repeats_EBNA1_Binding_sites_I      -> EBNA1
    """

    # Remove dataset prefix
    if "___" in gene:
        gene = gene.split("___")[-1]

    # Remove bracket annotations
    gene = re.sub(r"\(.*?\)", "", gene)

    # Remove common suffixes
    gene = re.sub(r"-splice_variant$", "", gene)

    gene = gene.strip()

    # If no viral gene list supplied, return the cleaned name
    if viral_names is None:
        return gene

    # Exact match first
    if gene in viral_names:
        return gene

    # Otherwise search for a complete viral gene inside the annotation
    for viral_gene in viral_names:

        # Very short viral genes are too ambiguous.
        if len(viral_gene) <= 2:
            continue

        pattern = (
            rf'(?<![A-Za-z0-9])'
            rf'{re.escape(viral_gene)}'
            rf'(?![A-Za-z0-9])'
        )

        if re.search(pattern, gene):
            return viral_gene

    return gene


def list_viral_gene_sets():
    """List all available viral gene set files.

    Use:
    - Drives dropdown options and auto-detection set iteration.

    Interacts with:
    - find_viral_genes, register_vd_callbacks.

    Inputs:
    - None.

    Outputs:
    - list[str]: file stems for *.txt files in VIRAL_SETS_PATH.
    """

    if not VIRAL_SETS_PATH.exists():
        return []

    return sorted(path.stem for path in VIRAL_SETS_PATH.glob("*.txt"))


def load_viral_gene_set(virus):
    """
    Load one viral gene set file into a synonym set.

    Use:
    - Provides lookup symbols for automatic/custom viral detection.

    Interacts with:
    - find_viral_genes.

    Inputs:
    - virus (str): viral set file stem.

    Outputs:
    - set[str]: all known symbols/aliases in the selected set file.
    """

    viral_names = set()
    viral_file = VIRAL_SETS_PATH / f"{virus}.txt"

    with viral_file.open() as f:
        for line in f:

            synonyms = [
                synonym.strip()
                for synonym in line.split(",")
                if synonym.strip()
            ]

            viral_names.update(synonyms)

    return viral_names


def find_viral_genes(value):
    """Run automatic viral-gene detection for one or all configured viral sets.

    Use:
    - Main detection path used by the viral detection panel.

    Interacts with:
    - get_dataset, load_viral_gene_set, normalize_gene_name, register_vd_callbacks.

    Inputs:
    - value (str): virus name or "__auto__" to scan all sets.

    Outputs:
    - dict: per-virus detected genes/features and gene->feature mapping.
    """

    adata = get_working_dataset() or get_dataset()
    if adata is None:
        raise ValueError("No active dataset found for viral gene detection.")

    available_sets = list_viral_gene_sets()
    detected = {
        virus: {
            "features": set(),
            "genes": set(),
            "matched_features_by_gene": {},
        }
        for virus in available_sets
    }

    viruses = (
        available_sets
        if value == "__auto__"
        else [value]
    )

    for virus in viruses:

        try:

            viral_names = load_viral_gene_set(virus)

            for feature in adata.var_names:

                gene = normalize_gene_name(feature, viral_names)

                if gene in viral_names:

                    detected[virus]["features"].add(feature)
                    detected[virus]["genes"].add(gene)
                    detected[virus]["matched_features_by_gene"].setdefault(gene, set()).add(feature)

            print(
                f"{virus}: "
                f"{len(detected[virus]['genes'])} unique genes, "
                f"{len(detected[virus]['features'])} matching features."
            )

        except FileNotFoundError:
            print(f"Gene set for {virus} not found.")

    # Convert sets to sorted lists for returning
    for virus in detected:

        detected[virus]["features"] = sorted(
            detected[virus]["features"]
        )

        detected[virus]["genes"] = sorted(
            detected[virus]["genes"]
        )
        detected[virus]["matched_features_by_gene"] = {
            gene: sorted(features)
            for gene, features in sorted(detected[virus]["matched_features_by_gene"].items())
        }

    if value == "__auto__":
        return detected

    return detected.get(
        value,
        {
            "features": [],
            "genes": [],
            "matched_features_by_gene": {},
        },
    )

def find_custom_viral_genes(custom_gene_list):
    """
    Detect viral genes from a user-provided list.

    Use:
    - Custom detection path and baseline state for add/remove curation.

    Interacts with:
    - get_dataset, normalize_gene_name, register_vd_callbacks.

    Inputs:
    - custom_gene_list (str): comma-separated user-entered genes.

    Outputs:
    - dict: detected genes/features, gene->feature mapping, and not_found list.
    """

    adata = get_working_dataset() or get_dataset()
    if adata is None:
        raise ValueError("No active dataset found for viral gene detection.")

    detected = {
        "features": set(),
        "genes": set(),
        "matched_features_by_gene": {},
        "not_found": set(),
    }

    # Split the custom gene list into individual gene names
    custom_genes = [gene.strip() for gene in custom_gene_list.split(",")]

    for feature in adata.var_names:

        gene = normalize_gene_name(feature, custom_genes)

        if gene in custom_genes:

            detected["features"].add(feature)
            detected["genes"].add(gene)
            detected["matched_features_by_gene"].setdefault(gene, set()).add(feature)
    
    # Identify genes from the custom list that were not found in the dataset
    detected["not_found"] = set(custom_genes) - detected["genes"]

    print(
        f"Custom: "
        f"{len(detected['genes'])} unique genes, "
        f"{len(detected['features'])} matching features, "
        f"{len(detected['not_found'])} not found."
    )

    # Convert sets to sorted lists for returning
    detected["features"] = sorted(detected["features"])
    detected["genes"] = sorted(detected["genes"])
    detected["matched_features_by_gene"] = {
        gene: sorted(features)
        for gene, features in sorted(detected["matched_features_by_gene"].items())
    }
    detected["not_found"] = sorted(detected["not_found"])

    return detected