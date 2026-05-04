import os


def cleanup_empty_dirs(start_path: str, project_root: str):
    """
    Recursively delete empty directories from start_path up to project_root.
    Stops at project_root (inclusive).
    """

    current = start_path

    while True:
        # 🔒 Stop if outside boundary
        if not current.startswith(project_root):
            break

        # Stop if path doesn't exist
        if not os.path.exists(current):
            break

        # Check if directory is empty
        if os.path.isdir(current) and not os.listdir(current):
            try:
                os.rmdir(current)  # only removes empty dir
            except Exception as e:
                print(f"Failed to delete folder {current}: {e}")
                break
        else:
            break

        # Stop at project root AFTER deleting it if empty
        if current == project_root:
            break

        # Move one level up
        current = os.path.dirname(current)
