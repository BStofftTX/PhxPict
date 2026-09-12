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
    python_requires=">=3.9",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=["Pillow>=9.5", "pillow-heif>=0.18"],
    extras_require={
        "visual": ["torch>=2.1", "transformers>=4.38,<5"],
    },
    entry_points={
        "console_scripts": [
            "phxpict=phxpict.app:main",
            "phxpict-cli=phxpict.cli:main",
        ]
    },
)
