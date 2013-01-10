# -*- coding: utf-8 -*-
import scope
import gsgenerator
import dxgenerator


def register():
    """Register this generator.
    """
    import agx.generator.dexterity
    from agx.core.config import register_generator
    register_generator(agx.generator.dexterity)
