"""Setup script for commit-ai."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme = Path(__file__).parent / 'README.md'
long_description = readme.read_text() if readme.exists() else ''

setup(
    name='commit-ai',
    version='0.1.0',
    author='Hassan',
    description='AI-powered git commit message generator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hassan/commit-ai',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Version Control :: Git',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=[
        'requests>=2.28.0',
    ],
    entry_points={
        'console_scripts': [
            'commit-ai=commit_ai.cli:main',
        ],
    },
    include_package_data=True,
)
