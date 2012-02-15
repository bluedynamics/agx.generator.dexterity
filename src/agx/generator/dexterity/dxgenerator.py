import uuid
from zope.interface import alsoProvides
from node.ext import python
from node.ext.python.utils import Imports
from node.ext.uml.utils import (
    TaggedValues,
    UNSET,
)
from node.ext.uml.interfaces import IClass
from node.ext.directory import Directory
from node.ext.zcml import (
    ZCMLFile,
    SimpleDirective,
)
from agx.core import (
    handler,
    token,
)
from agx.core.util import read_target_node
from agx.generator.pyegg.treesync import ModuleNameChooser
from agx.generator.pyegg.utils import (
    set_copyright,
    sort_classes_in_module,
)
from agx.generator.zca.utils import zcml_include_package
from agx.generator.dexterity.schema import mapping


class IDexterityType(IClass):
    """Marker.
    """


class DexterityModuleNameChooser(ModuleNameChooser):
    
    def __call__(self):
        return self.context.name[1:].lower()


def read_tgv(tgv, attribute, stereotype, attrs):
    for attr in attrs:
        value = tgv.direct(attr, stereotype)
        if value is not UNSET:
            attribute.kwargs[attr] = value


def field_tgv(tgv, attribute, stereotype):
    """
    - title: String
    - description: String
    - required: Bool
    - readonly: Bool
    - default: String
    - missing_value: String
    """
    attrs = ['title', 'description', 'required', 'readonly', 'default',
             'missing_value']
    read_tgv(tgv, attribute, stereotype, attrs)


def minmaxlen_tgv(tgv, attribute, stereotype):
    """
    - min_length: Int
    - max_length: Int
    """
    field_tgv(tgv, attribute, stereotype)
    attrs = ['min_length', 'max_length']
    read_tgv(tgv, attribute, stereotype, attrs)


def collection_tgv(tgv, attribute, stereotype):
    """
    - value_type: String
    - unique: Bool
    """
    minmaxlen_tgv(tgv, attribute, stereotype)
    attrs = ['value_type', 'unique']
    read_tgv(tgv, attribute, stereotype, attrs)


def dict_tgv(tgv, attribute, stereotype):
    """
    - key_type: String
    - value_type: String
    """
    minmaxlen_tgv(tgv, attribute, stereotype)
    attrs = ['key_type', 'value_type']
    read_tgv(tgv, attribute, stereotype, attrs)


def richtext_tgv(tgv, attribute, stereotype):
    """
    - default_mime_type: String
    - output_mime_type: String
    - allowed_mime_types: String
    """
    field_tgv(tgv, attribute, stereotype)
    attrs = ['default_mime_type', 'output_mime_type', 'allowed_mime_types']
    read_tgv(tgv, attribute, stereotype, attrs)


def minmax_tgv(tgv, attribute, stereotype):
    """
    - min: String
    - max: String
    """
    field_tgv(tgv, attribute, stereotype)
    attrs = ['min', 'max']
    read_tgv(tgv, attribute, stereotype, attrs)


def object_tgv(tgv, attribute, stereotype):
    """
    - schema: String
    """
    field_tgv(tgv, attribute, stereotype)
    attrs = ['schema']
    read_tgv(tgv, attribute, stereotype, attrs)


def field_def_for(group, stereotype):
    field = mapping[group].get(stereotype)
    if not field:
        return None
    return {
        'factory': field['factory'],
        'import': field.get('import', 'schema'),
        'import_from': field.get('import_from', 'zope'),
        'depends':  field.get('depends'),
        'stereotype': stereotype,
    }


def lookup_field_def(source, group):
    field = None
    for st in source.stereotypes:
        field = field_def_for(group, st.name)
        if field:
            break
    if not field:
        raise RuntimeError(u"Field definition not found for %s" % source.name)
    return field


def transform_attribute(source, target, group, fetch_tgv):
    field_def = lookup_field_def(source, group)
    attribute = read_target_node(source, target.target)
    attribute.value = field_def['factory']
    tgv = TaggedValues(source)
    fetch_tgv(tgv, attribute, field_def['stereotype'])
    imp = Imports(attribute.parent.parent)
    imp.set(field_def['import_from'], [[field_def['import'], None]])


@handler('dxcollection', 'uml2fs', 'zcagenerator', 'dxcollection', order=100)
def dxcollection(self, source, target):
    transform_attribute(source, target, 'collection', collection_tgv)


@handler('dxminmaxlen', 'uml2fs', 'zcagenerator', 'dxminmaxlen', order=100)
def dxminmaxlen(self, source, target):
    transform_attribute(source, target, 'minmaxlen', minmaxlen_tgv)


@handler('dxdict', 'uml2fs', 'zcagenerator', 'dxdict', order=100)
def dxdict(self, source, target):
    transform_attribute(source, target, 'dict', dict_tgv)


@handler('dxfield', 'uml2fs', 'zcagenerator', 'dxfield', order=100)
def dxfield(self, source, target):
    transform_attribute(source, target, 'field', field_tgv)


@handler('dxrichtext', 'uml2fs', 'zcagenerator', 'dxrichtext', order=100)
def dxrichtext(self, source, target):
    transform_attribute(source, target, 'richtext', richtext_tgv)


@handler('dxminmax', 'uml2fs', 'zcagenerator', 'dxminmax', order=100)
def dxminmax(self, source, target):
    transform_attribute(source, target, 'minmax', minmax_tgv)


@handler('dxobject', 'uml2fs', 'zcagenerator', 'dxobject', order=100)
def dxobject(self, source, target):
    transform_attribute(source, target, 'object', object_tgv)


@handler('typeview', 'uml2fs', 'zcagenerator', 'contenttype', order=100)
def typeview(self, source, target):
    schema = read_target_node(source, target.target)
    module = schema.parent
    
    classname = '%sView' % schema.classname[1:]
    if module.classes(classname):
        view = module.classes(classname)[0]
    else:
        view = python.Class()
        module[uuid.uuid4()] = view
    view.classname = classname
    
    if not 'BrowserPage' in view.bases:
        view.bases.append('BrowserPage')
    
    imp = Imports(module)
    imp.set('Products.Five', [['BrowserPage', None]])
    
    directory = module.parent
    if not 'configure.zcml' in directory:
        snmap = {
            None: 'http://namespaces.zope.org/zope',
            'browser': 'http://namespaces.zope.org/browser',
        }
        directory['configure.zcml'] = ZCMLFile(nsmap=snmap)
    zcml = directory['configure.zcml']
    
    iface = '.%s.%s' % (module.modulename, schema.classname)
    viewclass = '.%s.%s' % (module.modulename, schema.classname[1:])
    
    template = 'templates/%s.pt' % schema.classname[1:].lower()
    if not 'templates' in directory:
        directory['templates'] = Directory()
    
    directives = zcml.filter(tag='browser:page', attr='name', value='view')
    exists = None
    if directives:
        for directive in directives:
            if directive.attrs['class'] == viewclass \
              and directive.attrs['for'] == iface:
                exists = directive
                break
    if not exists:
        directive = SimpleDirective(name='browser:page', parent = zcml)
    else:
        directive = exists
    
    directive.attrs['name'] = 'view'
    directive.attrs['for'] = iface
    directive.attrs['class'] = viewclass
    directive.attrs['template'] = template
    directive.attrs['permission'] = 'zope2.View'
    # XXX: directive.attrs['layer'] = 'foo'
    
    if not source.parent.stereotype('pyegg:pyegg'):
        zcml_include_package(directory)


@handler('schemaumlclass', 'xmi2uml', 'finalizegenerator', 'class')
def schemaumlclass(self, source, target):
    class_ = read_target_node(source, target.target)
    if class_.stereotype('plone:content_type'):
        class_.__name__ = 'I%s' % class_.name
    alsoProvides(class_, IDexterityType)


@handler('schemaclass', 'uml2fs', 'zcagenerator', 'contenttype', order=110)
def schemaclass(self, source, target):
    schema = read_target_node(source, target.target)
    module = schema.parent
    
    view = module.classes('%sView' % schema.classname[1:])[0]
    tok = token(str(view.uuid), True, depends_on=set())
    tok.depends_on.add(schema)
    
    if not 'form.Schema' in schema.bases:
        schema.bases.append('form.Schema')
    
    imp = Imports(schema.parent)
    imp.set('plone.directives', [['form', None]])


@handler('typemodulesorter', 'uml2fs', 'zcasemanticsgenerator', 
         'contenttype', order=100)
def dependencysorter(self, source, target):
    schema = read_target_node(source, target.target)
    module = schema.parent
    sort_classes_in_module(module)