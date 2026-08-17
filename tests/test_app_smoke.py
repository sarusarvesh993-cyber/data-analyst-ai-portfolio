from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).parents[1]
APP_FILES = [
    ROOT / "streamlit_app.py",
    ROOT / "pages" / "1_Customer_Churn.py",
    ROOT / "pages" / "2_Retail_Sales_Forecast.py",
    ROOT / "pages" / "3_AB_Test_Calculator.py",
    ROOT / "pages" / "4_Ecommerce_SQL.py",
]


@pytest.mark.parametrize("app_file", APP_FILES, ids=lambda path: path.name)
def test_streamlit_page_has_no_uncaught_exception(app_file):
    app = AppTest.from_file(str(app_file), default_timeout=45).run()
    assert not app.exception, [exception.message for exception in app.exception]
