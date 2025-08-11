import os
import re
import json
import requests


def list_files(directory, recursive=False):
    """
    Lists all files in a given directory.

    Args:
      directory: The path to the directory.
      recursive: If True, lists files in subdirectories as well.

    Returns:
      A list of file paths.
    """
    file_list = []
    for entry in os.scandir(directory):
        if entry.is_file():
            file_list.append(entry.path)
        elif entry.is_dir() and recursive:
            file_list.extend(list_files(entry.path, recursive=True))
    return file_list


def read_file(filepath):
    """
    Reads the content of a file.

    Args:
      filepath: The path to the file.

    Returns:
      The content of the file as a string, or None if the file doesn't exist.
    """
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return f.read()
    else:
        return None


def write_file(filepath, content):
    """
    Writes content to a file.

    Args:
      filepath: The path to the file.
      content: The content to write to the file.
    """
    with open(filepath, "w") as f:
        f.write(content)


def list_files_by_pattern(directory, pattern, recursive=False):
    """
    Lists files in a given directory that match a regex pattern.

    Args:
      directory: The path to the directory.
      pattern: The regex pattern to match file names.
      recursive: If True, lists files in subdirectories as well.

    Returns:
      A list of file paths that match the pattern.
    """
    file_list = []
    for entry in os.scandir(directory):
        if entry.is_file() and re.search(pattern, entry.name):
            file_list.append(entry.path)
        elif entry.is_dir() and recursive:
            file_list.extend(list_files_by_pattern(entry.path, pattern, recursive=True))
    return file_list


def ask_any_question_internet(question, vendor="Perplexity"):
    """
    Sends a question to an external internet-based API and returns the response text.

    This function is designed to interact with a remote question-answering service. It sends the provided question to the specified vendor's API endpoint and retrieves the response. The function handles HTTP errors gracefully and returns None if the request fails.

        question (str): The question string to send to the API for answering.
        vendor (str, optional): The name of the vendor/service to use for answering the question.
            Defaults to "Perplexity". The vendor name is appended to the base API URL.

        str or None: The response text from the API if the request is successful, otherwise None.

    Raises:
        None explicitly. Any exceptions during the request are caught and logged.

    Note:
    - Requires the `requests` and `json` modules.
    - Ensure that the vendor name matches the expected API endpoint.
    - The function prints an error message if the API call fails.
    Args:
        question: The question string to send to the API.

    Returns:
        The response text from the API.
    """
    url = "https://macllm.technicalheist.com/ask" + vendor

    payload = json.dumps({"question": question})
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None
