# Dexterity standard behaviors related to
# http://plone.org/products/dexterity/documentation/manual/developer-manual/reference/standard-behaviors
#
# key:
#     stereotype name
#
# value:
#     behavior interface
standard_behaviors = {
    'dexterity:behavior_basic':
        'plone.app.dexterity.behaviors.metadata.IBasic',
    'dexterity:behavior_categorization':
        'plone.app.dexterity.behaviors.metadata.ICategorization',
    'dexterity:behavior_publication':
        'plone.app.dexterity.behaviors.metadata.IPublication',
    'dexterity:behavior_ownership':
        'plone.app.dexterity.behaviors.metadata.IOwnership',
    'dexterity:behavior_dublincore':
        'plone.app.dexterity.behaviors.metadata.IDublinCore',
    'dexterity:behavior_namefromtitle':
        'plone.app.content.interfaces.INameFromTitle',
    'dexterity:behavior_relateditems':
        'plone.app.dexterity.behaviors.metadata.IRelatedItems',
}


# Schema field properties related to
# http://plone.org/products/dexterity/documentation/manual/developer-manual/reference/fields
#
# i18n_string:
#     convert given value to _(u'VALUE')
#
# string:
#     convert given value to u'VALUE'
#
# bool:
#     bool evaluation of given value
#
# int:
#     cast value to int
#
# raw:
#     no value manipulation
#
field_properties = {
    # zope.schema.interfaces.IField
    'title': 'i18n_string',
    'description': 'i18n_string',
    'required': 'bool',
    'readonly': 'bool',
    'default': 'raw',
    'missing_value': 'raw',

    # zope.schema.interfaces.IMinMaxLen
    'min_length': 'int',
    'max_length': 'int',

    # zope.schema.interfaces.ICollection
    'value_type': 'raw',
    'unique': 'bool',

    # zope.schema.interfaces.IDict
    'key_type': 'raw',
    'value_type': 'raw',

    # plone.app.textfield.interfaces.IRichText
    'default_mime_type': 'string',
    'output_mime_type': 'string',
    'allowed_mime_types': 'raw',

    # zope.schema.interfaces.IMinMax
    'min': 'raw',
    'max': 'raw',

    # zope.schema.interfaces.IObject
    'schema': 'string',
}


# default values
field_defaults = {
    'required': False,
}


# Schema field types related to
# http://plone.org/products/dexterity/documentation/manual/developer-manual/reference/fields
#
# must:
#     factory -> i.e. 'schema.Tuple'
#
# may:
#     import -> What to import
#     import_from -> From where to import
#     depends -> i.e. 'plone.namedfile'
#
# defaults:
#     import -> 'schema'
#     import_from -> 'zope'
#
field_types = {
    # zope.schema.interfaces.ICollection related fields
    'collection': {
        'dexterity:Tuple': {
            'factory': 'schema.Tuple',
        },
        'dexterity:List': {
            'factory': 'schema.List',
        },
        'dexterity:Set': {
            'factory': 'schema.Set',
        },
        'dexterity:Frozenset': {
            'factory': 'schema.FrozenSet',
        },
    },

    # zope.schema.interfaces.IMinMaxLen related fields
    'minmaxlen': {
        'dexterity:SourceText': {
            'factory': 'schema.SourceText',
        },
        'dexterity:Bytes': {
            'factory': 'schema.Bytes',
        },
        'dexterity:ASCII': {
            'factory': 'schema.ASCII',
        },
        'dexterity:DottedName': {
            'factory': 'schema.DottedName',
        },
        'dexterity:BytesLine': {
            'factory': 'schema.BytesLine',
        },
        'dexterity:URI': {
            'factory': 'schema.URI',
        },
        'dexterity:ASCIILine': {
            'factory': 'schema.ASCIILine',
        },
        'dexterity:Id': {
            'factory': 'schema.Id',
        },
        'dexterity:Text': {
            'factory': 'schema.Text',
        },
        'dexterity:TextLine': {
            'factory': 'schema.TextLine',
        },
        'dexterity:Password': {
            'factory': 'schema.Password',
        },
    },

    # zope.schema.interfaces.IDict related fields
    'dict': {
        'dexterity:Dict': {
            'factory': 'schema.Dict',
        },
    },

    # zope.schema.interfaces.IField related fields
    'field': {
        'dexterity:Bool': {
            'factory': 'schema.Bool',
        },
        'dexterity:InterfaceField': {
            'factory': 'schema.InterfaceField',
        },
        'dexterity:NamedFile': {
            'factory': 'NamedFile',
            'import': 'NamedFile',
            'import_from': 'plone.namedfile.field',
            'depends': 'plone.namedfile',
        },
        'dexterity:Relation': {
            'factory': 'Relation',
            'import': 'Relation',
            'import_from': 'z3c.relationfield.schema',
            'depends': 'z3c.relationfield',
        },
        'dexterity:NamedImage': {
            'factory': 'NamedImage',
            'import': 'NamedImage',
            'import_from': 'plone.namedfile.field',
            'depends': 'plone.namedfile',
        },
        'dexterity:NamedBlobFile': {
            'factory': 'NamedBlobFile',
            'import': 'NamedBlobFile',
            'import_from': 'plone.namedfile.field',
            'depends': 'plone.namedfile',
        },
        'dexterity:NamedBlobImage': {
            'factory': 'NamedBlobFile',
            'import': 'NamedBlobFile',
            'import_from': 'plone.namedfile.field',
            'depends': 'plone.namedfile',
        },
    },

    # plone.app.textfield.interfaces.IRichText related fields
    'richtext': {
        'dexterity:RichText': {
            'factory': 'RichText',
            'import': 'RichText',
            'import_from': 'plone.app.textfield',
            'depends': 'plone.app.textfield',
        },
    },

    # zope.schema.interfaces.IMinMax related fields
    'minmax': {
        'dexterity:Int': {
            'factory': 'schema.Int',
        },
        'dexterity:Float': {
            'factory': 'schema.Float',
        },
        'dexterity:Date': {
            'factory': 'schema.Date',
        },
        'dexterity:Datetime': {
            'factory': 'schema.Datetime',
        },
        'dexterity:Timedelta': {
            'factory': 'schema.Timedelta',
        },
        'dexterity:Decimal': {
            'factory': 'schema.Decimal',
        },
    },

    # zope.schema.interfaces.IObject related fields
    'object': {
        'dexterity:Object': {
            'factory': 'schema.Object',
        },
    },
}
