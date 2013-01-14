from node.ext.directory import Directory
from node.ext.template import DTMLTemplate
from node.ext.uml.utils import TaggedValues
from agx.core import (
    handler,
    token
)
from agx.core.util import (
    read_target_node,
    dotted_path,
)
from agx.generator.pyegg.utils import (
    egg_source,
    class_base_name,
    class_full_name,
)
from agx.generator.dexterity.schema import standard_behaviors
from agx.generator.dexterity.utils import type_id
from agx.generator.dexterity.dxgenerator import getschemaclass


@handler('gsprofiletypes', 'uml2fs', 'connectorgenerator',
         'contenttype', order=100)
def gsprofiletypes(self, source, target):
    """Create or extend types.xml and corresponding TYPENAME.xml.
    """
    egg = egg_source(source)
    package = read_target_node(egg, target.target)
    default = package['profiles']['default']

    # create types foder if not exists
    if not 'types' in default:
        default['types'] = Directory()

    # read or create types.xml
    if 'types.xml' in default:
        types = default['types.xml']
    else:
        types = default['types.xml'] = DTMLTemplate()

    # set template and params if not done yet
    if not types.template:
        types.template = 'agx.generator.plone:templates/types.xml'
        types.params['portalTypes'] = list()

    # calculate type name
    full_name = type_id(source, target.target)

    # add portal type to types.xml
    types.params['portalTypes'].append({
        'name': full_name,
        'meta_type': 'Dexterity FTI',
    })

    # add TYPENAME.xml to types folder
    # read or create TYPENAME.xml
    name = '%s.xml' % full_name
    if name in default['types']:
        type = default['types'][name]
    else:
        type = default['types'][name] = DTMLTemplate()

    # set template used for TYPENAME.xml
    type.template = 'agx.generator.plone:templates/type.xml'

    # set template params
    # FTI properties can be added by prefixing param key with 'fti:'
    # XXX: calculate from model
    content_icon = '++resource++%s/%s_icon.png' % (
        egg.name, source.name.lower())

    type.params['ctype'] = dict()

    # general
    type.params['ctype']['name'] = full_name
    type.params['ctype']['meta_type'] = 'Dexterity FTI'
    type.params['ctype']['i18n_domain'] = egg.name
    
    # basic metadata
    type.params['ctype']['title'] = source.name
    type.params['ctype']['description'] = source.name
    type.params['ctype']['content_icon'] = content_icon
    type.params['ctype']['allow_discussion'] = 'False'
    type.params['ctype']['global_allow'] = 'True'
    # XXX: maybe False for non contained ones?
    type.params['ctype']['filter_content_types'] = 'True'
    type.params['ctype']['allowed_content_types'] = list()

    # dexterity specific
    class_ = read_target_node(source, target.target)
    schemaclass=getschemaclass(source,target)
    schema = '%s.%s' % (class_base_name(class_), schemaclass.classname)

    # XXX: check whether container or leaf
    if token(str(class_.uuid), False, dont_generate=False).dont_generate:
        klass = 'plone.dexterity.content.Item'
    else:
        klass = '%s.%s' % (class_base_name(class_), class_.classname)

    type.params['ctype']['schema'] = schema
    type.params['ctype']['klass'] = klass
    type.params['ctype']['add_permission'] = 'cmf.AddPortalContent'
    type.params['ctype']['behaviors'] = list()

    # View information
    type.params['ctype']['view_methods'] = ['view']
    type.params['ctype']['default_view'] = 'view'
    type.params['ctype']['default_view_fallback'] = 'False'

    # Method aliases
    type.params['ctype']['aliases'] = list()
    type.params['ctype']['aliases'].append({
        'from': '(Default)',
        'to': '(dynamic view)',
    })
    type.params['ctype']['aliases'].append({
        'from': 'view',
        'to': '(selected layout)',
    })
    type.params['ctype']['aliases'].append({
        'from': 'edit',
        'to': '@@edit',
    })
    type.params['ctype']['aliases'].append({
        'from': 'sharing',
        'to': '@@sharing',
    })

    # Actions
    type.params['ctype']['actions'] = list()
    type.params['ctype']['actions'].append({
        'action_id': 'edit',
        'title': 'Edit',
        'category': 'object',
        'condition_expr': '',
        'url_expr': 'string:${object_url}/edit',
        'visible': 'True',
        'permissions': ['Modify portal content'],
    })
    type.params['ctype']['actions'].append({
        'action_id': 'view',
        'title': 'View',
        'category': 'object',
        'condition_expr': '',
        'url_expr': 'string:${object_url}/view',
        'visible': 'True',
        'permissions': ['View'],
    })


@handler('gscomposition', 'uml2fs', 'zcasemanticsgenerator',
         'association', order=100)
def gscomposition(self, source, target):
    # get container. ownedEnds len should always be 1
    container = source.ownedEnds[0].type
    class_ = read_target_node(container, target.target)

    # lookup child from memberEnds
    child = None
    for member in source.memberEnds:
        if member.type is not container:
            child = member.type
            break

    # self containment
    if child is None:
        child = container

    # both end types need to be content types
    if not container.stereotype('plone:content_type') \
      or not child.stereotype('plone:content_type'):
        return

    # read fti and append allowed content type
    container_name = type_id(container, target.target)
    child_name = type_id(child, target.target)

    egg = egg_source(source)
    package = read_target_node(egg, target.target)
    default = package['profiles']['default']

    name = '%s.xml' % container_name
    fti = default['types'][name]
    fti.params['ctype']['allowed_content_types'].append(child_name)
    # otherwise the class name is already set
    if token(str(class_.uuid), False, dont_generate=False).dont_generate:
        fti.params['ctype']['klass'] = 'plone.dexterity.content.Container'


@handler('gsdynamicview', 'uml2fs', 'semanticsgenerator',
         'dependency', order=100)
def gsdynamicview(self, source, target):
    """Add view method to FTI's of all dependent content types.
    """
    if not source.supplier.stereotype('plone:content_type') \
      or not source.client.stereotype('plone:dynamic_view'):
        return

    view = source.client
    content_type = source.supplier
    package = read_target_node(egg_source(content_type), target.target)
    default = package['profiles']['default']
    full_name = type_id(content_type, target.target)
    name = '%s.xml' % full_name
    type_xml = default['types'][name]
    tgv = TaggedValues(view)
    viewname = tgv.direct('name', 'plone:dynamic_view', view.name)
    type_xml.params['ctype']['view_methods'].append(viewname)


def get_standard_behaviors(source):
    behaviors = list()
    for stereotype in standard_behaviors.keys():
        if source.stereotype(stereotype):
            behaviors.append(standard_behaviors[stereotype])
    return behaviors


@handler('standardbehavior', 'uml2fs', 'zcasemanticsgenerator', 'contenttype')
def standardbehavior(self, source, target):
    # XXX: cleanup standard behaviors, some inherit each other
    if source.stereotype('dexterity:behavior_standard'):
        behaviors = standard_behaviors.values()
    else:
        behaviors = get_standard_behaviors(source)

    package = read_target_node(egg_source(source), target.target)
    default = package['profiles']['default']
    full_name = type_id(source, target.target)
    name = '%s.xml' % full_name
    type_xml = default['types'][name]
    for behavior in behaviors:
        type_xml.params['ctype']['behaviors'].append(behavior)


@handler('gsbehavior', 'uml2fs', 'zcasemanticsgenerator', 'dependency')
def gsbehavior(self, source, target):
    if not source.client.stereotype('dexterity:behavior'):
        return

    package = read_target_node(egg_source(source), target.target)
    default = package['profiles']['default']

    supplier = source.supplier
    full_name = type_id(supplier, target.target)
    name = '%s.xml' % full_name
    type_xml = default['types'][name]

    behavior_class = read_target_node(source.client, target.target)
    behavior = class_full_name(behavior_class)

    type_xml.params['ctype']['behaviors'].append(behavior)
