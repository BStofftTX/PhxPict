"""Compatibility setup entry point for older Python/pip installations."""

from pathlib import Path

from setuptools import find_packages, setup

ROOT = Path(__file__).parent

setup(
    name="phxpict",
    version="0.1.0",
    description="Privacy-first desktop photo indexing and search by MacroStofft",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="MacroStofft",
    license="LicenseRef-Proprietary",
    python_requires=">=3.12",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=["Pillow>=12.3", "pillow-heif>=1.7"],
    extras_require={
        "visual": ["torch>=2.14,<3", "transformers>=5.17,<6"],
        "dev": [
            "PyInstaller>=6.0",
            "ruff>=0.8",
            "mypy>=1.10",
            "pip-audit>=2.7",
        ],
    },
    entry_points={
        "console_scripts": [
            "phxpict=phxpict.app:main",
            "phxpict-cli=phxpict.cli:main",
        ]
    },
)
