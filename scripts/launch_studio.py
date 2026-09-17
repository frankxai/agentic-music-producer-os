#!/usr/bin/env python3
"""Launch the Agentic Music Producer OS Studio Dashboard locally."""

from __future__ import annotations

import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8844
STUDIO_DIR = Path(__file__).resolve().parent.parent / "studio"


class StudioHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STUDIO_DIR), **kwargs)


def main():
    print(f"🚀 Starting Agentic Music Producer OS Studio on http://localhost:{PORT}")
    print(f"📁 Serving directory: {STUDIO_DIR}")

    with socketserver.TCPServer(("", PORT), StudioHandler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print(f"🌐 Studio Dashboard URL: {url}")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Studio server stopped.")


if __name__ == "__main__":
    main()
