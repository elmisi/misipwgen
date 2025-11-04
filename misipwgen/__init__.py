from .misipwgen import MisiPwGen as _LegacyMisiPwGen
from .generator_v2 import MisiPwGenV2

__version__ = "0.2.0"

# Friendlier alias for v2 (default public name)
class MisiPwGenPositional(MisiPwGenV2):
    @classmethod
    def legacy(cls, *args, **kwargs):
        return _LegacyMisiPwGen(*args, **kwargs)


# Public default: modern positional generator
MisiPwGen = MisiPwGenPositional
