from pathlib import Path


def get_absolute_zip_path(relative_path):
    p = Path(relative_path)
    file_url = p.resolve().as_uri()
    return file_url.replace('file', 'zip')
