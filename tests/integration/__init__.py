import pytest

# This allows pytest to show the values of the asserts.
pytest.register_assert_rewrite('tests.integration.utils')
from dotenv import load_dotenv
load_dotenv()