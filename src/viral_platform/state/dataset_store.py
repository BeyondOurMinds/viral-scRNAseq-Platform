RAW_DATASET = None
WORKING_DATASET = None

def set_dataset(adata):
    global RAW_DATASET
    RAW_DATASET = adata

def get_dataset():
    global RAW_DATASET
    return RAW_DATASET

def clear_dataset():
    global RAW_DATASET
    RAW_DATASET = None

def set_working_dataset(adata):
    global WORKING_DATASET
    WORKING_DATASET = adata

def get_working_dataset():
    global WORKING_DATASET
    return WORKING_DATASET

def clear_working_dataset():
    global WORKING_DATASET
    WORKING_DATASET = None