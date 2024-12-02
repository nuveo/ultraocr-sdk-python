from setuptools import setup

setup(
    name="ultraocr-sdk-python",
    packages=["ultraocr"],
    version="0.1.0",
    description="UltraOCR Python SDK",
    author="Nuveo",
    install_requires=["requests"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest==8.3.3", "responses"],
    test_suite="tests",
)
