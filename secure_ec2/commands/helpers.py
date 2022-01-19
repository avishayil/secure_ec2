from secure_ec2.src.constants import MetadataOptions, OperatingSystem

def normalize_os(input: str):
    """Normalize answer input to OperatingSystem enum."""
    if input == "Linux": return OperatingSystem.LINUX

    elif input == "Windows": return OperatingSystem.WINDOWS

    else: raise AttributeError(f"{input} is not a valid OS prompt answer")

def normalize_metadata(input: str):
    """Normalize answer input to MetadataOptions enum."""
    if input == "No": return MetadataOptions.DISABLED

    elif input == "Yes": return MetadataOptions.V2

    elif input == "I'm an expert, I only want secure IMDSv2.":
        return MetadataOptions.V2

    elif input == "I an expert, I need secure IMDSv2 and legacy IMDSv2.":
        return MetadataOptions.V1ANDV2

    else:
        raise AttributeError(f"{input} is not a valid Metadata prompt answer")
