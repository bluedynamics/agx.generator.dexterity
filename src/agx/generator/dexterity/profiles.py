import agx.generator.dexterity
from zope.interface import implements
from agx.core.interfaces import IProfileLocation


class ProfileLocation(object):
    implements(IProfileLocation)
    name = u'dexterity.profile.uml'
    package = agx.generator.dexterity