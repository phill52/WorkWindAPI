import regex as re


# Function to check if a string is valid
def check_string(
    strVal,
    strName,
    minLength=None,
    maxLength=None,
    alphaOnly=False,  # Only allow letters
    numericOnly=False,  # Only allow numbers
    alphaNumericOnly=False,  # Only allow letters and numbers
    noSpaces=False,  # Cannot contain spaces
    customRegex=None,  # Custom regex to check against
):
    if strVal is None:
        raise ValueError(f"{strName} cannot be None")

    elif not strVal:
        raise ValueError(f"{strName} cannot be empty")

    elif not isinstance(strVal, str):
        raise ValueError(f"{strName} must be a string")

    strVal = strVal.strip()

    if minLength is not None:
        if len(strVal) <= minLength:
            raise ValueError(f"{strName} must be at least {minLength} characters")

    if maxLength is not None:
        if len(strVal) >= maxLength:
            raise ValueError(f"{strName} cannot be more than {maxLength} characters")

    if noSpaces and " " in strVal:
        raise ValueError(f"{strName} cannot contain spaces")

    if alphaOnly and not strVal.isalpha():
        raise ValueError(f"{strName} must only contain letters")

    if numericOnly and not strVal.isdigit():
        raise ValueError(f"{strName} must only contain numbers")

    if alphaNumericOnly and not strVal.isalnum():
        raise ValueError(f"{strName} must only contain letters and numbers")

    if customRegex is not None:
        if not re.match(customRegex, strVal):
            raise ValueError(f"{strName} is not valid")

    return strVal


# Function to check a address
def check_address(address):
    return check_string(
        address, "Address", minLength=1, maxLength=100, alphaNumericOnly=True
    )


# Function to check a city
def check_city(city):
    return check_string(city, "City", minLength=1, maxLength=30, alphaNumericOnly=True)


# Function to check a state
def check_state(state):
    return check_string(state, "State", minLength=2, maxLength=2, alphaOnly=True)


# Function to check a zip code
def check_zip(zip):
    return check_string(
        zip, "Zip", minLength=5, maxLength=5, numericOnly=True, noSpaces=True
    )


# Function to check a country
def check_country(country):
    return check_string(country, "Country", minLength=2, maxLength=2, alphaOnly=True)


# Function to check a phone number
def check_phone(phone):
    return check_string(phone, "Phone", minLength=10, maxLength=10, numericOnly=True)


# Function to check a email
def check_email(email):
    return check_string(
        email,
        "Email",
        minLength=1,
        maxLength=30,
        noSpaces=True,
        customRegex=r"[^@]+@[^@]+\.[^@]+",
    )


# Function to check if a project name is valid
def check_project_name(name):
    return check_string(name, "Project name", minLength=1, maxLength=50)


# Function to check if a project description is valid
def check_project_description(description):
    return check_string(description, "Project description", minLength=1, maxLength=300)
