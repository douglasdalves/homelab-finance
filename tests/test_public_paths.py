"""Tests for ensuring private files stay outside the public web root."""

import sys
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from finance_app.server import (  # noqa: E402  # pylint: disable=wrong-import-position
    WEB_ROOT,
    FinanceHandler,
    resolve_public_path,
)


class PublicPathTests(unittest.TestCase):
    def test_resolves_pages_under_web_root(self):
        self.assertEqual(
            resolve_public_path("/dashboard.html"),
            WEB_ROOT / "dashboard.html",
        )

    def test_rejects_hidden_files(self):
        for path in ("/.env", "/config/.env"):
            with self.subTest(path=path), self.assertRaises(PermissionError):
                resolve_public_path(path)

    def test_rejects_traversal_and_encoded_traversal(self):
        for path in ("/../config/.env", "/%2e%2e/config/.env"):
            with self.subTest(path=path), self.assertRaises(PermissionError):
                resolve_public_path(path)

    def test_rejects_windows_separators(self):
        with self.assertRaises(PermissionError):
            resolve_public_path("/..\\config\\.env")

    def test_save_rejects_non_object_payload(self):
        with ThreadingHTTPServer(("127.0.0.1", 0), FinanceHandler) as server:
            thread = Thread(target=server.serve_forever)
            thread.start()
            try:
                request = Request(
                    f"http://127.0.0.1:{server.server_port}/api/save",
                    data=b"[]",
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(HTTPError) as response:
                    with urlopen(request):
                        pass
                self.assertEqual(response.exception.code, 400)
            finally:
                server.shutdown()
                thread.join()


if __name__ == "__main__":
    unittest.main()
