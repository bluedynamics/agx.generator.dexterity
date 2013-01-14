from node.ext.uml.interfaces import IAssociation
from agx.core import (
    Scope,
    registerScope,
)


class CollectionScope(Scope):

    def __call__(self, node):
        return node.stereotype('dexterity:Tuple') \
            or node.stereotype('dexterity:List') \
            or node.stereotype('dexterity:Set') \
            or node.stereotype('dexterity:Frozenset')
    

class MinMaxLenScope(Scope):

    def __call__(self, node):
        return node.stereotype('dexterity:SourceText') \
            or node.stereotype('dexterity:Bytes') \
            or node.stereotype('dexterity:ASCII') \
            or node.stereotype('dexterity:DottedName') \
            or node.stereotype('dexterity:BytesLine') \
            or node.stereotype('dexterity:URI') \
            or node.stereotype('dexterity:ASCIILine') \
            or node.stereotype('dexterity:Id') \
            or node.stereotype('dexterity:Text') \
            or node.stereotype('dexterity:TextLine') \
            or node.stereotype('dexterity:Password')


class DictScope(Scope):

    def __call__(self, node):
        return node.stereotype('dexterity:Dict')


class FieldScope(Scope):

    def __call__(self, node):
        return node.stereotype('dexterity:Bool') \
            or node.stereotype('dexterity:InterfaceField') \
            or node.stereotype('dexterity:NamedFile') \
            or node.stereotype('dexterity:Relation') \
            or node.stereotype('dexterity:NamedImage') \
            or node.stereotype('dexterity:NamedBlobFile') \
            or node.stereotype('dexterity:NamedBlobImage')


class RichTextScope(Scope):

    def __call__(self, node):
        return node.stereotype('dexterity:RichText')


class MinMaxScope(Scope):

    def __call__(self, node):
        return node.stereotype('dexterity:Int') \
            or node.stereotype('dexterity:Float') \
            or node.stereotype('dexterity:Date') \
            or node.stereotype('dexterity:Datetime') \
            or node.stereotype('dexterity:Timedelta') \
            or node.stereotype('dexterity:Decimal')


class ObjectScope(Scope):

    def __call__(self, node):
        return node.stereotype('dexterity:Object')


class BehaviorScope(Scope):

    def __call__(self, node):
        return node.stereotype('dexterity:behavior')


registerScope('association', 'uml2fs', [IAssociation], Scope)
registerScope('dxcollection', 'uml2fs', None, CollectionScope)
registerScope('dxminmaxlen', 'uml2fs', None, MinMaxLenScope)
registerScope('dxdict', 'uml2fs', None, DictScope)
registerScope('dxfield', 'uml2fs', None, FieldScope)
registerScope('dxrichtext', 'uml2fs', None, RichTextScope)
registerScope('dxminmax', 'uml2fs', None, MinMaxScope)
registerScope('dxobject', 'uml2fs', None, ObjectScope)
registerScope('dxbehavior', 'uml2fs', None, BehaviorScope)
