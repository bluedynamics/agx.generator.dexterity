import os
import uuid
from zope.interface import alsoProvides
from node.ext import python
from node.ext.python.interfaces import IModule
from node.ext.python.utils import Imports
from node.ext.uml.utils import (
    TaggedValues,
    UNSET,
)
from node.ext.uml.interfaces import IClass
from node.ext.directory import (
    MODE_BINARY,
    File,
    Directory,
)
from node.ext.template import XMLTemplate
from node.ext.zcml import (
    ZCMLFile,
    SimpleDirective,
)
from agx.core import (
    handler,
    token,
)
from agx.core.util import (
    read_target_node,
    dotted_path,
)
from agx.generator.pyegg.treesync import ModuleNameChooser
from agx.generator.pyegg.utils import (
    set_copyright,
    sort_classes_in_module,
    class_base_name,
    class_full_name,
    egg_source,
)
from agx.generator.zca.utils import (
    zcml_include_package,
    set_zcml_namespace,
    set_zcml_directive,
    get_zcml,
)
from agx.generator.dexterity.schema import (
    field_properties,
    field_defaults,
    field_types,
)
from agx.generator.dexterity.utils import type_id


class DexterityModuleNameChooser(ModuleNameChooser):

    def __call__(self):
        return self.context.name.lower()


class DexterityBehaviorModuleNameChooser(ModuleNameChooser):

    def __call__(self):
        return self.context.name[1:].lower()


###############################################################################
# schema field related
###############################################################################


def tgv_value(attr, value):
    format = field_properties[attr]
    if format == 'i18n_string':
        value = value.strip('"').strip("'")
        return '_(u"%s")' % value
    elif format == 'string':
        value = value.strip('"').strip("'")
        return "u'%s'" % value
    elif format == 'bool':
        if value in ['True', 'true', 'TRUE', '1']:
            return True
        if value in ['False', 'false', 'FALSE', '0']:
            return False
        return bool(value)
    elif format == 'int':
        return int(value)
    elif format == 'raw':
        return value
    raise RuntimeError(u"Unknown format for '%s': '%s'" % (attr, format))


_marker = object()


def read_tgv(tgv, attribute, stereotype, attrs):
    for attr in attrs:
        value = tgv.direct(attr, stereotype)
        if value is not UNSET:
            attribute.kwargs[attr] = tgv_value(attr, value)
        else:
            default = field_defaults.get(attr, _marker)
            if default is not _marker:
                attribute.kwargs[attr] = default


def field_tgv(tgv, attribute, stereotype):
    attrs = ['title', 'description', 'required', 'readonly', 'default',
             'missing_value']
    read_tgv(tgv, attribute, stereotype, attrs)


def minmaxlen_tgv(tgv, attribute, stereotype):
    field_tgv(tgv, attribute, stereotype)
    attrs = ['min_length', 'max_length']
    read_tgv(tgv, attribute, stereotype, attrs)


def collection_tgv(tgv, attribute, stereotype):
    minmaxlen_tgv(tgv, attribute, stereotype)
    attrs = ['value_type', 'unique']
    read_tgv(tgv, attribute, stereotype, attrs)


def dict_tgv(tgv, attribute, stereotype):
    minmaxlen_tgv(tgv, attribute, stereotype)
    attrs = ['key_type', 'value_type']
    read_tgv(tgv, attribute, stereotype, attrs)


def richtext_tgv(tgv, attribute, stereotype):
    field_tgv(tgv, attribute, stereotype)
    attrs = ['default_mime_type', 'output_mime_type', 'allowed_mime_types']
    read_tgv(tgv, attribute, stereotype, attrs)


def minmax_tgv(tgv, attribute, stereotype):
    field_tgv(tgv, attribute, stereotype)
    attrs = ['min', 'max']
    read_tgv(tgv, attribute, stereotype, attrs)


def object_tgv(tgv, attribute, stereotype):
    field_tgv(tgv, attribute, stereotype)
    attrs = ['schema']
    read_tgv(tgv, attribute, stereotype, attrs)


def field_def_for(group, stereotype):
    field = field_types[group].get(stereotype)
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
    if not attribute: # attribute has been removed
        return
    attribute.value = field_def['factory']
    tgv = TaggedValues(source)
    fetch_tgv(tgv, attribute, field_def['stereotype'])
    imp = Imports(attribute.parent.parent)
    imp.set(field_def['import_from'], [[field_def['import'], None]])
    if field_def['depends']:
        pass # XXX write to setup.py setup_dependencies


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


###############################################################################
# type related
###############################################################################


def getschemaclass(source, target):
    klass = read_target_node(source, target.target)
    module = klass.parent
    schemaclassname = 'I' + klass.classname
    found = module.classes(schemaclassname)
    return found[0]


@handler('createschemaclass', 'uml2fs', 'hierarchygenerator',
         'contenttype', order=99)
def createschemaclass(self, source, target):
    """create the schema interface class on the fly.
    """
    klass = read_target_node(source, target.target)
    module = klass.parent
    schemaclassname = 'I' + klass.classname
    found = module.classes(schemaclassname)
    if found:
        schemaclass = found[0]
    else:
        schemaclass = python.Class(classname=schemaclassname)
        schemaclass.__name__ = schemaclass.uuid
        module.insertbefore(schemaclass, klass)
    # expose it in __init__
    imp = Imports(module.parent['__init__.py'])
    imp.set(class_base_name(schemaclass), [[schemaclassname, None]])
    # mark the content class for deletion if not needed
    createit = TaggedValues(source).direct('create_contentclass',
                                           'plone:content_type',
                                           False)
    if not (createit or klass.functions()):
        token(str(klass.uuid), True, dont_generate=True)


@handler('schemaclass_move_attribs', 'uml2fs', 'dxcleanupgenerator',
         'contenttype', order=99)
def schemaclass_move_attribs(self, source, target):
    """Move the content class attribute to the schema class.
    """
    klass = read_target_node(source, target.target)
    module = klass.parent
    schemaclassname = 'I' + klass.classname
    found = module.classes(schemaclassname)
    if found:
        schemaclass = found[0]
    else:
        return
    # transfer the attributes into the schema class
    for att in klass.attributes():
        # move only schema attributes
        if att.value == 'None' or att.value.startswith('schema.'):
            klass.detach(att.__name__)
            if not schemaclass.attributes(att.targets[0]):
                schemaclass.insertlast(att)
            else:
                del att


@handler('purgecontentclasses', 'uml2fs', 'dxcleanupgenerator',
         'contenttype', order=160)
def purgecontentclasses(self, source, target):
    """remove the content classes that should not be generated.
    """
    klass = read_target_node(source, target.target)
    module = klass.parent
    if token(str(klass.uuid), False, dont_generate=False).dont_generate:
        module.detach(klass.__name__)
        # remove the imports
        init = module.parent['__init__.py']
        imps = init.imports()
        impname = [klass.classname, None]
        for imp in imps:
            if impname in imp.names:
                if len(imp.names) > 1:
                    # if more names are in the imp delete the name
                    imp.names=[n for n in imp.names if n != impname]
                else:
                    # delete the whole import
                    init.detach(imp.__name__)


@handler('grokforcontentclass', 'uml2fs', 'connectorgenerator',
         'contenttype', order=110)
def grokforcontentclass(self, source, target):
    """create the schema interface class on the fly.
    """
    klass = read_target_node(source, target.target)
    module = klass.parent
    schemaclassname = 'I' + klass.classname
    # add the schemaclass to realizes, the rest is done by the
    # zcagenerator::zcarealize_finalize handler
    impltok = token(str(klass.uuid), True, realizes=[], provides=None)
    impltok.realizes.insert(0, {'name': schemaclassname})

    require = "grok.name('%s')" % dotted_path(source)
    require_exists = False

    for block in klass.blocks():
        for line in block.lines:
            if line == require:
                require_exists = True

    block = python.Block()
    block.__name__ = str(uuid.uuid4())

    if not require_exists:
        block.lines.append(require)

    if block.lines:
        klass.insertfirst(block)


@handler('dxcomposition', 'uml2fs', 'zcasemanticsgenerator',
         'association', order=100)
def dxcomposition(self, source, target):
    # get container. ownedEnds len should always be 2
    container = source.ownedEnds[0].type
    if container.stereotype('plone:content_type'):
        klass = read_target_node(container, target.target)
        token(str(klass.uuid), True, folderish=True)
        bases = [b for b in klass.bases if b != 'dexterity.Item']
        if 'dexterity.Container' not in bases:
            klass.bases = ['dexterity.Container'] + bases


@handler('dxitem', 'uml2fs', 'zcasemanticsgenerator', 'contenttype', order=99)
def dxitem(self, source, target):
    schema = getschemaclass(source,target)
    klass = read_target_node(source, target.target)
    module = schema.parent
    bases = [b for b in klass.bases if b != 'dexterity.Container']
    if 'dexterity.Item' not in bases:
        klass.bases = ['dexterity.Item'] + bases


@handler('typeview', 'uml2fs', 'zcagenerator', 'contenttype', order=100)
def typeview(self, source, target):
    schema = getschemaclass(source,target)
    klass = read_target_node(source, target.target)
    module = schema.parent
    if IModule.providedBy(module):
        directory = module.parent
    else:
        directory = module
    nsmap = {
        None: 'http://namespaces.zope.org/zope',
        'plone': 'http://namespaces.plone.org/plone',
        'grok': 'http://namespaces.zope.org/grok',
    }
    zcmlfile = get_zcml(directory, 'configure.zcml', nsmap=nsmap)

    # include grok:grok directive if not set yet
    set_zcml_directive(directory, 'configure.zcml',
                       'grok:grok', 'package', '.')

    classname = '%sView' % klass.classname
    if module.classes(classname):
        view = module.classes(classname)[0]
    else:
        view = python.Class()
        module[uuid.uuid4()] = view
    view.classname = classname

    if not 'dexterity.DisplayForm' in view.bases:
        view.bases.append('dexterity.DisplayForm')

    context = "grok.context(%s)" % schema.classname
    require = "grok.require('zope2.View')"

    context_exists = False
    require_exists = False

    for block in view.blocks():
        for line in block.lines:
            if line == context:
                context_exists = True
            if line == require:
                require_exists = True

    block = python.Block()
    block.__name__ = str(uuid.uuid4())

    if not context_exists:
        block.lines.append(context)
    if not require_exists:
        block.lines.append(require)

    if block.lines:
        view.insertfirst(block)

    template = False
    for attr in view.attributes():
        if 'template' in attr.targets:
            template = attr
            break

    if not template:
        template = python.Attribute()
        template.targets = ['template']
        view[str(uuid.uuid4())] = template

    template.value = "PageTemplate('templates/%s.pt')" \
        % klass.classname.lower()

    imp = Imports(module)
    imp.set('plone.directives', [['dexterity', None]])
    imp.set('five', [['grok', None]])
    imp.set('grokcore.view.components', [['PageTemplate', None]])

    directory = module.parent
    template_name = '%s.pt' % klass.classname.lower()
    template = 'templates/%s' % template_name
    if not 'templates' in directory:
        directory['templates'] = Directory()

    templates = directory['templates']
    templates.factories['.pt'] = XMLTemplate

    if template_name not in templates:
        pt = templates[template_name] = XMLTemplate()
        pt.template = 'agx.generator.dexterity:templates/displayform.pt'


def templatepath(name):
    return os.path.join(os.path.dirname(__file__), 'templates/%s' % name)


@handler('typeicon', 'uml2fs', 'plonegenerator', 'contenttype', order=100)
def typeicon(self, source, target):
    egg = egg_source(source)
    package = read_target_node(egg, target.target)
    resources = package['resources']
    icon = '%s_icon.png' % source.name.lower()
    klass = read_target_node(source,target.target)
    folderish = token(str(klass.uuid), True, folderish=False).folderish
    if not icon in resources:
        default = package['profiles']['default']
        type_name = type_id(source, target.target)
        name = '%s.xml' % type_name

        fti = default['types'][name]
        if folderish:
            path = templatepath('folder_icon.png')
        else:
            path = templatepath('document_icon.png')

        file = resources[icon] = File()
        file.mode = MODE_BINARY
        with open(path) as template:
            file.data = template.read()


class IDexterityType(IClass):
    """Marker.
    """


@handler('schemaumlclass', 'xmi2uml', 'finalizegenerator', 'class')
def schemaumlclass(self, source, target):
    class_ = read_target_node(source, target.target)
    if class_.stereotype('plone:content_type'):
#        class_.__name__ = 'I%s' % class_.name
        alsoProvides(class_, IDexterityType)


@handler('schemaclass', 'uml2fs', 'zcagenerator', 'contenttype', order=110)
def schemaclass(self, source, target):
    schema = getschemaclass(source,target)
    klass = read_target_node(source, target.target)
    module = schema.parent

    view = module.classes('%sView' % klass.classname)[0]
    tok = token(str(view.uuid), True, depends_on=set())
    tok.depends_on.add(schema)

    if not 'form.Schema' in schema.bases:
        schema.bases.append('form.Schema')

    egg = egg_source(source)

    imp = Imports(schema.parent)
    imp.set(egg.name, [['_', None]])
    imp.set('plone.directives', [['form', None]])


@handler('typemodulesorter', 'uml2fs', 'zcasemanticsgenerator', 
         'contenttype', order=100)
def dependencysorter(self, source, target):
    schema = getschemaclass(source,target)
    module = schema.parent
    sort_classes_in_module(module)


@handler('dxpackagedependencies', 'uml2fs', 'semanticsgenerator', 'pythonegg')
def dxpackagedependencies(self, source, target):
    # check whether dexterity profile exists in model, otherwise skip.
    if not source.root.get('dexterity'):
        return
    setup = target.target['setup.py']
    setup.params['setup_dependencies'].append('plone.app.dexterity')


###############################################################################
# behavior related
###############################################################################


class IDexterityBehavior(IClass):
    """Marker.
    """


@handler('behaviorumlclass', 'xmi2uml', 'finalizegenerator', 'class')
def behaviorumlclass(self, source, target):
    class_ = read_target_node(source, target.target)
    if class_.stereotype('dexterity:behavior'):
        class_.__name__ = 'I%s' % class_.name
        alsoProvides(class_, IDexterityBehavior)


@handler('behaviorschema', 'uml2fs', 'zcagenerator', 'dxbehavior', order=100)
def behaviorschema(self, source, target):
    schema = read_target_node(source, target.target)
    module = schema.parent

    # check whether this behavior has schema attributes
    if not 'form.Schema' in schema.bases:
        schema.bases.append('form.Schema')

    alsoprovides = "alsoProvides(%s, form.IFormFieldProvider)" \
        % schema.classname

    alsoprovides_exists = False

    for block in module.blocks():
        for line in block.lines:
            if line == alsoprovides:
                alsoprovides_exists = True

    block = python.Block()
    block.__name__ = str(uuid.uuid4())

    if not alsoprovides_exists:
        block.lines.append(alsoprovides)

    if block.lines:
        module.insertafter(block, schema)

    egg = egg_source(source)

    imp = Imports(schema.parent)
    imp.set(egg.name, [['_', None]])
    imp.set('plone.directives', [['form', None]])
    imp.set('zope.interface', [['alsoProvides', None]])


@handler('behavioradapter', 'uml2fs', 'zcagenerator', 'dxbehavior', order=110)
def behavioradapter(self, source, target):
    schema = read_target_node(source, target.target)
    module = schema.parent

    adaptername = schema.classname[1:]
    if module.classes(adaptername):
        adapter = module.classes(adaptername)[0]
    else:
        adapter = python.Class()
        module[uuid.uuid4()] = adapter
    adapter.classname = adaptername

    implements = "implements(%s)" % schema.classname
    implements_exists = False
    for block in adapter.blocks():
        for line in block.lines:
            if line == implements:
                implements_exists = True

    block = python.Block()
    block.__name__ = str(uuid.uuid4())

    if not implements_exists:
        block.lines.append(implements)

    if block.lines:
        adapter.insertfirst(block)

    # ``__init__ only created once``
    # XXX: check if signature changed and raise error
    if not adapter.functions('__init__'):
        init = python.Function(functionname='__init__')
        init.args.append('context')
        block = init[str(uuid.uuid4())] = python.Block()
        block.lines.append('self.context = context')
        adapter[str(uuid.uuid4())] = init

    imp = Imports(module)
    imp.set('zope.interface', [['implements', None]])

    # read or create configure.zcml
    package = module.parent
    if 'configure.zcml' in package:
        configure = package['configure.zcml']
    else:
        path = package.path
        path.append('configure.zcml')
        fullpath = os.path.join(*path)
        configure = ZCMLFile(fullpath)
        configure.nsmap['plone'] = 'http://namespaces.plone.org/plone'
        configure.nsmap['grok'] = 'http://namespaces.zope.org/grok'
        package['configure.zcml'] = configure

    provides = '.%s.%s' % (module.modulename, schema.classname)
    factory = '.%s.%s' % (module.modulename, adapter.classname)

    # XXX: maybe more filters
    if not configure.filter(tag='plone:behavior',
                            attr='factory',
                            value=factory):
        behavior = SimpleDirective(name='plone:behavior', parent=configure)
        behavior.attrs['title'] = adapter.classname
        # XXX: stereotype tgv
        behavior.attrs['description'] = adapter.classname
        behavior.attrs['provides'] = provides
        behavior.attrs['factory'] = factory
