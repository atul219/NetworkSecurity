from setuptools import find_packages, setup
import os
from typing import List


def get_requirements() -> List[str]:
    """
    This function will return list of requirements
    """

    requirement_list: List[str] = []
    try:
        with open('requirements.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                requirement = line.strip()
                # ignore empty line and -e .
                if requirement and requirement != '-e .':
                    requirement_list.append(requirement)
    
    except FileNotFoundError:
        print("requirements.txt file not found")

    return requirement_list

setup(
    name = "NetworkSecurity",
    version = "0.0.1",
    author = "Atul Yadav",
    author_email= "atulyadav219@gmail.com",
    packages= find_packages(),
    install_requires = get_requirements()
)