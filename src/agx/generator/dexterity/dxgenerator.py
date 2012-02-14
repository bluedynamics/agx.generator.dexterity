from agx.core import handler


@handler('dxcollection', 'uml2fs', 'zcagenerator', 'dxcollection', order=100)
def dxcollection(self, source, target):
    print source


@handler('dxminmaxlen', 'uml2fs', 'zcagenerator', 'dxminmaxlen', order=100)
def dxminmaxlen(self, source, target):
    print source


@handler('dxdict', 'uml2fs', 'zcagenerator', 'dxdict', order=100)
def dxdict(self, source, target):
    print source


@handler('dxfield', 'uml2fs', 'zcagenerator', 'dxfield', order=100)
def dxfield(self, source, target):
    print source


@handler('dxrichtext', 'uml2fs', 'zcagenerator', 'dxrichtext', order=100)
def dxrichtext(self, source, target):
    print source


@handler('dxminmax', 'uml2fs', 'zcagenerator', 'dxminmax', order=100)
def dxminmax(self, source, target):
    print source


@handler('dxobject', 'uml2fs', 'zcagenerator', 'dxobject', order=100)
def dxobject(self, source, target):
    print source