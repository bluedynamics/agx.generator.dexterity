import agx.generator.dexterity
from zope.interface import implementer
from agx.core.interfaces import IProfileLocation


@implementer(IProfileLocation)
class ProfileLocation(object):
    name = u'dexterity.profile.uml'
    package = agx.generator.dexterity
