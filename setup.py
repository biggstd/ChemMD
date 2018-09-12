from setuptools import setup, find_packages

setup(
    name='chemmd',
    author='Tyler Biggs',
    author_email='biggstd@gmail.com',
    version='0.1',
    packages=find_packages(),
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    include_package_data=True
)
