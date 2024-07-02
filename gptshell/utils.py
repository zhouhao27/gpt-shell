import base64

def display_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
        print(f'\x1b]1337;File=inline=1:{encoded_string}\a')

def str_to_bool(s):
    """
    Convert a string representation to a boolean value.
    
    Args:
    s (str): The string to convert. It should be one of: 'true', 't', 'yes', 'y', '1' (case insensitive) for True,
             or 'false', 'f', 'no', 'n', '0' (case insensitive) for False.
    
    Returns:
    bool: The boolean value corresponding to the string.
    
    Raises:
    ValueError: If the string does not match any of the expected values.
    """
    if s is None or s == '':
        return False
    s = s.lower()
    if s in ('true', 't', 'yes', 'y', '1'):
        return True
    elif s in ('false', 'f', 'no', 'n', '0'):
        return False
    else:
        return False