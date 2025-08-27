import json
from typing import Dict, Any, Union, List
import os
from pathlib import Path


def resolve_json_schema(path) -> Dict[str, Any]:
    # Handle both relative and absolute paths
    if not os.path.isabs(path):
        # For relative paths, resolve relative to this package
        package_dir = Path(__file__).parent
        path = package_dir / path

    schema = json.load(open(path, "r", encoding="utf-8"))

    def resolve_refs(obj, root_schema) -> Any:
        if isinstance(obj, dict):
            if '$ref' in obj:
                # find and resolve $ref
                ref_path = obj['$ref']
                if ref_path.startswith('#/'):
                    path_parts = ref_path[2:].split('/')
                    resolved = root_schema
                    for part in path_parts:
                        resolved = resolved[part]
                    return resolve_refs(resolved, root_schema)
                return obj
            else:
                # recursively resolve all properties in the object
                return {k: resolve_refs(v, root_schema) for k, v in obj.items()}
        elif isinstance(obj, list):
            # recursively resolve all items in the list
            return [resolve_refs(item, root_schema) for item in obj]
        else:
            return obj

    # resolve all $ref in the schema
    resolved_schema = resolve_refs(schema, schema)
    assert isinstance(resolved_schema, dict)
    return resolved_schema


def remove_null_items(obj: Union[Dict[str, Any], List[Any]]) -> Union[Dict[str, Any], List[Any]]:
    """
    Recursively remove items with value None from the dictionary.
    """
    if isinstance(obj, dict):
        return {k: remove_null_items(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [remove_null_items(item) for item in obj if item is not None]
    else:
        return obj
