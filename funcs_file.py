def get_tools() -> list:
    return [get_current_temperature, get_current_wind_speed]


def get_globals() -> dict:
    return globals()



def get_current_temperature(
    location: str, temp: int = 20, unit: str = "fahrenheit"
) -> float:
    """
    Get the current temperature at a location. unit and temp are optional arguments.
    If the arguemnts unit and temp are not provided in prompt, set unit="celsius", temp=30
    Always make sure to return all arguments in your tool call

    Args:
        location: (required) The location to get the temperature for, in the format "City, Country"
        unit: Always set to "celsius" if not provided in prompt. The unit to return the temperature in. (choices: ["celsius", "fahrenheit"])
        temp: always set to 30 if not provided in prompt. If provided, use given value
    Returns:
        The current temperature at the specified location in the specified units, as a float.
    """
    return 104


def get_current_wind_speed(location: str) -> float:
    """
    Get the current wind speed in km/h at a given location.

    Args:
        location: The location to get the temperature for, in the format "City, Country"
    Returns:
        The current wind speed at the given location in km/h, as a float.
    """
    return 6.0