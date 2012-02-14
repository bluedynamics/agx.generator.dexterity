from node.ext.directory import Directory
from node.ext.template import DTMLTemplate
from agx.core import handler
from agx.core.util import read_target_node
from agx.generator.pyegg.utils import (
    egg_source,
    class_base_name,
)


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
    class_ = read_target_node(source, target.target)
    if source.parent.stereotype('pyegg:pymodule'):
        full_name = '%s.%s' % (class_base_name(class_),
                               class_.classname.lower())
    else:
        full_name = class_base_name(class_)
    
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
    
    content_icon = '++resource++%s/%s_icon.png' % (egg.name, source.name)
    
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
    type.params['ctype']['filter_content_types'] = 'True'
    type.params['ctype']['allowed_content_types'] = list()
    
    # dexterity specific
    schema = '%s.I%s' % (class_base_name(class_), class_.classname)
    
    # XXX: check whether container or leaf
    klass = 'plone.dexterity.content.Item'
    
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
        'condition_expr': 'not:object/@@plone_lock_info/is_locked_for_current_user',
        'url_expr': 'string:${object_url}/edit',
        'visible': 'True',
        'permissions': ['Modify portal content'],
    })
    type.params['ctype']['actions'].append({
        'action_id': 'view',
        'title': 'View',
        'category': 'object',
        'condition_expr': 'python:1',
        'url_expr': 'string:${object_url}/view',
        'visible': 'True',
        'permissions': ['View'],
    })


@handler('gsdynamicview', 'uml2fs', 'semanticsgenerator',
         'dependency', order=100)
def gsdynamicview(self, source, target):
    """Add view method to FTI's of all dependent content types.
    """
    if not source.supplier.stereotype('plone:content_type') \
      or not source.client.stereotype('plone:dynamic_view'):
        return
    
    content_type = source.supplier
    package = read_target_node(egg_source(content_type), target.target)
    default = package['profiles']['default']
    
    class_ = read_target_node(content_type, target.target)
    if source.supplier.parent.stereotype('pyegg:pymodule'):
        full_name = '%s.%s' % (class_base_name(class_),
                               class_.classname.lower())
    else:
        full_name = class_base_name(class_)
    
    name = '%s.xml' % full_name
    type_xml = default['types'][name]
    type_xml.params['ctype']['view_methods'].append(source.client.name)