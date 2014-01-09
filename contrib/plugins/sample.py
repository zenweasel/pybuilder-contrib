#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pybuilder.core import init

@init
def initialize_my_plugin(project, logger):
    project.set_property("property_for_my_plugin", 42)
    my_property = project.get_property("property_for_my_plugin")
    logger.info("The property for my plugin is {0}".format(my_property))

