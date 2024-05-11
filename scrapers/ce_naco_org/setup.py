# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'ce_naco_org',
    version      = '1.0',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = ce_naco_org.settings']},
)
