import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError


def validate_input(user_input, schema_path):
    """
    Validate the input data against the provided JSON schema.
    
    Args:
        user_input: user input that has been parsed
        schema_path: the path to user input schema
    
    Return:
        data if the input is valide, None if not
    """
    with open(schema_path) as f:
        schema = json.load(f)
    try:
        validate(instance=user_input, schema=schema)
        print("Validation succeeded")
        return user_input
    except ValidationError as e:
        print("Validation failed")
        print(f"Error message: {e.message}")
        return None