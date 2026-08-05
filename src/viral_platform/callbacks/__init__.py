from .sidebar_callbacks import register_sidebar_callbacks
from .upload_callbacks import register_upload_callbacks
from .qc_callbacks import register_qc_callbacks
from .preprocessing_callbacks import register_preprocessing_callbacks
from .differential_expression_callbacks import register_differential_expression_callbacks
from .viral_detection_callbacks import register_vd_callbacks
from .viral_burden_callbacks import register_viral_burden_callbacks
from .isg_callbacks import register_isg_callbacks
from .host_virus_interaction_callbacks import register_host_virus_interaction_callbacks
from .ccc_callbacks import register_ccc_callbacks
from .scmovir_reference_callbacks import register_scmovir_reference_callbacks
from .cell_annotation_callbacks import register_cell_annotation_callbacks

__all__ = [
	"register_sidebar_callbacks",
	"register_upload_callbacks",
	"register_qc_callbacks",
	"register_preprocessing_callbacks",
    "register_cell_annotation_callbacks",
	"register_differential_expression_callbacks",
	"register_vd_callbacks",
	"register_viral_burden_callbacks",
	"register_isg_callbacks",
	"register_host_virus_interaction_callbacks",
	"register_ccc_callbacks",
	"register_scmovir_reference_callbacks",
]
