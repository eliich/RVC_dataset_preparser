from setuptools import setup, find_packages

setup(
    name='RVC_dataset_preparser',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'moviepy==1.0.3',
        'pysrt==1.1.2',
        'pygame==2.5.2',
    ],
)
