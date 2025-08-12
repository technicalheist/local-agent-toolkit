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
      A list of file paths, or an error message if the directory does not exist.
    """
    if not os.path.isdir(directory):
        return f"Error: Directory '{directory}' not found."

    try:
        file_list = []
        for entry in os.scandir(directory):
            if entry.is_file():
                file_list.append(entry.path)
            elif entry.is_dir() and recursive:
                file_list.extend(list_files(entry.path, recursive=True))
        return file_list
    except Exception as e:
        return f"Error listing files in '{directory}': {e}"


def read_file(filepath):
    """
    Reads the content of a file.

    Args:
      filepath: The path to the file.

    Returns:
      The content of the file as a string, or an error message if the file doesn't exist.
    """
    if not os.path.exists(filepath):
        return f"Error: File '{filepath}' not found."
    try:
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{filepath}': {e}"


def write_file(filepath, content):
    """
    Writes content to a file.

    Args:
      filepath: The path to the file.
      content: The content to write to the file.

    Returns:
        A success message or an error message.
    """
    try:
        with open(filepath, "w") as f:
            f.write(content)
        return f"File '{filepath}' written successfully."
    except Exception as e:
        return f"Error writing to file '{filepath}': {e}"


def list_files_by_pattern(directory, pattern, recursive=False):
    """
    Lists files in a given directory that match a regex pattern.

    Args:
      directory: The path to the directory.
      pattern: The regex pattern to match file names.
      recursive: If True, lists files in subdirectories as well.

    Returns:
      A list of file paths that match the pattern, or an error message if the directory does not exist.
    """
    if not os.path.isdir(directory):
        return f"Error: Directory '{directory}' not found."

    try:
        file_list = []
        for entry in os.scandir(directory):
            if entry.is_file() and re.search(pattern, entry.name):
                file_list.append(entry.path)
            elif entry.is_dir() and recursive:
                file_list.extend(list_files_by_pattern(entry.path, pattern, recursive=True))
        return file_list
    except Exception as e:
        return f"Error listing files by pattern in '{directory}': {e}"


def ask_any_question_internet(question, vendor="Perplexity"):
    """
    Sends a question to an external internet-based API and returns the response text.

    Args:
        question (str): The question string to send to the API for answering.
        vendor (str, optional): The name of the vendor/service to use for answering the question.
            Defaults to "Perplexity".

    Returns:
        The response text from the API or an error message.
    """
    url = "https://macllm.technicalheist.com/ask" + vendor

    payload = json.dumps({"question": question})
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
