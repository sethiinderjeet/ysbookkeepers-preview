"""Entry point for the website form mailer on GoDaddy cPanel "Setup Python App".

Create a second Python app with Application root = ysforms and Application URL = /forms.
It reuses the code and virtual environment packages of ../ysblog-admin.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ysblog-admin"))

from forms_app import create_app  # noqa: E402

application = create_app()
