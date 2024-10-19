import setuptools

with open("README.md", "r",encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="dftt_timecode",
    version="0.0.12",
    author="You Ziyuan",
    author_email="hikaridragon0216@gmail.com",
    description="Timecode library for film and TV industry, supports HFR and a bunch of cool features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OwenYou/dftt_timecode",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Natural Language :: Chinese (Simplified)",
        "Operating System :: OS Independent",
    ],
)
