# Function to check if a string is valid
def check_string(
    strVal,
    strName,
    minLength=None,
    maxLength=None,
):
    if strVal is None:
        raise ValueError(f"{strName} cannot be None")

    elif not strVal:
        raise ValueError(f"{strName} cannot be empty")

    elif not isinstance(strVal, str):
        raise ValueError(f"{strName} must be a string")

    if minLength is not None:
        if len(strVal) <= minLength:
            raise ValueError(f"{strName} must be at least {minLength} characters")

    if maxLength is not None:
        if len(strVal) >= maxLength:
            raise ValueError(f"{strName} cannot be more than {maxLength} characters")

    return strVal.strip()


# Function to check if a project name is valid
def check_project_name(name):
    return check_string(name, "Project name", minLength=1, maxLength=50)
