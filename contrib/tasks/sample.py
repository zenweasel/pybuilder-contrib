#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pybuilder.core import task

@task
def say_hello():
    print "Hello, PyBuilder"