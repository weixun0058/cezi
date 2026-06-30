from .divination import divination_bp
from .huangli_api import huangli_bp
from .lunming_api import lunming_bp
from .oracle_en_api import oracle_en_api_bp
from .pages import pages_bp
from .pages_en import pages_en_bp

ALL_BLUEPRINTS = (
    pages_en_bp,
    pages_bp,
    divination_bp,
    huangli_bp,
    lunming_bp,
    oracle_en_api_bp,
)
