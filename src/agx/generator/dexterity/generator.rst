Test agx.generator.dexterity
============================

Setup configuration and emulate main routine::

    >>> from zope.configuration.xmlconfig import XMLConfig

    >>> import agx.core
    >>> XMLConfig('configure.zcml', agx.core)()

    >>> from agx.core.main import parse_options

    >>> import os
    >>> modelpath = os.path.join(datadir, 'agx.generator.dexterity-sample.uml')

    >>> import pkg_resources
    >>> subpath = 'profiles/pyegg.profile.uml'
    >>> eggprofilepath = \
    ...     pkg_resources.resource_filename('agx.generator.pyegg', subpath)

    >>> subpath = 'profiles/zca.profile.uml'
    >>> zcaprofilepath = \
    ...     pkg_resources.resource_filename('agx.generator.zca', subpath)

    >>> subpath = 'profiles/plone.profile.uml'
    >>> ploneprofilepath = \
    ...     pkg_resources.resource_filename('agx.generator.plone', subpath)

    >>> subpath = 'profiles/dexterity.profile.uml'
    >>> dexterityprofilepath = \
    ...     pkg_resources.resource_filename('agx.generator.dexterity', subpath)

    >>> subpath = 'profiles/buildout.profile.uml'
    >>> buildoutprofilepath = \
    ...     pkg_resources.resource_filename('agx.generator.buildout', subpath)

    >>> modelpaths = [modelpath, eggprofilepath, zcaprofilepath,
    ...     ploneprofilepath, dexterityprofilepath, buildoutprofilepath]

    >>> outdir = os.path.join(datadir, 'agx.generator.dexterity-sample')
    >>> controller = agx.core.Controller()
    >>> target = controller(modelpaths, outdir)
    >>> target
    <Directory object '/.../agx.generator.dexterity/src/agx/generator/dexterity/testing/data/agx.generator.dexterity-sample' at ...>
