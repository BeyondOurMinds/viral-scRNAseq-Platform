from dash import Output, Input, State, no_update, dcc
from viral_platform.state.dataset_store import cache_results, get_working_dataset, set_working_dataset
import logging

logger = logging.getLogger(__name__)

def register_pathway_enrichment_callbacks(app):
    return  # Temporarily disable pathway enrichment callbacks until implementation is complete