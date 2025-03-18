from setuptools import setup, find_packages

setup(
    name="drumtrackkai",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "flask-jwt-extended",
        "flask-cors",
        "flask-limiter",
        "python-dotenv",
        "yt-dlp",
        "google-api-python-client",
        "validators",
    ],
)
