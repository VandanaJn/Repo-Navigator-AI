import pytest

# This conftest provides a deterministic fake GitHub client so integration
# tests that depend on repository contents become repeatable. It only fakes
# the minimal surface used by `agents/repo_navigator/sub_agents/tools/githubtools.py`.

class FakeItem:
    def __init__(self, type_, name, path, size=0):
        self.type = type_
        self.name = name
        self.path = path
        self.size = size


class FakeContent:
    def __init__(self, name, path, content_bytes):
        self.name = name
        self.path = path
        self.decoded_content = content_bytes
        self.size = len(content_bytes)


class FakeRepo:
    def __init__(self, full_name):
        self.full_name = full_name

    def get_contents(self, path, ref=None):
        # Normalize path
        p = (path or "").strip("/")
        owner_repo = self.full_name

        # Return deterministic directory listing for known repos
        if owner_repo.endswith("yt-channel-crawler"):
            if p == "" or p == ".":
                return [
                    FakeItem("file", "batch_transcribe_v3.py", "batch_transcribe_v3.py", 1234),
                    FakeItem("file", "requirements.txt", "requirements.txt", 40),
                ]
            if p == "batch_transcribe_v3.py":
                content = (
                    "# batch_transcribe_v3.py\n" 
                    "# pipeline: download audio -> convert -> transcribe with Whisper\n"
                    "def transcribe():\n    pass\n"
                ).encode("utf-8")
                return FakeContent("batch_transcribe_v3.py", "batch_transcribe_v3.py", content)
            if p == "requirements.txt":
                content = (
                    "google-cloud-storage==2.5.0\n"
                    "whisper==20230314\n"
                ).encode("utf-8")
                return FakeContent("requirements.txt", "requirements.txt", content)

        if owner_repo.endswith("chatbot-backend"):
            if p == "" or p == ".":
                return [
                    FakeItem("file", "app.py", "app.py", 512),
                    FakeItem("file", "pdf_indexer.py", "pdf_indexer.py", 2048),
                    FakeItem("file", "milvus_integration.py", "milvus_integration.py", 1024),
                ]
            if p == "app.py":
                content = (
                    "# app.py\n"
                    "from flask import Flask\n"
                    "app = Flask(__name__)\n"
                    "@app.route('/')\n"
                    "def home():\n    return 'Hello, World!'\n"
                ).encode("utf-8")
                return FakeContent("app.py", "app.py", content)
            if p == "pdf_indexer.py":
                content = (
                    "# pdf_indexer.py\n"
                    "def index_pdf(file_path):\n    pass\n"
                ).encode("utf-8")
                return FakeContent("pdf_indexer.py", "pdf_indexer.py", content)
            if p == "milvus_integration.py":
                content = (
                    "# milvus_integration.py\n"
                    "def connect_milvus():\n    pass\n"
                ).encode("utf-8")
                return FakeContent("milvus_integration.py", "milvus_integration.py", content)

        # Default: empty directory
        return []


class FakeGithub:
    def __init__(self, token=None):
        self.token = token

    def get_repo(self, full_name):
        return FakeRepo(full_name)


@pytest.fixture(autouse=True)
def patch_github_client(monkeypatch):
    # Patch _get_github_client() to return our fake client for integration tests.
    try:
        import repo_navigator.sub_agents.tools.githubtools as gt

        # Make the module treat our FakeContent as the ContentFile type so
        # `isinstance(..., ContentFile)` checks succeed for file responses.
        monkeypatch.setattr(gt, "ContentFile", FakeContent, raising=False)

        fake = FakeGithub()
        # Patch _get_github_client to return the fake client instead of None or real client
        monkeypatch.setattr(gt, "_get_github_client", lambda: fake)
    except Exception:
        # If import fails for some reason, tests will continue without patching;
        # this keeps the fixture safe during partial test runs.
        pass