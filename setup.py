import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bingtiles-Claudio9701", # Replace with your own username
    version="0.0.1",
    author="Claudio Ortega",
    author_email="claudio.rtega2701@gmail.com",
    description="A small library for Bing Maps Sytstem. Adapted from Microsoft Official Docs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Claudio9701/bingtiles",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
