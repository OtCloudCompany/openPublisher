import json
from uuid import UUID


class CustomUUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)  # Convert UUID to string for serialization
        return super().default(obj)
