from pathlib import Path


def get_working_dir() -> Path:
    """
    Get the absolute path of the current working directory.

    Returns:
        Path: An absolute `Path` object representing the current working directory.

    Example:
        >>> get_working_dir()
        PosixPath('/app')
    """
    return Path().resolve()


def get_target_dirpath(target_dir: str) -> Path:
    """
    Construct the absolute path to a given target directory, relative to the working directory.

    Args:
        target_dir (str): The name of the target directory.

    Returns:
        Path: A `Path` object representing the absolute path to the target directory.

    Example:
        >>> get_target_dirpath("output")
        PosixPath('/app/output')
    """
    return get_working_dir() / target_dir


def get_cache_dirpath(target_dir: str) -> Path:
    """
    Construct the path to a hidden '.cache' directory within the given target directory.

    Args:
        target_dir (str): The name of the target directory.

    Returns:
        Path: A `Path` object representing the absolute path to the '.cache' subdirectory.

    Example:
        >>> get_cache_dirpath("output")
        PosixPath('/app/output/.cache')
    """
    return get_target_dirpath(target_dir) / ".cache"
