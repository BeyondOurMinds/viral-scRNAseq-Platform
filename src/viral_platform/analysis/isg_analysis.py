import re
from pathlib import Path

from viral_platform.state.dataset_store import get_dataset, get_working_dataset


ISG_SETS_PATH = Path(__file__).parent / "isg_sets"


def normalize_gene_name(gene):
	"""Canonicalize dataset feature names for ISG comparison.

	Use:
	- Produces a stable symbol used by all ISG matching functions.

	Interacts with:
	- parse_isg_line, load_isg_set, find_isg_genes, find_custom_isg_genes.

	Inputs:
	- gene (str): raw feature name from dataset or set file.

	Outputs:
	- str: cleaned uppercase symbol.
	"""

	if "___" in gene:
		gene = gene.split("___")[-1]

	gene = re.sub(r"\(.*?\)", "", gene)
	gene = re.sub(r"-splice_variant$", "", gene)
	return gene.strip().upper()


def parse_isg_line(line):
	"""Parse one ISG set line into a core symbol plus aliases.

	Use:
	- Converts one line from an ISG set into canonical comparison tokens.

	Interacts with:
	- normalize_gene_name, load_isg_set.

	Inputs:
	- line (str): one line from an ISG set text file.

	Outputs:
	- tuple[str|None, set[str]]: (core_gene, aliases). Empty/invalid lines return (None, set()).
	"""

	cleaned = line.strip()
	if not cleaned:
		return None, set()

	tokens = [part.strip() for part in cleaned.split(",") if part.strip()]
	if not tokens:
		return None, set()

	core_gene = normalize_gene_name(re.sub(r"\(.*?\)", "", tokens[0]).strip())
	aliases = {core_gene}

	for token in tokens:
		aliases.add(normalize_gene_name(token))

		# Expand common "GENE (ALIAS)" format into separate aliases.
		paren_matches = re.findall(r"\(([^)]+)\)", token)
		for alias in paren_matches:
			alias = alias.strip()
			if alias:
				aliases.add(normalize_gene_name(alias))

		no_paren = re.sub(r"\(.*?\)", "", token).strip()
		if no_paren:
			aliases.add(normalize_gene_name(no_paren))

	return core_gene, aliases


def list_isg_sets():
	"""List all available ISG set files.

	Use:
	- Drives dropdown options and auto-detection set iteration.

	Interacts with:
	- find_isg_genes, register_isg_callbacks.

	Inputs:
	- None.

	Outputs:
	- list[str]: file stems for *.txt files in ISG_SETS_PATH.
	"""

	if not ISG_SETS_PATH.exists():
		return []

	return sorted(path.stem for path in ISG_SETS_PATH.glob("*.txt"))


def load_isg_set(set_name):
	"""Load one ISG set and build matching metadata.

	Use:
	- Constructs canonical core genes and alias->core lookup for robust matching.

	Interacts with:
	- parse_isg_line, find_isg_genes, ISG curation callbacks.

	Inputs:
	- set_name (str): ISG set stem name.

	Outputs:
	- dict: {"core_genes": set[str], "alias_to_core": dict[str, str]}.
	"""

	core_genes = set()
	alias_to_core = {}
	isg_file = ISG_SETS_PATH / f"{set_name}.txt"

	with isg_file.open() as handle:
		for line in handle:
			core_gene, aliases = parse_isg_line(line)
			if core_gene is None:
				continue

			core_genes.add(core_gene)
			for alias in aliases:
				alias_to_core.setdefault(alias, core_gene)

	return {
		"core_genes": core_genes,
		"alias_to_core": alias_to_core,
	}


def find_isg_genes(set_name):
	"""Detect ISG matches from curated sets against dataset features.

	Use:
	- Primary automatic ISG detection path used by the ISG panel.

	Interacts with:
	- get_dataset, list_isg_sets, load_isg_set, register_isg_callbacks.

	Inputs:
	- set_name (str): specific set name or "__auto__" for all sets.

	Outputs:
	- dict: per-set detection payload with genes, features, mapping, and set totals.
	"""

	adata = get_working_dataset() or get_dataset()
	if adata is None:
		raise ValueError("No active dataset found for ISG detection.")

	available_sets = list_isg_sets()
	detected = {
		isg_set: {
			"features": set(),
			"genes": set(),
			"matched_features_by_gene": {},
			"total_core_genes": 0,
		}
		for isg_set in available_sets
	}

	selected_sets = available_sets if set_name == "__auto__" else [set_name]

	for isg_set in selected_sets:
		try:
			isg_set_data = load_isg_set(isg_set)
			alias_to_core = isg_set_data["alias_to_core"]
			detected[isg_set]["total_core_genes"] = len(isg_set_data["core_genes"])

			for feature in adata.var_names:
				gene = normalize_gene_name(feature)
				core_match = alias_to_core.get(gene)

				if core_match:
					detected[isg_set]["features"].add(feature)
					detected[isg_set]["genes"].add(core_match)
					detected[isg_set]["matched_features_by_gene"].setdefault(core_match, set()).add(feature)

		except FileNotFoundError:
			print(f"ISG set file for {isg_set} not found.")

	for isg_set in detected:
		detected[isg_set]["features"] = sorted(detected[isg_set]["features"])
		detected[isg_set]["genes"] = sorted(detected[isg_set]["genes"])
		detected[isg_set]["matched_features_by_gene"] = {
			gene: sorted(features)
			for gene, features in sorted(detected[isg_set]["matched_features_by_gene"].items())
		}

	if set_name == "__auto__":
		return detected

	return detected.get(set_name, {"features": [], "genes": []})


def find_custom_isg_genes(custom_gene_list):
	"""Detect ISG matches from a user-provided custom list.

	Use:
	- Custom detection path and add/remove curation baseline.

	Interacts with:
	- get_dataset, normalize_gene_name, register_isg_callbacks.

	Inputs:
	- custom_gene_list (str): comma-separated symbols entered by the user.

	Outputs:
	- dict: detected genes/features, per-gene feature mapping, and not_found list.
	"""

	adata = get_working_dataset() or get_dataset()
	if adata is None:
		raise ValueError("No active dataset found for ISG detection.")

	detected = {
		"features": set(),
		"genes": set(),
		"matched_features_by_gene": {},
		"not_found": set(),
	}

	custom_genes = [normalize_gene_name(gene) for gene in custom_gene_list.split(",") if gene.strip()]

	for feature in adata.var_names:
		gene = normalize_gene_name(feature)

		if gene in custom_genes:
			detected["features"].add(feature)
			detected["genes"].add(gene)
			detected["matched_features_by_gene"].setdefault(gene, set()).add(feature)

	detected["not_found"] = set(custom_genes) - detected["genes"]

	detected["features"] = sorted(detected["features"])
	detected["genes"] = sorted(detected["genes"])
	detected["matched_features_by_gene"] = {
		gene: sorted(features)
		for gene, features in sorted(detected["matched_features_by_gene"].items())
	}
	detected["not_found"] = sorted(detected["not_found"])

	return detected
