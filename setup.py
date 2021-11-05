import setuptools

with open("README.md","r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="npend",
    version="1.0.1",
    author="chenzhun",
    author_email="863657500@qq.com",
    description="Provides a convenient way to append numpy arrays to a file.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/czwchenzhun/npend.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy',
        'sip',
    ]
)
