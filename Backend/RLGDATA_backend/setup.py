from .setup import setup, find_packages

# Load requirements from requirements.txt
def parse_requirements(filename):
    with open(filename, "r") as req_file:
        return [line.strip() for line in req_file if line and not line.startswith("#")]

requirements = parse_requirements("requirements.txt")

setup(
    name="rlg_data",
    version="1.0.0",
    description="RLG Data: A Comprehensive Data Collection & Analysis Tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name or Company",
    author_email="your.email@example.com",
    url="https://github.com/your_username/rlg_data",
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "rlg_data=rlg_data.app:main",  # Replace with your app's main entry point if necessary
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="data scraping analysis flask celery redis",
    license="MIT",
)
