#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_local
----------------------------------

Local tests for `datafs` module.

Requirements
~~~~~~~~~~~~

A local MongoDB instance must be running. See ``examples/local.py`` for 
instructions.

"""

import pytest


from examples import local


def test_content():
    """Sample pytest test function with the pytest fixture as an argument.
    """
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    local.main()