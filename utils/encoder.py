from flask.json.provider import DefaultJSONProvider
import six
try:
    # Try absolute import (when package is installed)
    from swagger_server.models.base_model_ import Model
except Exception:
    try:
        # Try relative import (when running as a package module)
        from ..models import Model
    except Exception:
        # Fallback minimal Model to avoid import errors during linting/static analysis.
        class Model:
            pass

class CustomJSONProvider(DefaultJSONProvider):
    include_nulls = False

    def default(self, o):
        if isinstance(o, Model):
            dikt = {}
            for attr, _ in six.iteritems(o.swagger_types):
                value = getattr(o, attr)
                if value is None and not self.include_nulls:
                    continue
                attr_name = o.attribute_map[attr]
                dikt[attr_name] = value
            return dikt
        return super().default(o)