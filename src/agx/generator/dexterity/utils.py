from agx.core.util import read_target_node
from agx.generator.pyegg.utils import class_base_name


def type_id(source, target):
    # calculate type id
    class_ = read_target_node(source, target)
    if source.parent.stereotype('pyegg:pymodule'):
        name = '%s.%s' % (class_base_name(class_), class_.classname.lower())
    else:
        name = class_base_name(class_)
    return name
