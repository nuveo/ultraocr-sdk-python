from setuptools import find_packages, setup

setup(
    name="ultraocr-sdk-python",
    packages=find_packages(),
    version="0.1.0",
    description="UltraOCR Python SDK",
    author="Nuveo",
    install_requires=[],
    setup_requires=["pytest-runner"],
    tests_require=["pytest==8.3.3", "responses"],
    test_suite="tests",
)
