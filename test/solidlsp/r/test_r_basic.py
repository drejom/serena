import shutil
import subprocess

import pytest

from solidlsp.ls_config import Language


@pytest.mark.r
class TestRLanguageServer:
    def test_file_matching(self):
        """Test R file pattern matching."""
        lang = Language.R
        matcher = lang.get_source_fn_matcher()

        assert matcher.is_relevant_filename("script.R")
        assert matcher.is_relevant_filename("analysis.r")
        assert matcher.is_relevant_filename("report.Rmd")
        assert matcher.is_relevant_filename("document.Rnw")
        assert not matcher.is_relevant_filename("script.py")

    def test_r_language_enum(self):
        """Test R language enum properties."""
        assert Language.R == "r"
        assert not Language.R.is_experimental()

    @pytest.fixture(scope="class")
    def check_r_available(self):
        """Skip tests if R is not available."""
        if not shutil.which("R"):
            pytest.skip("R is not installed")

        # Check if languageserver package is available
        try:
            result = subprocess.run(
                ["R", "--slave", "-e", "if (!require('languageserver', quietly=TRUE)) quit(status=1)"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                pytest.skip("R languageserver package is not installed")
        except Exception:
            pytest.skip("Cannot check R languageserver package")

    @pytest.mark.parametrize("language_server", [Language.R], indirect=True)
    def test_server_initialization(self, language_server, check_r_available):
        """Test that R language server initializes correctly."""
        assert language_server is not None
        # Test that the language server is an instance of our R language server
        assert language_server.language_id == "r"

    @pytest.mark.parametrize("language_server", [Language.R], indirect=True)
    def test_symbol_retrieval(self, language_server, check_r_available):
        """Test symbol retrieval from R files."""
        import os

        utils_file = os.path.join("test_repo", "R", "utils.R")

        # Test that we can request document symbols from R files
        symbols, _ = language_server.request_document_symbols(utils_file)
        symbol_names = [s.get("name") for s in symbols]

        assert "calculate_mean" in symbol_names
        assert "summarize_data" in symbol_names
