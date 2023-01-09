import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")

        """
        It was giving this error: 'utf-8' codec can't decode byte 0x92 in position: invalid start byte
        So I had to change the decoding type to "cp1252".
        I found the solution here: https://bobbyhadz.com/blog/python-unicodedecodeerror-utf-8-codec-cant-decode-byte-0x92-in-position
        """
        return f.read().decode("cp1252") 
    except FileNotFoundError:
        return None
