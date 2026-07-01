import re

from viral_platform.state.dataset_store import get_dataset

viral_sets_path = "src/viral_platform/viral_gene_sets/"


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
    Normalise a dataset feature name while preserving case.

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


def load_viral_gene_set(virus):
    """
    Loads all viral gene names and synonyms into a set.
    """

    viral_names = set()

    with open(f"{viral_sets_path}{virus}.txt") as f:
        for line in f:

            synonyms = [
                synonym.strip()
                for synonym in line.split(",")
                if synonym.strip()
            ]

            viral_names.update(synonyms)

    return viral_names


def find_viral_genes(value):

    adata = get_dataset()

    detected = {
        "EBV": {
            "features": set(),
            "genes": set(),
        },
        "HIV": {
            "features": set(),
            "genes": set(),
        },
        "SARS-CoV-2": {
            "features": set(),
            "genes": set(),
        },
        "InfluenzaA": {
            "features": set(),
            "genes": set(),
        },
        "InfluenzaB": {
            "features": set(),
            "genes": set(),
        },
        "RSV": {
            "features": set(),
            "genes": set(),
        },
        "Zika": {
            "features": set(),
            "genes": set(),
        },
    }

    viruses = (
        detected.keys()
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

    if value == "__auto__":
        return detected

    return detected[value]

def find_custom_viral_genes(custom_gene_list):
    """
    Detects viral genes based on a custom list provided by the user.
    """

    adata = get_dataset()

    detected = {
        "features": set(),
        "genes": set(),
        "not_found": set(),
    }

    # Split the custom gene list into individual gene names
    custom_genes = [gene.strip() for gene in custom_gene_list.split(",")]

    for feature in adata.var_names:

        gene = normalize_gene_name(feature, custom_genes)

        if gene in custom_genes:

            detected["features"].add(feature)
            detected["genes"].add(gene)
    
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
    detected["not_found"] = sorted(detected["not_found"])

    return detected