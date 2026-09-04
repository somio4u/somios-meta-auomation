import os

def public_url_for(repo_relative_path: str) -> str:
    """Instagram's API needs a public image URL. Since generated/user-supplied
    images get committed to the GitHub repo, raw.githubusercontent.com gives us
    a free public URL with no extra hosting service — as long as the file has
    already been pushed to the branch before this URL is used."""
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ.get("GITHUB_BRANCH", "main")
    rel = repo_relative_path.replace("\\", "/").lstrip("/")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{rel}"
