import setuptools
import dftt_timecode as package
with open("README.md", "r",encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name=package.name,
    version=package.__version__,
    author="You Ziyuan",
    author_email="hikaridragon0216@gmail.com",
    description="Timecode library for film and TV industry, supports HFR and a bunch of cool features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OwenYou/dftt_timecode",
    packages=['dftt_timecode','dftt_timecode.core'],
    python_requires=">=3.11",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Natural Language :: Chinese (Simplified)",
        "Operating System :: OS Independent",
    ],
)
