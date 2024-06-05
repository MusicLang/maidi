from .density import get_density_tags, DensityTagsProvider
from .polyphony import get_min_max_polyphony_tags, get_min_polyphony_tags, get_max_polyphony_tags
from .register import get_min_max_register_tags, get_min_max_registers
from .special_notes import get_special_notes_tags



CONTROL_PROVIDERS = [DensityTagsProvider]