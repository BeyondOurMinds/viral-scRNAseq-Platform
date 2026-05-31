CURRENT_DATASET = None

def set_dataset(adata):
    global CURRENT_DATASET
    CURRENT_DATASET = adata

def get_dataset():
    global CURRENT_DATASET
    return CURRENT_DATASET