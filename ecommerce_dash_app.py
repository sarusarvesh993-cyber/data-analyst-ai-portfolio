"""Production entry point for the standalone e-commerce Dash application."""
from __future__ import annotations

import os

from portfolio_app.ecommerce_dash import create_dash_app

app = create_dash_app()
server = app.server

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8050")),
        debug=os.getenv("DASH_DEBUG", "0") == "1",
    )
