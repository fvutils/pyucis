# src/pyucis/ucis_dom.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:d11d37fcdc1395ea87e7588f023f6a599db761c8
# Generated 2019-12-22 14:45:14.915818 by PyXB version 1.2.6 using Python 3.6.8.final.0
# Namespace UCIS

from __future__ import unicode_literals
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import io
import pyxb.utils.utility
import pyxb.utils.domutils
import sys
import pyxb.utils.six as _six
# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:92c7c91e-24f3-11ea-97fc-80c16e228da2')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.6'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

# A holder for module-level binding classes so we can access them from
# inside class definitions where property names may conflict.
_module_typeBindings = pyxb.utils.utility.Object()

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.NamespaceForURI('UCIS', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.

    @param xml_text An XML document.  This should be data (Python 2
    str or Python 3 bytes), or a text (Python 2 unicode or Python 3
    str) in the L{pyxb._InputEncoding} encoding.

    @keyword default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utils.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement, default_namespace=default_namespace)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    xmld = xml_text
    if isinstance(xmld, _six.text_type):
        xmld = xmld.encode(pyxb._InputEncoding)
    saxer.parse(io.BytesIO(xmld))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, default_namespace)


# Atomic simple type: [anonymous]
class STD_ANON (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 17, 1)
    _Documentation = None
STD_ANON._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON, enum_prefix=None)
STD_ANON.int = STD_ANON._CF_enumeration.addEnumeration(unicode_value='int', tag='int')
STD_ANON.float = STD_ANON._CF_enumeration.addEnumeration(unicode_value='float', tag='float')
STD_ANON.double = STD_ANON._CF_enumeration.addEnumeration(unicode_value='double', tag='double')
STD_ANON.str = STD_ANON._CF_enumeration.addEnumeration(unicode_value='str', tag='str')
STD_ANON.bits = STD_ANON._CF_enumeration.addEnumeration(unicode_value='bits', tag='bits')
STD_ANON.int64 = STD_ANON._CF_enumeration.addEnumeration(unicode_value='int64', tag='int64')
STD_ANON._InitializeFacetMap(STD_ANON._CF_enumeration)
_module_typeBindings.STD_ANON = STD_ANON

# Complex type {UCIS}NAME_VALUE with content type ELEMENT_ONLY
class NAME_VALUE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}NAME_VALUE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'NAME_VALUE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 7, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}name uses Python identifier name
    __name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'name'), 'name', '__UCIS_NAME_VALUE_UCISname', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 9, 1), )

    
    name = property(__name.value, __name.set, None, None)

    
    # Element {UCIS}value uses Python identifier value_
    __value = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'value'), 'value_', '__UCIS_NAME_VALUE_UCISvalue', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 10, 1), )

    
    value_ = property(__value.value, __value.set, None, None)

    _ElementMap.update({
        __name.name() : __name,
        __value.name() : __value
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.NAME_VALUE = NAME_VALUE
Namespace.addCategoryObject('typeBinding', 'NAME_VALUE', NAME_VALUE)


# Complex type {UCIS}BIN_CONTENTS with content type ELEMENT_ONLY
class BIN_CONTENTS (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}BIN_CONTENTS with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'BIN_CONTENTS')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 33, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}historyNodeId uses Python identifier historyNodeId
    __historyNodeId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'historyNodeId'), 'historyNodeId', '__UCIS_BIN_CONTENTS_UCIShistoryNodeId', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 35, 1), )

    
    historyNodeId = property(__historyNodeId.value, __historyNodeId.set, None, None)

    
    # Attribute nameComponent uses Python identifier nameComponent
    __nameComponent = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'nameComponent'), 'nameComponent', '__UCIS_BIN_CONTENTS_nameComponent', pyxb.binding.datatypes.string)
    __nameComponent._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 37, 1)
    __nameComponent._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 37, 1)
    
    nameComponent = property(__nameComponent.value, __nameComponent.set, None, None)

    
    # Attribute typeComponent uses Python identifier typeComponent
    __typeComponent = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'typeComponent'), 'typeComponent', '__UCIS_BIN_CONTENTS_typeComponent', pyxb.binding.datatypes.string)
    __typeComponent._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 38, 1)
    __typeComponent._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 38, 1)
    
    typeComponent = property(__typeComponent.value, __typeComponent.set, None, None)

    
    # Attribute coverageCount uses Python identifier coverageCount
    __coverageCount = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'coverageCount'), 'coverageCount', '__UCIS_BIN_CONTENTS_coverageCount', pyxb.binding.datatypes.nonNegativeInteger, required=True)
    __coverageCount._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 39, 1)
    __coverageCount._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 39, 1)
    
    coverageCount = property(__coverageCount.value, __coverageCount.set, None, None)

    _ElementMap.update({
        __historyNodeId.name() : __historyNodeId
    })
    _AttributeMap.update({
        __nameComponent.name() : __nameComponent,
        __typeComponent.name() : __typeComponent,
        __coverageCount.name() : __coverageCount
    })
_module_typeBindings.BIN_CONTENTS = BIN_CONTENTS
Namespace.addCategoryObject('typeBinding', 'BIN_CONTENTS', BIN_CONTENTS)


# Complex type {UCIS}BIN with content type ELEMENT_ONLY
class BIN (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}BIN with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'BIN')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 50, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}contents uses Python identifier contents
    __contents = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'contents'), 'contents', '__UCIS_BIN_UCIScontents', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 52, 1), )

    
    contents = property(__contents.value, __contents.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_BIN_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 53, 1), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_BIN_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 43, 1)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 43, 1)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute coverageCountGoal uses Python identifier coverageCountGoal
    __coverageCountGoal = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'coverageCountGoal'), 'coverageCountGoal', '__UCIS_BIN_coverageCountGoal', pyxb.binding.datatypes.nonNegativeInteger)
    __coverageCountGoal._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 44, 1)
    __coverageCountGoal._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 44, 1)
    
    coverageCountGoal = property(__coverageCountGoal.value, __coverageCountGoal.set, None, None)

    
    # Attribute excluded uses Python identifier excluded
    __excluded = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excluded'), 'excluded', '__UCIS_BIN_excluded', pyxb.binding.datatypes.boolean, unicode_default='false')
    __excluded._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 45, 1)
    __excluded._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 45, 1)
    
    excluded = property(__excluded.value, __excluded.set, None, None)

    
    # Attribute excludedReason uses Python identifier excludedReason
    __excludedReason = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excludedReason'), 'excludedReason', '__UCIS_BIN_excludedReason', pyxb.binding.datatypes.string)
    __excludedReason._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 46, 1)
    __excludedReason._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 46, 1)
    
    excludedReason = property(__excludedReason.value, __excludedReason.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_BIN_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 47, 1)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 47, 1)
    
    weight = property(__weight.value, __weight.set, None, None)

    _ElementMap.update({
        __contents.name() : __contents,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __alias.name() : __alias,
        __coverageCountGoal.name() : __coverageCountGoal,
        __excluded.name() : __excluded,
        __excludedReason.name() : __excludedReason,
        __weight.name() : __weight
    })
_module_typeBindings.BIN = BIN
Namespace.addCategoryObject('typeBinding', 'BIN', BIN)


# Complex type {UCIS}SOURCE_FILE with content type EMPTY
class SOURCE_FILE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}SOURCE_FILE with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'SOURCE_FILE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 263)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute fileName uses Python identifier fileName
    __fileName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'fileName'), 'fileName', '__UCIS_SOURCE_FILE_fileName', pyxb.binding.datatypes.string, required=True)
    __fileName._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 299)
    __fileName._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 299)
    
    fileName = property(__fileName.value, __fileName.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'id'), 'id', '__UCIS_SOURCE_FILE_id', pyxb.binding.datatypes.positiveInteger, required=True)
    __id._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 364)
    __id._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 364)
    
    id = property(__id.value, __id.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __fileName.name() : __fileName,
        __id.name() : __id
    })
_module_typeBindings.SOURCE_FILE = SOURCE_FILE
Namespace.addCategoryObject('typeBinding', 'SOURCE_FILE', SOURCE_FILE)


# Complex type {UCIS}HISTORY_NODE with content type ELEMENT_ONLY
class HISTORY_NODE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}HISTORY_NODE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'HISTORY_NODE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 485)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_HISTORY_NODE_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 536), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute historyNodeId uses Python identifier historyNodeId
    __historyNodeId = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'historyNodeId'), 'historyNodeId', '__UCIS_HISTORY_NODE_historyNodeId', pyxb.binding.datatypes.nonNegativeInteger, required=True)
    __historyNodeId._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 634)
    __historyNodeId._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 634)
    
    historyNodeId = property(__historyNodeId.value, __historyNodeId.set, None, None)

    
    # Attribute parentId uses Python identifier parentId
    __parentId = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'parentId'), 'parentId', '__UCIS_HISTORY_NODE_parentId', pyxb.binding.datatypes.nonNegativeInteger)
    __parentId._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 716)
    __parentId._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 716)
    
    parentId = property(__parentId.value, __parentId.set, None, None)

    
    # Attribute logicalName uses Python identifier logicalName
    __logicalName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'logicalName'), 'logicalName', '__UCIS_HISTORY_NODE_logicalName', pyxb.binding.datatypes.string, required=True)
    __logicalName._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 778)
    __logicalName._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 778)
    
    logicalName = property(__logicalName.value, __logicalName.set, None, None)

    
    # Attribute physicalName uses Python identifier physicalName
    __physicalName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'physicalName'), 'physicalName', '__UCIS_HISTORY_NODE_physicalName', pyxb.binding.datatypes.string)
    __physicalName._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 846)
    __physicalName._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 846)
    
    physicalName = property(__physicalName.value, __physicalName.set, None, None)

    
    # Attribute kind uses Python identifier kind
    __kind = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'kind'), 'kind', '__UCIS_HISTORY_NODE_kind', pyxb.binding.datatypes.string)
    __kind._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 900)
    __kind._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 900)
    
    kind = property(__kind.value, __kind.set, None, None)

    
    # Attribute testStatus uses Python identifier testStatus
    __testStatus = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'testStatus'), 'testStatus', '__UCIS_HISTORY_NODE_testStatus', pyxb.binding.datatypes.boolean, required=True)
    __testStatus._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 946)
    __testStatus._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 946)
    
    testStatus = property(__testStatus.value, __testStatus.set, None, None)

    
    # Attribute simtime uses Python identifier simtime
    __simtime = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'simtime'), 'simtime', '__UCIS_HISTORY_NODE_simtime', pyxb.binding.datatypes.double)
    __simtime._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1014)
    __simtime._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1014)
    
    simtime = property(__simtime.value, __simtime.set, None, None)

    
    # Attribute timeunit uses Python identifier timeunit
    __timeunit = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'timeunit'), 'timeunit', '__UCIS_HISTORY_NODE_timeunit', pyxb.binding.datatypes.string)
    __timeunit._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1063)
    __timeunit._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1063)
    
    timeunit = property(__timeunit.value, __timeunit.set, None, None)

    
    # Attribute runCwd uses Python identifier runCwd
    __runCwd = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'runCwd'), 'runCwd', '__UCIS_HISTORY_NODE_runCwd', pyxb.binding.datatypes.string)
    __runCwd._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1113)
    __runCwd._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1113)
    
    runCwd = property(__runCwd.value, __runCwd.set, None, None)

    
    # Attribute cpuTime uses Python identifier cpuTime
    __cpuTime = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'cpuTime'), 'cpuTime', '__UCIS_HISTORY_NODE_cpuTime', pyxb.binding.datatypes.double)
    __cpuTime._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1161)
    __cpuTime._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1161)
    
    cpuTime = property(__cpuTime.value, __cpuTime.set, None, None)

    
    # Attribute seed uses Python identifier seed
    __seed = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'seed'), 'seed', '__UCIS_HISTORY_NODE_seed', pyxb.binding.datatypes.string)
    __seed._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1210)
    __seed._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1210)
    
    seed = property(__seed.value, __seed.set, None, None)

    
    # Attribute cmd uses Python identifier cmd
    __cmd = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'cmd'), 'cmd', '__UCIS_HISTORY_NODE_cmd', pyxb.binding.datatypes.string)
    __cmd._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1256)
    __cmd._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1256)
    
    cmd = property(__cmd.value, __cmd.set, None, None)

    
    # Attribute args uses Python identifier args
    __args = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'args'), 'args', '__UCIS_HISTORY_NODE_args', pyxb.binding.datatypes.string)
    __args._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1301)
    __args._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1301)
    
    args = property(__args.value, __args.set, None, None)

    
    # Attribute compulsory uses Python identifier compulsory
    __compulsory = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'compulsory'), 'compulsory', '__UCIS_HISTORY_NODE_compulsory', pyxb.binding.datatypes.string)
    __compulsory._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1347)
    __compulsory._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1347)
    
    compulsory = property(__compulsory.value, __compulsory.set, None, None)

    
    # Attribute date uses Python identifier date
    __date = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'date'), 'date', '__UCIS_HISTORY_NODE_date', pyxb.binding.datatypes.dateTime, required=True)
    __date._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1399)
    __date._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1399)
    
    date = property(__date.value, __date.set, None, None)

    
    # Attribute userName uses Python identifier userName
    __userName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'userName'), 'userName', '__UCIS_HISTORY_NODE_userName', pyxb.binding.datatypes.string)
    __userName._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1462)
    __userName._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1462)
    
    userName = property(__userName.value, __userName.set, None, None)

    
    # Attribute cost uses Python identifier cost
    __cost = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'cost'), 'cost', '__UCIS_HISTORY_NODE_cost', pyxb.binding.datatypes.decimal)
    __cost._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1512)
    __cost._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1512)
    
    cost = property(__cost.value, __cost.set, None, None)

    
    # Attribute toolCategory uses Python identifier toolCategory
    __toolCategory = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'toolCategory'), 'toolCategory', '__UCIS_HISTORY_NODE_toolCategory', pyxb.binding.datatypes.string, required=True)
    __toolCategory._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1559)
    __toolCategory._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1559)
    
    toolCategory = property(__toolCategory.value, __toolCategory.set, None, None)

    
    # Attribute ucisVersion uses Python identifier ucisVersion
    __ucisVersion = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'ucisVersion'), 'ucisVersion', '__UCIS_HISTORY_NODE_ucisVersion', pyxb.binding.datatypes.string, required=True)
    __ucisVersion._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1628)
    __ucisVersion._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1628)
    
    ucisVersion = property(__ucisVersion.value, __ucisVersion.set, None, None)

    
    # Attribute vendorId uses Python identifier vendorId
    __vendorId = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'vendorId'), 'vendorId', '__UCIS_HISTORY_NODE_vendorId', pyxb.binding.datatypes.string, required=True)
    __vendorId._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1696)
    __vendorId._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1696)
    
    vendorId = property(__vendorId.value, __vendorId.set, None, None)

    
    # Attribute vendorTool uses Python identifier vendorTool
    __vendorTool = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'vendorTool'), 'vendorTool', '__UCIS_HISTORY_NODE_vendorTool', pyxb.binding.datatypes.string, required=True)
    __vendorTool._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1761)
    __vendorTool._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1761)
    
    vendorTool = property(__vendorTool.value, __vendorTool.set, None, None)

    
    # Attribute vendorToolVersion uses Python identifier vendorToolVersion
    __vendorToolVersion = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'vendorToolVersion'), 'vendorToolVersion', '__UCIS_HISTORY_NODE_vendorToolVersion', pyxb.binding.datatypes.string, required=True)
    __vendorToolVersion._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1828)
    __vendorToolVersion._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1828)
    
    vendorToolVersion = property(__vendorToolVersion.value, __vendorToolVersion.set, None, None)

    
    # Attribute sameTests uses Python identifier sameTests
    __sameTests = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'sameTests'), 'sameTests', '__UCIS_HISTORY_NODE_sameTests', pyxb.binding.datatypes.nonNegativeInteger)
    __sameTests._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1902)
    __sameTests._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1902)
    
    sameTests = property(__sameTests.value, __sameTests.set, None, None)

    
    # Attribute comment uses Python identifier comment
    __comment = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comment'), 'comment', '__UCIS_HISTORY_NODE_comment', pyxb.binding.datatypes.string)
    __comment._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1965)
    __comment._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 1965)
    
    comment = property(__comment.value, __comment.set, None, None)

    _ElementMap.update({
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __historyNodeId.name() : __historyNodeId,
        __parentId.name() : __parentId,
        __logicalName.name() : __logicalName,
        __physicalName.name() : __physicalName,
        __kind.name() : __kind,
        __testStatus.name() : __testStatus,
        __simtime.name() : __simtime,
        __timeunit.name() : __timeunit,
        __runCwd.name() : __runCwd,
        __cpuTime.name() : __cpuTime,
        __seed.name() : __seed,
        __cmd.name() : __cmd,
        __args.name() : __args,
        __compulsory.name() : __compulsory,
        __date.name() : __date,
        __userName.name() : __userName,
        __cost.name() : __cost,
        __toolCategory.name() : __toolCategory,
        __ucisVersion.name() : __ucisVersion,
        __vendorId.name() : __vendorId,
        __vendorTool.name() : __vendorTool,
        __vendorToolVersion.name() : __vendorToolVersion,
        __sameTests.name() : __sameTests,
        __comment.name() : __comment
    })
_module_typeBindings.HISTORY_NODE = HISTORY_NODE
Namespace.addCategoryObject('typeBinding', 'HISTORY_NODE', HISTORY_NODE)


# Complex type {UCIS}DIMENSION with content type EMPTY
class DIMENSION (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}DIMENSION with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DIMENSION')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2066)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute left uses Python identifier left
    __left = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'left'), 'left', '__UCIS_DIMENSION_left', pyxb.binding.datatypes.integer, required=True)
    __left._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2100)
    __left._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2100)
    
    left = property(__left.value, __left.set, None, None)

    
    # Attribute right uses Python identifier right
    __right = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'right'), 'right', '__UCIS_DIMENSION_right', pyxb.binding.datatypes.integer, required=True)
    __right._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2162)
    __right._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2162)
    
    right = property(__right.value, __right.set, None, None)

    
    # Attribute downto uses Python identifier downto
    __downto = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'downto'), 'downto', '__UCIS_DIMENSION_downto', pyxb.binding.datatypes.boolean, required=True)
    __downto._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2225)
    __downto._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2225)
    
    downto = property(__downto.value, __downto.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __left.name() : __left,
        __right.name() : __right,
        __downto.name() : __downto
    })
_module_typeBindings.DIMENSION = DIMENSION
Namespace.addCategoryObject('typeBinding', 'DIMENSION', DIMENSION)


# Complex type {UCIS}TOGGLE with content type ELEMENT_ONLY
class TOGGLE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}TOGGLE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TOGGLE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2338)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}bin uses Python identifier bin
    __bin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'bin'), 'bin', '__UCIS_TOGGLE_UCISbin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2383), )

    
    bin = property(__bin.value, __bin.set, None, None)

    
    # Attribute from uses Python identifier from_
    __from = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'from'), 'from_', '__UCIS_TOGGLE_from', pyxb.binding.datatypes.string, required=True)
    __from._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2434)
    __from._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2434)
    
    from_ = property(__from.value, __from.set, None, None)

    
    # Attribute to uses Python identifier to
    __to = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'to'), 'to', '__UCIS_TOGGLE_to', pyxb.binding.datatypes.string, required=True)
    __to._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2495)
    __to._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2495)
    
    to = property(__to.value, __to.set, None, None)

    _ElementMap.update({
        __bin.name() : __bin
    })
    _AttributeMap.update({
        __from.name() : __from,
        __to.name() : __to
    })
_module_typeBindings.TOGGLE = TOGGLE
Namespace.addCategoryObject('typeBinding', 'TOGGLE', TOGGLE)


# Complex type {UCIS}TOGGLE_BIT with content type ELEMENT_ONLY
class TOGGLE_BIT (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}TOGGLE_BIT with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TOGGLE_BIT')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2606)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}index uses Python identifier index
    __index = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'index'), 'index', '__UCIS_TOGGLE_BIT_UCISindex', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2655), )

    
    index = property(__index.value, __index.set, None, None)

    
    # Element {UCIS}toggle uses Python identifier toggle
    __toggle = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'toggle'), 'toggle', '__UCIS_TOGGLE_BIT_UCIStoggle', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2748), )

    
    toggle = property(__toggle.value, __toggle.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_TOGGLE_BIT_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2826), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_TOGGLE_BIT_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute excluded uses Python identifier excluded
    __excluded = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excluded'), 'excluded', '__UCIS_TOGGLE_BIT_excluded', pyxb.binding.datatypes.boolean, unicode_default='false')
    __excluded._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    __excluded._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    
    excluded = property(__excluded.value, __excluded.set, None, None)

    
    # Attribute excludedReason uses Python identifier excludedReason
    __excludedReason = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excludedReason'), 'excludedReason', '__UCIS_TOGGLE_BIT_excludedReason', pyxb.binding.datatypes.string)
    __excludedReason._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    __excludedReason._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    
    excludedReason = property(__excludedReason.value, __excludedReason.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_TOGGLE_BIT_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    
    weight = property(__weight.value, __weight.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__UCIS_TOGGLE_BIT_name', pyxb.binding.datatypes.string, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2924)
    __name._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2924)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute key uses Python identifier key
    __key = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'key'), 'key', '__UCIS_TOGGLE_BIT_key', pyxb.binding.datatypes.string, required=True)
    __key._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2985)
    __key._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2985)
    
    key = property(__key.value, __key.set, None, None)

    _ElementMap.update({
        __index.name() : __index,
        __toggle.name() : __toggle,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __alias.name() : __alias,
        __excluded.name() : __excluded,
        __excludedReason.name() : __excludedReason,
        __weight.name() : __weight,
        __name.name() : __name,
        __key.name() : __key
    })
_module_typeBindings.TOGGLE_BIT = TOGGLE_BIT
Namespace.addCategoryObject('typeBinding', 'TOGGLE_BIT', TOGGLE_BIT)


# Complex type {UCIS}TOGGLE_OBJECT with content type ELEMENT_ONLY
class TOGGLE_OBJECT (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}TOGGLE_OBJECT with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TOGGLE_OBJECT')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 3141)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}dimension uses Python identifier dimension
    __dimension = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'dimension'), 'dimension', '__UCIS_TOGGLE_OBJECT_UCISdimension', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 3193), )

    
    dimension = property(__dimension.value, __dimension.set, None, None)

    
    # Element {UCIS}id uses Python identifier id
    __id = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'id'), 'id', '__UCIS_TOGGLE_OBJECT_UCISid', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 0), )

    
    id = property(__id.value, __id.set, None, None)

    
    # Element {UCIS}toggleBit uses Python identifier toggleBit
    __toggleBit = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'toggleBit'), 'toggleBit', '__UCIS_TOGGLE_OBJECT_UCIStoggleBit', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 44), )

    
    toggleBit = property(__toggleBit.value, __toggleBit.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_TOGGLE_OBJECT_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 129), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_TOGGLE_OBJECT_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute excluded uses Python identifier excluded
    __excluded = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excluded'), 'excluded', '__UCIS_TOGGLE_OBJECT_excluded', pyxb.binding.datatypes.boolean, unicode_default='false')
    __excluded._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    __excluded._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    
    excluded = property(__excluded.value, __excluded.set, None, None)

    
    # Attribute excludedReason uses Python identifier excludedReason
    __excludedReason = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excludedReason'), 'excludedReason', '__UCIS_TOGGLE_OBJECT_excludedReason', pyxb.binding.datatypes.string)
    __excludedReason._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    __excludedReason._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    
    excludedReason = property(__excludedReason.value, __excludedReason.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_TOGGLE_OBJECT_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    
    weight = property(__weight.value, __weight.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__UCIS_TOGGLE_OBJECT_name', pyxb.binding.datatypes.string, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 227)
    __name._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 227)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute key uses Python identifier key
    __key = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'key'), 'key', '__UCIS_TOGGLE_OBJECT_key', pyxb.binding.datatypes.string, required=True)
    __key._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 288)
    __key._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 288)
    
    key = property(__key.value, __key.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__UCIS_TOGGLE_OBJECT_type', pyxb.binding.datatypes.string)
    __type._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 348)
    __type._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 348)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute portDirection uses Python identifier portDirection
    __portDirection = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'portDirection'), 'portDirection', '__UCIS_TOGGLE_OBJECT_portDirection', pyxb.binding.datatypes.string)
    __portDirection._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 394)
    __portDirection._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 394)
    
    portDirection = property(__portDirection.value, __portDirection.set, None, None)

    _ElementMap.update({
        __dimension.name() : __dimension,
        __id.name() : __id,
        __toggleBit.name() : __toggleBit,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __alias.name() : __alias,
        __excluded.name() : __excluded,
        __excludedReason.name() : __excludedReason,
        __weight.name() : __weight,
        __name.name() : __name,
        __key.name() : __key,
        __type.name() : __type,
        __portDirection.name() : __portDirection
    })
_module_typeBindings.TOGGLE_OBJECT = TOGGLE_OBJECT
Namespace.addCategoryObject('typeBinding', 'TOGGLE_OBJECT', TOGGLE_OBJECT)


# Complex type {UCIS}METRIC_MODE with content type ELEMENT_ONLY
class METRIC_MODE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}METRIC_MODE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'METRIC_MODE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 544)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_METRIC_MODE_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 594), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute metricMode uses Python identifier metricMode
    __metricMode = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'metricMode'), 'metricMode', '__UCIS_METRIC_MODE_metricMode', pyxb.binding.datatypes.string, required=True)
    __metricMode._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 692)
    __metricMode._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 692)
    
    metricMode = property(__metricMode.value, __metricMode.set, None, None)

    _ElementMap.update({
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __metricMode.name() : __metricMode
    })
_module_typeBindings.METRIC_MODE = METRIC_MODE
Namespace.addCategoryObject('typeBinding', 'METRIC_MODE', METRIC_MODE)


# Complex type {UCIS}TOGGLE_COVERAGE with content type ELEMENT_ONLY
class TOGGLE_COVERAGE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}TOGGLE_COVERAGE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TOGGLE_COVERAGE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 816)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}toggleObject uses Python identifier toggleObject
    __toggleObject = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'toggleObject'), 'toggleObject', '__UCIS_TOGGLE_COVERAGE_UCIStoggleObject', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 870), )

    
    toggleObject = property(__toggleObject.value, __toggleObject.set, None, None)

    
    # Element {UCIS}metricMode uses Python identifier metricMode
    __metricMode = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'metricMode'), 'metricMode', '__UCIS_TOGGLE_COVERAGE_UCISmetricMode', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 961), )

    
    metricMode = property(__metricMode.value, __metricMode.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_TOGGLE_COVERAGE_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1048), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute metricMode uses Python identifier metricMode_
    __metricMode_ = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'metricMode'), 'metricMode_', '__UCIS_TOGGLE_COVERAGE_metricMode', pyxb.binding.datatypes.string)
    __metricMode_._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    __metricMode_._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    
    metricMode_ = property(__metricMode_.value, __metricMode_.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_TOGGLE_COVERAGE_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    
    weight = property(__weight.value, __weight.set, None, None)

    _ElementMap.update({
        __toggleObject.name() : __toggleObject,
        __metricMode.name() : __metricMode,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __metricMode_.name() : __metricMode_,
        __weight.name() : __weight
    })
_module_typeBindings.TOGGLE_COVERAGE = TOGGLE_COVERAGE
Namespace.addCategoryObject('typeBinding', 'TOGGLE_COVERAGE', TOGGLE_COVERAGE)


# Complex type {UCIS}LINE_ID with content type EMPTY
class LINE_ID (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}LINE_ID with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'LINE_ID')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1238)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute file uses Python identifier file
    __file = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'file'), 'file', '__UCIS_LINE_ID_file', pyxb.binding.datatypes.positiveInteger, required=True)
    __file._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1270)
    __file._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1270)
    
    file = property(__file.value, __file.set, None, None)

    
    # Attribute line uses Python identifier line
    __line = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'line'), 'line', '__UCIS_LINE_ID_line', pyxb.binding.datatypes.positiveInteger, required=True)
    __line._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1340)
    __line._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1340)
    
    line = property(__line.value, __line.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __file.name() : __file,
        __line.name() : __line
    })
_module_typeBindings.LINE_ID = LINE_ID
Namespace.addCategoryObject('typeBinding', 'LINE_ID', LINE_ID)


# Complex type {UCIS}STATEMENT_ID with content type EMPTY
class STATEMENT_ID (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}STATEMENT_ID with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'STATEMENT_ID')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1463)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute file uses Python identifier file
    __file = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'file'), 'file', '__UCIS_STATEMENT_ID_file', pyxb.binding.datatypes.positiveInteger, required=True)
    __file._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1500)
    __file._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1500)
    
    file = property(__file.value, __file.set, None, None)

    
    # Attribute line uses Python identifier line
    __line = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'line'), 'line', '__UCIS_STATEMENT_ID_line', pyxb.binding.datatypes.positiveInteger, required=True)
    __line._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1570)
    __line._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1570)
    
    line = property(__line.value, __line.set, None, None)

    
    # Attribute inlineCount uses Python identifier inlineCount
    __inlineCount = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'inlineCount'), 'inlineCount', '__UCIS_STATEMENT_ID_inlineCount', pyxb.binding.datatypes.positiveInteger, required=True)
    __inlineCount._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1640)
    __inlineCount._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1640)
    
    inlineCount = property(__inlineCount.value, __inlineCount.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __file.name() : __file,
        __line.name() : __line,
        __inlineCount.name() : __inlineCount
    })
_module_typeBindings.STATEMENT_ID = STATEMENT_ID
Namespace.addCategoryObject('typeBinding', 'STATEMENT_ID', STATEMENT_ID)


# Complex type {UCIS}STATEMENT with content type ELEMENT_ONLY
class STATEMENT (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}STATEMENT with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'STATEMENT')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1766)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}id uses Python identifier id
    __id = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'id'), 'id', '__UCIS_STATEMENT_UCISid', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1814), )

    
    id = property(__id.value, __id.set, None, None)

    
    # Element {UCIS}bin uses Python identifier bin
    __bin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'bin'), 'bin', '__UCIS_STATEMENT_UCISbin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1858), )

    
    bin = property(__bin.value, __bin.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_STATEMENT_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1894), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_STATEMENT_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute excluded uses Python identifier excluded
    __excluded = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excluded'), 'excluded', '__UCIS_STATEMENT_excluded', pyxb.binding.datatypes.boolean, unicode_default='false')
    __excluded._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    __excluded._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    
    excluded = property(__excluded.value, __excluded.set, None, None)

    
    # Attribute excludedReason uses Python identifier excludedReason
    __excludedReason = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excludedReason'), 'excludedReason', '__UCIS_STATEMENT_excludedReason', pyxb.binding.datatypes.string)
    __excludedReason._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    __excludedReason._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    
    excludedReason = property(__excludedReason.value, __excludedReason.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_STATEMENT_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    
    weight = property(__weight.value, __weight.set, None, None)

    _ElementMap.update({
        __id.name() : __id,
        __bin.name() : __bin,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __alias.name() : __alias,
        __excluded.name() : __excluded,
        __excludedReason.name() : __excludedReason,
        __weight.name() : __weight
    })
_module_typeBindings.STATEMENT = STATEMENT
Namespace.addCategoryObject('typeBinding', 'STATEMENT', STATEMENT)


# Complex type {UCIS}BLOCK with content type ELEMENT_ONLY
class BLOCK (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}BLOCK with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'BLOCK')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2080)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}statementId uses Python identifier statementId
    __statementId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'statementId'), 'statementId', '__UCIS_BLOCK_UCISstatementId', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2124), )

    
    statementId = property(__statementId.value, __statementId.set, None, None)

    
    # Element {UCIS}hierarchicalBlock uses Python identifier hierarchicalBlock
    __hierarchicalBlock = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'hierarchicalBlock'), 'hierarchicalBlock', '__UCIS_BLOCK_UCIShierarchicalBlock', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2213), )

    
    hierarchicalBlock = property(__hierarchicalBlock.value, __hierarchicalBlock.set, None, None)

    
    # Element {UCIS}blockBin uses Python identifier blockBin
    __blockBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'blockBin'), 'blockBin', '__UCIS_BLOCK_UCISblockBin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2301), )

    
    blockBin = property(__blockBin.value, __blockBin.set, None, None)

    
    # Element {UCIS}blockId uses Python identifier blockId
    __blockId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'blockId'), 'blockId', '__UCIS_BLOCK_UCISblockId', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2342), )

    
    blockId = property(__blockId.value, __blockId.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_BLOCK_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2391), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_BLOCK_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute excluded uses Python identifier excluded
    __excluded = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excluded'), 'excluded', '__UCIS_BLOCK_excluded', pyxb.binding.datatypes.boolean, unicode_default='false')
    __excluded._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    __excluded._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    
    excluded = property(__excluded.value, __excluded.set, None, None)

    
    # Attribute excludedReason uses Python identifier excludedReason
    __excludedReason = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excludedReason'), 'excludedReason', '__UCIS_BLOCK_excludedReason', pyxb.binding.datatypes.string)
    __excludedReason._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    __excludedReason._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    
    excludedReason = property(__excludedReason.value, __excludedReason.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_BLOCK_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    
    weight = property(__weight.value, __weight.set, None, None)

    
    # Attribute parentProcess uses Python identifier parentProcess
    __parentProcess = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'parentProcess'), 'parentProcess', '__UCIS_BLOCK_parentProcess', pyxb.binding.datatypes.string)
    __parentProcess._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2489)
    __parentProcess._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2489)
    
    parentProcess = property(__parentProcess.value, __parentProcess.set, None, None)

    _ElementMap.update({
        __statementId.name() : __statementId,
        __hierarchicalBlock.name() : __hierarchicalBlock,
        __blockBin.name() : __blockBin,
        __blockId.name() : __blockId,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __alias.name() : __alias,
        __excluded.name() : __excluded,
        __excludedReason.name() : __excludedReason,
        __weight.name() : __weight,
        __parentProcess.name() : __parentProcess
    })
_module_typeBindings.BLOCK = BLOCK
Namespace.addCategoryObject('typeBinding', 'BLOCK', BLOCK)


# Complex type {UCIS}PROCESS_BLOCK with content type ELEMENT_ONLY
class PROCESS_BLOCK (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}PROCESS_BLOCK with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PROCESS_BLOCK')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2640)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}block uses Python identifier block
    __block = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'block'), 'block', '__UCIS_PROCESS_BLOCK_UCISblock', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2692), )

    
    block = property(__block.value, __block.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_PROCESS_BLOCK_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_PROCESS_BLOCK_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute excluded uses Python identifier excluded
    __excluded = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excluded'), 'excluded', '__UCIS_PROCESS_BLOCK_excluded', pyxb.binding.datatypes.boolean, unicode_default='false')
    __excluded._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    __excluded._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    
    excluded = property(__excluded.value, __excluded.set, None, None)

    
    # Attribute excludedReason uses Python identifier excludedReason
    __excludedReason = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excludedReason'), 'excludedReason', '__UCIS_PROCESS_BLOCK_excludedReason', pyxb.binding.datatypes.string)
    __excludedReason._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    __excludedReason._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    
    excludedReason = property(__excludedReason.value, __excludedReason.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_PROCESS_BLOCK_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    
    weight = property(__weight.value, __weight.set, None, None)

    
    # Attribute processType uses Python identifier processType
    __processType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'processType'), 'processType', '__UCIS_PROCESS_BLOCK_processType', pyxb.binding.datatypes.string, required=True)
    __processType._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 98)
    __processType._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 98)
    
    processType = property(__processType.value, __processType.set, None, None)

    _ElementMap.update({
        __block.name() : __block,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __alias.name() : __alias,
        __excluded.name() : __excluded,
        __excludedReason.name() : __excludedReason,
        __weight.name() : __weight,
        __processType.name() : __processType
    })
_module_typeBindings.PROCESS_BLOCK = PROCESS_BLOCK
Namespace.addCategoryObject('typeBinding', 'PROCESS_BLOCK', PROCESS_BLOCK)


# Complex type {UCIS}BLOCK_COVERAGE with content type ELEMENT_ONLY
class BLOCK_COVERAGE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}BLOCK_COVERAGE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'BLOCK_COVERAGE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 263)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}process uses Python identifier process
    __process = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'process'), 'process', '__UCIS_BLOCK_COVERAGE_UCISprocess', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 328), )

    
    process = property(__process.value, __process.set, None, None)

    
    # Element {UCIS}block uses Python identifier block
    __block = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'block'), 'block', '__UCIS_BLOCK_COVERAGE_UCISblock', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 414), )

    
    block = property(__block.value, __block.set, None, None)

    
    # Element {UCIS}statement uses Python identifier statement
    __statement = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'statement'), 'statement', '__UCIS_BLOCK_COVERAGE_UCISstatement', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 490), )

    
    statement = property(__statement.value, __statement.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_BLOCK_COVERAGE_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 587), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute metricMode uses Python identifier metricMode
    __metricMode = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'metricMode'), 'metricMode', '__UCIS_BLOCK_COVERAGE_metricMode', pyxb.binding.datatypes.string)
    __metricMode._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    __metricMode._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    
    metricMode = property(__metricMode.value, __metricMode.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_BLOCK_COVERAGE_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    
    weight = property(__weight.value, __weight.set, None, None)

    _ElementMap.update({
        __process.name() : __process,
        __block.name() : __block,
        __statement.name() : __statement,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __metricMode.name() : __metricMode,
        __weight.name() : __weight
    })
_module_typeBindings.BLOCK_COVERAGE = BLOCK_COVERAGE
Namespace.addCategoryObject('typeBinding', 'BLOCK_COVERAGE', BLOCK_COVERAGE)


# Complex type {UCIS}EXPR with content type ELEMENT_ONLY
class EXPR (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}EXPR with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'EXPR')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 775)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}id uses Python identifier id
    __id = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'id'), 'id', '__UCIS_EXPR_UCISid', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 818), )

    
    id = property(__id.value, __id.set, None, None)

    
    # Element {UCIS}subExpr uses Python identifier subExpr
    __subExpr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'subExpr'), 'subExpr', '__UCIS_EXPR_UCISsubExpr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 862), )

    
    subExpr = property(__subExpr.value, __subExpr.set, None, None)

    
    # Element {UCIS}bin uses Python identifier bin
    __bin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'bin'), 'bin', '__UCIS_EXPR_UCISbin', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 945), )

    
    bin = property(__bin.value, __bin.set, None, None)

    
    # Element {UCIS}hierarchicalExpr uses Python identifier hierarchicalExpr
    __hierarchicalExpr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'hierarchicalExpr'), 'hierarchicalExpr', '__UCIS_EXPR_UCIShierarchicalExpr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1017), )

    
    hierarchicalExpr = property(__hierarchicalExpr.value, __hierarchicalExpr.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_EXPR_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1103), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_EXPR_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute excluded uses Python identifier excluded
    __excluded = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excluded'), 'excluded', '__UCIS_EXPR_excluded', pyxb.binding.datatypes.boolean, unicode_default='false')
    __excluded._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    __excluded._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    
    excluded = property(__excluded.value, __excluded.set, None, None)

    
    # Attribute excludedReason uses Python identifier excludedReason
    __excludedReason = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excludedReason'), 'excludedReason', '__UCIS_EXPR_excludedReason', pyxb.binding.datatypes.string)
    __excludedReason._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    __excludedReason._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    
    excludedReason = property(__excludedReason.value, __excludedReason.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_EXPR_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    
    weight = property(__weight.value, __weight.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__UCIS_EXPR_name', pyxb.binding.datatypes.string, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1201)
    __name._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1201)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute key uses Python identifier key
    __key = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'key'), 'key', '__UCIS_EXPR_key', pyxb.binding.datatypes.string, required=True)
    __key._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1262)
    __key._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1262)
    
    key = property(__key.value, __key.set, None, None)

    
    # Attribute exprString uses Python identifier exprString
    __exprString = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'exprString'), 'exprString', '__UCIS_EXPR_exprString', pyxb.binding.datatypes.string, required=True)
    __exprString._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1322)
    __exprString._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1322)
    
    exprString = property(__exprString.value, __exprString.set, None, None)

    
    # Attribute index uses Python identifier index
    __index = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'index'), 'index', '__UCIS_EXPR_index', pyxb.binding.datatypes.nonNegativeInteger, required=True)
    __index._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1389)
    __index._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1389)
    
    index = property(__index.value, __index.set, None, None)

    
    # Attribute width uses Python identifier width
    __width = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'width'), 'width', '__UCIS_EXPR_width', pyxb.binding.datatypes.nonNegativeInteger, required=True)
    __width._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1463)
    __width._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1463)
    
    width = property(__width.value, __width.set, None, None)

    
    # Attribute statementType uses Python identifier statementType
    __statementType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'statementType'), 'statementType', '__UCIS_EXPR_statementType', pyxb.binding.datatypes.string)
    __statementType._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1537)
    __statementType._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1537)
    
    statementType = property(__statementType.value, __statementType.set, None, None)

    _ElementMap.update({
        __id.name() : __id,
        __subExpr.name() : __subExpr,
        __bin.name() : __bin,
        __hierarchicalExpr.name() : __hierarchicalExpr,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __alias.name() : __alias,
        __excluded.name() : __excluded,
        __excludedReason.name() : __excludedReason,
        __weight.name() : __weight,
        __name.name() : __name,
        __key.name() : __key,
        __exprString.name() : __exprString,
        __index.name() : __index,
        __width.name() : __width,
        __statementType.name() : __statementType
    })
_module_typeBindings.EXPR = EXPR
Namespace.addCategoryObject('typeBinding', 'EXPR', EXPR)


# Complex type {UCIS}CONDITION_COVERAGE with content type ELEMENT_ONLY
class CONDITION_COVERAGE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}CONDITION_COVERAGE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CONDITION_COVERAGE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1693)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}expr uses Python identifier expr
    __expr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'expr'), 'expr', '__UCIS_CONDITION_COVERAGE_UCISexpr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1750), )

    
    expr = property(__expr.value, __expr.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_CONDITION_COVERAGE_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1824), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute metricMode uses Python identifier metricMode
    __metricMode = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'metricMode'), 'metricMode', '__UCIS_CONDITION_COVERAGE_metricMode', pyxb.binding.datatypes.string)
    __metricMode._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    __metricMode._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    
    metricMode = property(__metricMode.value, __metricMode.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_CONDITION_COVERAGE_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    
    weight = property(__weight.value, __weight.set, None, None)

    _ElementMap.update({
        __expr.name() : __expr,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __metricMode.name() : __metricMode,
        __weight.name() : __weight
    })
_module_typeBindings.CONDITION_COVERAGE = CONDITION_COVERAGE
Namespace.addCategoryObject('typeBinding', 'CONDITION_COVERAGE', CONDITION_COVERAGE)


# Complex type {UCIS}BRANCH with content type ELEMENT_ONLY
class BRANCH (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}BRANCH with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'BRANCH')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2014)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}id uses Python identifier id
    __id = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'id'), 'id', '__UCIS_BRANCH_UCISid', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2059), )

    
    id = property(__id.value, __id.set, None, None)

    
    # Element {UCIS}nestedBranch uses Python identifier nestedBranch
    __nestedBranch = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'nestedBranch'), 'nestedBranch', '__UCIS_BRANCH_UCISnestedBranch', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2103), )

    
    nestedBranch = property(__nestedBranch.value, __nestedBranch.set, None, None)

    
    # Element {UCIS}branchBin uses Python identifier branchBin
    __branchBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'branchBin'), 'branchBin', '__UCIS_BRANCH_UCISbranchBin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2197), )

    
    branchBin = property(__branchBin.value, __branchBin.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_BRANCH_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2239), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    _ElementMap.update({
        __id.name() : __id,
        __nestedBranch.name() : __nestedBranch,
        __branchBin.name() : __branchBin,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.BRANCH = BRANCH
Namespace.addCategoryObject('typeBinding', 'BRANCH', BRANCH)


# Complex type {UCIS}BRANCH_STATEMENT with content type ELEMENT_ONLY
class BRANCH_STATEMENT (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}BRANCH_STATEMENT with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'BRANCH_STATEMENT')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2395)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}id uses Python identifier id
    __id = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'id'), 'id', '__UCIS_BRANCH_STATEMENT_UCISid', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2450), )

    
    id = property(__id.value, __id.set, None, None)

    
    # Element {UCIS}branch uses Python identifier branch
    __branch = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'branch'), 'branch', '__UCIS_BRANCH_STATEMENT_UCISbranch', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2494), )

    
    branch = property(__branch.value, __branch.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_BRANCH_STATEMENT_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2572), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_BRANCH_STATEMENT_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute excluded uses Python identifier excluded
    __excluded = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excluded'), 'excluded', '__UCIS_BRANCH_STATEMENT_excluded', pyxb.binding.datatypes.boolean, unicode_default='false')
    __excluded._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    __excluded._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    
    excluded = property(__excluded.value, __excluded.set, None, None)

    
    # Attribute excludedReason uses Python identifier excludedReason
    __excludedReason = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excludedReason'), 'excludedReason', '__UCIS_BRANCH_STATEMENT_excludedReason', pyxb.binding.datatypes.string)
    __excludedReason._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    __excludedReason._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    
    excludedReason = property(__excludedReason.value, __excludedReason.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_BRANCH_STATEMENT_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    
    weight = property(__weight.value, __weight.set, None, None)

    
    # Attribute branchExpr uses Python identifier branchExpr
    __branchExpr = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'branchExpr'), 'branchExpr', '__UCIS_BRANCH_STATEMENT_branchExpr', pyxb.binding.datatypes.string)
    __branchExpr._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2670)
    __branchExpr._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2670)
    
    branchExpr = property(__branchExpr.value, __branchExpr.set, None, None)

    
    # Attribute statementType uses Python identifier statementType
    __statementType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'statementType'), 'statementType', '__UCIS_BRANCH_STATEMENT_statementType', pyxb.binding.datatypes.string, required=True)
    __statementType._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 74, 0)
    __statementType._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 74, 0)
    
    statementType = property(__statementType.value, __statementType.set, None, None)

    _ElementMap.update({
        __id.name() : __id,
        __branch.name() : __branch,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __alias.name() : __alias,
        __excluded.name() : __excluded,
        __excludedReason.name() : __excludedReason,
        __weight.name() : __weight,
        __branchExpr.name() : __branchExpr,
        __statementType.name() : __statementType
    })
_module_typeBindings.BRANCH_STATEMENT = BRANCH_STATEMENT
Namespace.addCategoryObject('typeBinding', 'BRANCH_STATEMENT', BRANCH_STATEMENT)


# Complex type {UCIS}BRANCH_COVERAGE with content type ELEMENT_ONLY
class BRANCH_COVERAGE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}BRANCH_COVERAGE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'BRANCH_COVERAGE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 78, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}statement uses Python identifier statement
    __statement = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'statement'), 'statement', '__UCIS_BRANCH_COVERAGE_UCISstatement', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 80, 0), )

    
    statement = property(__statement.value, __statement.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_BRANCH_COVERAGE_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 82, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute metricMode uses Python identifier metricMode
    __metricMode = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'metricMode'), 'metricMode', '__UCIS_BRANCH_COVERAGE_metricMode', pyxb.binding.datatypes.string)
    __metricMode._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    __metricMode._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    
    metricMode = property(__metricMode.value, __metricMode.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_BRANCH_COVERAGE_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    
    weight = property(__weight.value, __weight.set, None, None)

    _ElementMap.update({
        __statement.name() : __statement,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __metricMode.name() : __metricMode,
        __weight.name() : __weight
    })
_module_typeBindings.BRANCH_COVERAGE = BRANCH_COVERAGE
Namespace.addCategoryObject('typeBinding', 'BRANCH_COVERAGE', BRANCH_COVERAGE)


# Complex type {UCIS}FSM_STATE with content type ELEMENT_ONLY
class FSM_STATE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}FSM_STATE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'FSM_STATE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 88, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}stateBin uses Python identifier stateBin
    __stateBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'stateBin'), 'stateBin', '__UCIS_FSM_STATE_UCISstateBin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 90, 0), )

    
    stateBin = property(__stateBin.value, __stateBin.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_FSM_STATE_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 91, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute stateName uses Python identifier stateName
    __stateName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'stateName'), 'stateName', '__UCIS_FSM_STATE_stateName', pyxb.binding.datatypes.string)
    __stateName._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 94, 0)
    __stateName._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 94, 0)
    
    stateName = property(__stateName.value, __stateName.set, None, None)

    
    # Attribute stateValue uses Python identifier stateValue
    __stateValue = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'stateValue'), 'stateValue', '__UCIS_FSM_STATE_stateValue', pyxb.binding.datatypes.string)
    __stateValue._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 95, 0)
    __stateValue._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 95, 0)
    
    stateValue = property(__stateValue.value, __stateValue.set, None, None)

    _ElementMap.update({
        __stateBin.name() : __stateBin,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __stateName.name() : __stateName,
        __stateValue.name() : __stateValue
    })
_module_typeBindings.FSM_STATE = FSM_STATE
Namespace.addCategoryObject('typeBinding', 'FSM_STATE', FSM_STATE)


# Complex type {UCIS}FSM_TRANSITION with content type ELEMENT_ONLY
class FSM_TRANSITION (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}FSM_TRANSITION with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'FSM_TRANSITION')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 98, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}state uses Python identifier state
    __state = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'state'), 'state', '__UCIS_FSM_TRANSITION_UCISstate', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 100, 0), )

    
    state = property(__state.value, __state.set, None, None)

    
    # Element {UCIS}transitionBin uses Python identifier transitionBin
    __transitionBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'transitionBin'), 'transitionBin', '__UCIS_FSM_TRANSITION_UCIStransitionBin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 102, 0), )

    
    transitionBin = property(__transitionBin.value, __transitionBin.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_FSM_TRANSITION_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 103, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    _ElementMap.update({
        __state.name() : __state,
        __transitionBin.name() : __transitionBin,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.FSM_TRANSITION = FSM_TRANSITION
Namespace.addCategoryObject('typeBinding', 'FSM_TRANSITION', FSM_TRANSITION)


# Complex type {UCIS}FSM with content type ELEMENT_ONLY
class FSM (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}FSM with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'FSM')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 108, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}state uses Python identifier state
    __state = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'state'), 'state', '__UCIS_FSM_UCISstate', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 110, 0), )

    
    state = property(__state.value, __state.set, None, None)

    
    # Element {UCIS}stateTransition uses Python identifier stateTransition
    __stateTransition = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'stateTransition'), 'stateTransition', '__UCIS_FSM_UCISstateTransition', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 112, 0), )

    
    stateTransition = property(__stateTransition.value, __stateTransition.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_FSM_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 114, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_FSM_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute excluded uses Python identifier excluded
    __excluded = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excluded'), 'excluded', '__UCIS_FSM_excluded', pyxb.binding.datatypes.boolean, unicode_default='false')
    __excluded._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    __excluded._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    
    excluded = property(__excluded.value, __excluded.set, None, None)

    
    # Attribute excludedReason uses Python identifier excludedReason
    __excludedReason = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excludedReason'), 'excludedReason', '__UCIS_FSM_excludedReason', pyxb.binding.datatypes.string)
    __excludedReason._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    __excludedReason._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    
    excludedReason = property(__excludedReason.value, __excludedReason.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_FSM_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    
    weight = property(__weight.value, __weight.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__UCIS_FSM_name', pyxb.binding.datatypes.string)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 117, 0)
    __name._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 117, 0)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__UCIS_FSM_type', pyxb.binding.datatypes.string)
    __type._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 118, 0)
    __type._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 118, 0)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute width uses Python identifier width
    __width = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'width'), 'width', '__UCIS_FSM_width', pyxb.binding.datatypes.positiveInteger)
    __width._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 119, 0)
    __width._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 119, 0)
    
    width = property(__width.value, __width.set, None, None)

    _ElementMap.update({
        __state.name() : __state,
        __stateTransition.name() : __stateTransition,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __alias.name() : __alias,
        __excluded.name() : __excluded,
        __excludedReason.name() : __excludedReason,
        __weight.name() : __weight,
        __name.name() : __name,
        __type.name() : __type,
        __width.name() : __width
    })
_module_typeBindings.FSM = FSM
Namespace.addCategoryObject('typeBinding', 'FSM', FSM)


# Complex type {UCIS}FSM_COVERAGE with content type ELEMENT_ONLY
class FSM_COVERAGE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}FSM_COVERAGE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'FSM_COVERAGE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 123, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}fsm uses Python identifier fsm
    __fsm = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'fsm'), 'fsm', '__UCIS_FSM_COVERAGE_UCISfsm', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 125, 0), )

    
    fsm = property(__fsm.value, __fsm.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_FSM_COVERAGE_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 127, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute metricMode uses Python identifier metricMode
    __metricMode = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'metricMode'), 'metricMode', '__UCIS_FSM_COVERAGE_metricMode', pyxb.binding.datatypes.string)
    __metricMode._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    __metricMode._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    
    metricMode = property(__metricMode.value, __metricMode.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_FSM_COVERAGE_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    
    weight = property(__weight.value, __weight.set, None, None)

    _ElementMap.update({
        __fsm.name() : __fsm,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __metricMode.name() : __metricMode,
        __weight.name() : __weight
    })
_module_typeBindings.FSM_COVERAGE = FSM_COVERAGE
Namespace.addCategoryObject('typeBinding', 'FSM_COVERAGE', FSM_COVERAGE)


# Complex type {UCIS}ASSERTION with content type ELEMENT_ONLY
class ASSERTION (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}ASSERTION with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ASSERTION')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 133, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}coverBin uses Python identifier coverBin
    __coverBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'coverBin'), 'coverBin', '__UCIS_ASSERTION_UCIScoverBin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 135, 0), )

    
    coverBin = property(__coverBin.value, __coverBin.set, None, None)

    
    # Element {UCIS}passBin uses Python identifier passBin
    __passBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'passBin'), 'passBin', '__UCIS_ASSERTION_UCISpassBin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 137, 0), )

    
    passBin = property(__passBin.value, __passBin.set, None, None)

    
    # Element {UCIS}failBin uses Python identifier failBin
    __failBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'failBin'), 'failBin', '__UCIS_ASSERTION_UCISfailBin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 139, 0), )

    
    failBin = property(__failBin.value, __failBin.set, None, None)

    
    # Element {UCIS}vacuousBin uses Python identifier vacuousBin
    __vacuousBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'vacuousBin'), 'vacuousBin', '__UCIS_ASSERTION_UCISvacuousBin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 141, 0), )

    
    vacuousBin = property(__vacuousBin.value, __vacuousBin.set, None, None)

    
    # Element {UCIS}disabledBin uses Python identifier disabledBin
    __disabledBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'disabledBin'), 'disabledBin', '__UCIS_ASSERTION_UCISdisabledBin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 143, 0), )

    
    disabledBin = property(__disabledBin.value, __disabledBin.set, None, None)

    
    # Element {UCIS}attemptBin uses Python identifier attemptBin
    __attemptBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'attemptBin'), 'attemptBin', '__UCIS_ASSERTION_UCISattemptBin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 145, 0), )

    
    attemptBin = property(__attemptBin.value, __attemptBin.set, None, None)

    
    # Element {UCIS}activeBin uses Python identifier activeBin
    __activeBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'activeBin'), 'activeBin', '__UCIS_ASSERTION_UCISactiveBin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 147, 0), )

    
    activeBin = property(__activeBin.value, __activeBin.set, None, None)

    
    # Element {UCIS}peakActiveBin uses Python identifier peakActiveBin
    __peakActiveBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'peakActiveBin'), 'peakActiveBin', '__UCIS_ASSERTION_UCISpeakActiveBin', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 150, 0), )

    
    peakActiveBin = property(__peakActiveBin.value, __peakActiveBin.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_ASSERTION_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 152, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_ASSERTION_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 59, 1)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute excluded uses Python identifier excluded
    __excluded = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excluded'), 'excluded', '__UCIS_ASSERTION_excluded', pyxb.binding.datatypes.boolean, unicode_default='false')
    __excluded._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    __excluded._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 60, 1)
    
    excluded = property(__excluded.value, __excluded.set, None, None)

    
    # Attribute excludedReason uses Python identifier excludedReason
    __excludedReason = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excludedReason'), 'excludedReason', '__UCIS_ASSERTION_excludedReason', pyxb.binding.datatypes.string)
    __excludedReason._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    __excludedReason._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 61, 1)
    
    excludedReason = property(__excludedReason.value, __excludedReason.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_ASSERTION_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 62, 1)
    
    weight = property(__weight.value, __weight.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__UCIS_ASSERTION_name', pyxb.binding.datatypes.string, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 155, 0)
    __name._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 155, 0)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute assertionKind uses Python identifier assertionKind
    __assertionKind = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'assertionKind'), 'assertionKind', '__UCIS_ASSERTION_assertionKind', pyxb.binding.datatypes.string, required=True)
    __assertionKind._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 156, 0)
    __assertionKind._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 156, 0)
    
    assertionKind = property(__assertionKind.value, __assertionKind.set, None, None)

    _ElementMap.update({
        __coverBin.name() : __coverBin,
        __passBin.name() : __passBin,
        __failBin.name() : __failBin,
        __vacuousBin.name() : __vacuousBin,
        __disabledBin.name() : __disabledBin,
        __attemptBin.name() : __attemptBin,
        __activeBin.name() : __activeBin,
        __peakActiveBin.name() : __peakActiveBin,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __alias.name() : __alias,
        __excluded.name() : __excluded,
        __excludedReason.name() : __excludedReason,
        __weight.name() : __weight,
        __name.name() : __name,
        __assertionKind.name() : __assertionKind
    })
_module_typeBindings.ASSERTION = ASSERTION
Namespace.addCategoryObject('typeBinding', 'ASSERTION', ASSERTION)


# Complex type {UCIS}ASSERTION_COVERAGE with content type ELEMENT_ONLY
class ASSERTION_COVERAGE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}ASSERTION_COVERAGE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ASSERTION_COVERAGE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 160, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}assertion uses Python identifier assertion
    __assertion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'assertion'), 'assertion', '__UCIS_ASSERTION_COVERAGE_UCISassertion', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 162, 0), )

    
    assertion = property(__assertion.value, __assertion.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_ASSERTION_COVERAGE_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 164, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute metricMode uses Python identifier metricMode
    __metricMode = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'metricMode'), 'metricMode', '__UCIS_ASSERTION_COVERAGE_metricMode', pyxb.binding.datatypes.string)
    __metricMode._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    __metricMode._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    
    metricMode = property(__metricMode.value, __metricMode.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_ASSERTION_COVERAGE_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    
    weight = property(__weight.value, __weight.set, None, None)

    _ElementMap.update({
        __assertion.name() : __assertion,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __metricMode.name() : __metricMode,
        __weight.name() : __weight
    })
_module_typeBindings.ASSERTION_COVERAGE = ASSERTION_COVERAGE
Namespace.addCategoryObject('typeBinding', 'ASSERTION_COVERAGE', ASSERTION_COVERAGE)


# Complex type {UCIS}SEQUENCE with content type ELEMENT_ONLY
class SEQUENCE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}SEQUENCE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'SEQUENCE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 170, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}contents uses Python identifier contents
    __contents = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'contents'), 'contents', '__UCIS_SEQUENCE_UCIScontents', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 172, 0), )

    
    contents = property(__contents.value, __contents.set, None, None)

    
    # Element {UCIS}seqValue uses Python identifier seqValue
    __seqValue = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'seqValue'), 'seqValue', '__UCIS_SEQUENCE_UCISseqValue', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 173, 0), )

    
    seqValue = property(__seqValue.value, __seqValue.set, None, None)

    _ElementMap.update({
        __contents.name() : __contents,
        __seqValue.name() : __seqValue
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.SEQUENCE = SEQUENCE
Namespace.addCategoryObject('typeBinding', 'SEQUENCE', SEQUENCE)


# Complex type {UCIS}RANGE_VALUE with content type ELEMENT_ONLY
class RANGE_VALUE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}RANGE_VALUE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'RANGE_VALUE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 178, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}contents uses Python identifier contents
    __contents = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'contents'), 'contents', '__UCIS_RANGE_VALUE_UCIScontents', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 180, 0), )

    
    contents = property(__contents.value, __contents.set, None, None)

    
    # Attribute from uses Python identifier from_
    __from = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'from'), 'from_', '__UCIS_RANGE_VALUE_from', pyxb.binding.datatypes.integer, required=True)
    __from._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 182, 0)
    __from._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 182, 0)
    
    from_ = property(__from.value, __from.set, None, None)

    
    # Attribute to uses Python identifier to
    __to = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'to'), 'to', '__UCIS_RANGE_VALUE_to', pyxb.binding.datatypes.integer, required=True)
    __to._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 183, 0)
    __to._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 183, 0)
    
    to = property(__to.value, __to.set, None, None)

    _ElementMap.update({
        __contents.name() : __contents
    })
    _AttributeMap.update({
        __from.name() : __from,
        __to.name() : __to
    })
_module_typeBindings.RANGE_VALUE = RANGE_VALUE
Namespace.addCategoryObject('typeBinding', 'RANGE_VALUE', RANGE_VALUE)


# Complex type {UCIS}COVERPOINT_BIN with content type ELEMENT_ONLY
class COVERPOINT_BIN (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}COVERPOINT_BIN with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'COVERPOINT_BIN')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 186, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}range uses Python identifier range
    __range = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'range'), 'range', '__UCIS_COVERPOINT_BIN_UCISrange', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 189, 0), )

    
    range = property(__range.value, __range.set, None, None)

    
    # Element {UCIS}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'sequence'), 'sequence', '__UCIS_COVERPOINT_BIN_UCISsequence', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 191, 0), )

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_COVERPOINT_BIN_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 194, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_COVERPOINT_BIN_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 197, 0)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 197, 0)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__UCIS_COVERPOINT_BIN_type', pyxb.binding.datatypes.string, required=True)
    __type._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 198, 0)
    __type._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 198, 0)
    
    type = property(__type.value, __type.set, None, None)

    _ElementMap.update({
        __range.name() : __range,
        __sequence.name() : __sequence,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __alias.name() : __alias,
        __type.name() : __type
    })
_module_typeBindings.COVERPOINT_BIN = COVERPOINT_BIN
Namespace.addCategoryObject('typeBinding', 'COVERPOINT_BIN', COVERPOINT_BIN)


# Complex type {UCIS}CROSS_BIN with content type ELEMENT_ONLY
class CROSS_BIN (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}CROSS_BIN with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CROSS_BIN')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 201, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}index uses Python identifier index
    __index = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'index'), 'index', '__UCIS_CROSS_BIN_UCISindex', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 203, 0), )

    
    index = property(__index.value, __index.set, None, None)

    
    # Element {UCIS}contents uses Python identifier contents
    __contents = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'contents'), 'contents', '__UCIS_CROSS_BIN_UCIScontents', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 205, 0), )

    
    contents = property(__contents.value, __contents.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_CROSS_BIN_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 206, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__UCIS_CROSS_BIN_type', pyxb.binding.datatypes.string, unicode_default='default')
    __type._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 209, 0)
    __type._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 209, 0)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_CROSS_BIN_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 210, 0)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 210, 0)
    
    alias = property(__alias.value, __alias.set, None, None)

    _ElementMap.update({
        __index.name() : __index,
        __contents.name() : __contents,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __type.name() : __type,
        __alias.name() : __alias
    })
_module_typeBindings.CROSS_BIN = CROSS_BIN
Namespace.addCategoryObject('typeBinding', 'CROSS_BIN', CROSS_BIN)


# Complex type {UCIS}CROSS_OPTIONS with content type EMPTY
class CROSS_OPTIONS (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}CROSS_OPTIONS with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CROSS_OPTIONS')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 213, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_CROSS_OPTIONS_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 214, 0)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 214, 0)
    
    weight = property(__weight.value, __weight.set, None, None)

    
    # Attribute goal uses Python identifier goal
    __goal = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'goal'), 'goal', '__UCIS_CROSS_OPTIONS_goal', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='100')
    __goal._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 215, 0)
    __goal._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 215, 0)
    
    goal = property(__goal.value, __goal.set, None, None)

    
    # Attribute comment uses Python identifier comment
    __comment = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comment'), 'comment', '__UCIS_CROSS_OPTIONS_comment', pyxb.binding.datatypes.string, unicode_default='')
    __comment._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 216, 0)
    __comment._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 216, 0)
    
    comment = property(__comment.value, __comment.set, None, None)

    
    # Attribute at_least uses Python identifier at_least
    __at_least = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'at_least'), 'at_least', '__UCIS_CROSS_OPTIONS_at_least', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __at_least._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 217, 0)
    __at_least._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 217, 0)
    
    at_least = property(__at_least.value, __at_least.set, None, None)

    
    # Attribute cross_num_print_missing uses Python identifier cross_num_print_missing
    __cross_num_print_missing = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'cross_num_print_missing'), 'cross_num_print_missing', '__UCIS_CROSS_OPTIONS_cross_num_print_missing', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='0')
    __cross_num_print_missing._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 218, 0)
    __cross_num_print_missing._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 218, 0)
    
    cross_num_print_missing = property(__cross_num_print_missing.value, __cross_num_print_missing.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __weight.name() : __weight,
        __goal.name() : __goal,
        __comment.name() : __comment,
        __at_least.name() : __at_least,
        __cross_num_print_missing.name() : __cross_num_print_missing
    })
_module_typeBindings.CROSS_OPTIONS = CROSS_OPTIONS
Namespace.addCategoryObject('typeBinding', 'CROSS_OPTIONS', CROSS_OPTIONS)


# Complex type {UCIS}CROSS with content type ELEMENT_ONLY
class CROSS (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}CROSS with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CROSS')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 222, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}options uses Python identifier options
    __options = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'options'), 'options', '__UCIS_CROSS_UCISoptions', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 226, 0), )

    
    options = property(__options.value, __options.set, None, None)

    
    # Element {UCIS}crossExpr uses Python identifier crossExpr
    __crossExpr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'crossExpr'), 'crossExpr', '__UCIS_CROSS_UCIScrossExpr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 227, 0), )

    
    crossExpr = property(__crossExpr.value, __crossExpr.set, None, None)

    
    # Element {UCIS}crossBin uses Python identifier crossBin
    __crossBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'crossBin'), 'crossBin', '__UCIS_CROSS_UCIScrossBin', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 229, 0), )

    
    crossBin = property(__crossBin.value, __crossBin.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_CROSS_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 231, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__UCIS_CROSS_name', pyxb.binding.datatypes.string, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 234, 0)
    __name._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 234, 0)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute key uses Python identifier key
    __key = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'key'), 'key', '__UCIS_CROSS_key', pyxb.binding.datatypes.string, required=True)
    __key._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 235, 0)
    __key._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 235, 0)
    
    key = property(__key.value, __key.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_CROSS_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 236, 0)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 236, 0)
    
    alias = property(__alias.value, __alias.set, None, None)

    _ElementMap.update({
        __options.name() : __options,
        __crossExpr.name() : __crossExpr,
        __crossBin.name() : __crossBin,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __name.name() : __name,
        __key.name() : __key,
        __alias.name() : __alias
    })
_module_typeBindings.CROSS = CROSS
Namespace.addCategoryObject('typeBinding', 'CROSS', CROSS)


# Complex type {UCIS}COVERPOINT_OPTIONS with content type EMPTY
class COVERPOINT_OPTIONS (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}COVERPOINT_OPTIONS with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'COVERPOINT_OPTIONS')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 239, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_COVERPOINT_OPTIONS_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 240, 0)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 240, 0)
    
    weight = property(__weight.value, __weight.set, None, None)

    
    # Attribute goal uses Python identifier goal
    __goal = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'goal'), 'goal', '__UCIS_COVERPOINT_OPTIONS_goal', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='100')
    __goal._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 241, 0)
    __goal._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 241, 0)
    
    goal = property(__goal.value, __goal.set, None, None)

    
    # Attribute comment uses Python identifier comment
    __comment = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comment'), 'comment', '__UCIS_COVERPOINT_OPTIONS_comment', pyxb.binding.datatypes.string, unicode_default='')
    __comment._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 242, 0)
    __comment._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 242, 0)
    
    comment = property(__comment.value, __comment.set, None, None)

    
    # Attribute at_least uses Python identifier at_least
    __at_least = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'at_least'), 'at_least', '__UCIS_COVERPOINT_OPTIONS_at_least', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __at_least._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 243, 0)
    __at_least._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 243, 0)
    
    at_least = property(__at_least.value, __at_least.set, None, None)

    
    # Attribute detect_overlap uses Python identifier detect_overlap
    __detect_overlap = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'detect_overlap'), 'detect_overlap', '__UCIS_COVERPOINT_OPTIONS_detect_overlap', pyxb.binding.datatypes.boolean, unicode_default='false')
    __detect_overlap._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 244, 0)
    __detect_overlap._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 244, 0)
    
    detect_overlap = property(__detect_overlap.value, __detect_overlap.set, None, None)

    
    # Attribute auto_bin_max uses Python identifier auto_bin_max
    __auto_bin_max = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'auto_bin_max'), 'auto_bin_max', '__UCIS_COVERPOINT_OPTIONS_auto_bin_max', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='64')
    __auto_bin_max._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 245, 0)
    __auto_bin_max._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 245, 0)
    
    auto_bin_max = property(__auto_bin_max.value, __auto_bin_max.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __weight.name() : __weight,
        __goal.name() : __goal,
        __comment.name() : __comment,
        __at_least.name() : __at_least,
        __detect_overlap.name() : __detect_overlap,
        __auto_bin_max.name() : __auto_bin_max
    })
_module_typeBindings.COVERPOINT_OPTIONS = COVERPOINT_OPTIONS
Namespace.addCategoryObject('typeBinding', 'COVERPOINT_OPTIONS', COVERPOINT_OPTIONS)


# Complex type {UCIS}COVERPOINT with content type ELEMENT_ONLY
class COVERPOINT (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}COVERPOINT with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'COVERPOINT')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 248, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}options uses Python identifier options
    __options = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'options'), 'options', '__UCIS_COVERPOINT_UCISoptions', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 250, 0), )

    
    options = property(__options.value, __options.set, None, None)

    
    # Element {UCIS}coverpointBin uses Python identifier coverpointBin
    __coverpointBin = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'coverpointBin'), 'coverpointBin', '__UCIS_COVERPOINT_UCIScoverpointBin', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 251, 0), )

    
    coverpointBin = property(__coverpointBin.value, __coverpointBin.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_COVERPOINT_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 253, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__UCIS_COVERPOINT_name', pyxb.binding.datatypes.string, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 256, 0)
    __name._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 256, 0)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute key uses Python identifier key
    __key = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'key'), 'key', '__UCIS_COVERPOINT_key', pyxb.binding.datatypes.string, required=True)
    __key._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 257, 0)
    __key._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 257, 0)
    
    key = property(__key.value, __key.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_COVERPOINT_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 258, 0)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 258, 0)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute exprString uses Python identifier exprString
    __exprString = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'exprString'), 'exprString', '__UCIS_COVERPOINT_exprString', pyxb.binding.datatypes.string)
    __exprString._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 259, 0)
    __exprString._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 259, 0)
    
    exprString = property(__exprString.value, __exprString.set, None, None)

    _ElementMap.update({
        __options.name() : __options,
        __coverpointBin.name() : __coverpointBin,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __name.name() : __name,
        __key.name() : __key,
        __alias.name() : __alias,
        __exprString.name() : __exprString
    })
_module_typeBindings.COVERPOINT = COVERPOINT
Namespace.addCategoryObject('typeBinding', 'COVERPOINT', COVERPOINT)


# Complex type {UCIS}CG_ID with content type ELEMENT_ONLY
class CG_ID (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}CG_ID with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CG_ID')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 262, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}cginstSourceId uses Python identifier cginstSourceId
    __cginstSourceId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'cginstSourceId'), 'cginstSourceId', '__UCIS_CG_ID_UCIScginstSourceId', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 264, 0), )

    
    cginstSourceId = property(__cginstSourceId.value, __cginstSourceId.set, None, None)

    
    # Element {UCIS}cgSourceId uses Python identifier cgSourceId
    __cgSourceId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'cgSourceId'), 'cgSourceId', '__UCIS_CG_ID_UCIScgSourceId', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 265, 0), )

    
    cgSourceId = property(__cgSourceId.value, __cgSourceId.set, None, None)

    
    # Attribute cgName uses Python identifier cgName
    __cgName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'cgName'), 'cgName', '__UCIS_CG_ID_cgName', pyxb.binding.datatypes.string, required=True)
    __cgName._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 267, 0)
    __cgName._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 267, 0)
    
    cgName = property(__cgName.value, __cgName.set, None, None)

    
    # Attribute moduleName uses Python identifier moduleName
    __moduleName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'moduleName'), 'moduleName', '__UCIS_CG_ID_moduleName', pyxb.binding.datatypes.string, required=True)
    __moduleName._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 268, 0)
    __moduleName._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 268, 0)
    
    moduleName = property(__moduleName.value, __moduleName.set, None, None)

    _ElementMap.update({
        __cginstSourceId.name() : __cginstSourceId,
        __cgSourceId.name() : __cgSourceId
    })
    _AttributeMap.update({
        __cgName.name() : __cgName,
        __moduleName.name() : __moduleName
    })
_module_typeBindings.CG_ID = CG_ID
Namespace.addCategoryObject('typeBinding', 'CG_ID', CG_ID)


# Complex type {UCIS}CGINST_OPTIONS with content type EMPTY
class CGINST_OPTIONS (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}CGINST_OPTIONS with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CGINST_OPTIONS')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 271, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_CGINST_OPTIONS_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 272, 0)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 272, 0)
    
    weight = property(__weight.value, __weight.set, None, None)

    
    # Attribute goal uses Python identifier goal
    __goal = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'goal'), 'goal', '__UCIS_CGINST_OPTIONS_goal', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='100')
    __goal._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 273, 0)
    __goal._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 273, 0)
    
    goal = property(__goal.value, __goal.set, None, None)

    
    # Attribute comment uses Python identifier comment
    __comment = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'comment'), 'comment', '__UCIS_CGINST_OPTIONS_comment', pyxb.binding.datatypes.string, unicode_default='')
    __comment._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 274, 0)
    __comment._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 274, 0)
    
    comment = property(__comment.value, __comment.set, None, None)

    
    # Attribute at_least uses Python identifier at_least
    __at_least = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'at_least'), 'at_least', '__UCIS_CGINST_OPTIONS_at_least', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __at_least._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 275, 0)
    __at_least._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 275, 0)
    
    at_least = property(__at_least.value, __at_least.set, None, None)

    
    # Attribute detect_overlap uses Python identifier detect_overlap
    __detect_overlap = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'detect_overlap'), 'detect_overlap', '__UCIS_CGINST_OPTIONS_detect_overlap', pyxb.binding.datatypes.boolean, unicode_default='false')
    __detect_overlap._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 276, 0)
    __detect_overlap._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 276, 0)
    
    detect_overlap = property(__detect_overlap.value, __detect_overlap.set, None, None)

    
    # Attribute auto_bin_max uses Python identifier auto_bin_max
    __auto_bin_max = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'auto_bin_max'), 'auto_bin_max', '__UCIS_CGINST_OPTIONS_auto_bin_max', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='64')
    __auto_bin_max._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 277, 0)
    __auto_bin_max._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 277, 0)
    
    auto_bin_max = property(__auto_bin_max.value, __auto_bin_max.set, None, None)

    
    # Attribute cross_num_print_missing uses Python identifier cross_num_print_missing
    __cross_num_print_missing = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'cross_num_print_missing'), 'cross_num_print_missing', '__UCIS_CGINST_OPTIONS_cross_num_print_missing', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='0')
    __cross_num_print_missing._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 278, 0)
    __cross_num_print_missing._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 278, 0)
    
    cross_num_print_missing = property(__cross_num_print_missing.value, __cross_num_print_missing.set, None, None)

    
    # Attribute per_instance uses Python identifier per_instance
    __per_instance = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'per_instance'), 'per_instance', '__UCIS_CGINST_OPTIONS_per_instance', pyxb.binding.datatypes.boolean, unicode_default='false')
    __per_instance._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 280, 0)
    __per_instance._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 280, 0)
    
    per_instance = property(__per_instance.value, __per_instance.set, None, None)

    
    # Attribute merge_instances uses Python identifier merge_instances
    __merge_instances = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'merge_instances'), 'merge_instances', '__UCIS_CGINST_OPTIONS_merge_instances', pyxb.binding.datatypes.boolean, unicode_default='false')
    __merge_instances._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 281, 0)
    __merge_instances._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 281, 0)
    
    merge_instances = property(__merge_instances.value, __merge_instances.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __weight.name() : __weight,
        __goal.name() : __goal,
        __comment.name() : __comment,
        __at_least.name() : __at_least,
        __detect_overlap.name() : __detect_overlap,
        __auto_bin_max.name() : __auto_bin_max,
        __cross_num_print_missing.name() : __cross_num_print_missing,
        __per_instance.name() : __per_instance,
        __merge_instances.name() : __merge_instances
    })
_module_typeBindings.CGINST_OPTIONS = CGINST_OPTIONS
Namespace.addCategoryObject('typeBinding', 'CGINST_OPTIONS', CGINST_OPTIONS)


# Complex type {UCIS}CGINSTANCE with content type ELEMENT_ONLY
class CGINSTANCE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}CGINSTANCE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CGINSTANCE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 284, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}options uses Python identifier options
    __options = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'options'), 'options', '__UCIS_CGINSTANCE_UCISoptions', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 286, 0), )

    
    options = property(__options.value, __options.set, None, None)

    
    # Element {UCIS}cgId uses Python identifier cgId
    __cgId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'cgId'), 'cgId', '__UCIS_CGINSTANCE_UCIScgId', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 287, 0), )

    
    cgId = property(__cgId.value, __cgId.set, None, None)

    
    # Element {UCIS}cgParms uses Python identifier cgParms
    __cgParms = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'cgParms'), 'cgParms', '__UCIS_CGINSTANCE_UCIScgParms', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 288, 0), )

    
    cgParms = property(__cgParms.value, __cgParms.set, None, None)

    
    # Element {UCIS}coverpoint uses Python identifier coverpoint
    __coverpoint = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'coverpoint'), 'coverpoint', '__UCIS_CGINSTANCE_UCIScoverpoint', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 290, 0), )

    
    coverpoint = property(__coverpoint.value, __coverpoint.set, None, None)

    
    # Element {UCIS}cross uses Python identifier cross
    __cross = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'cross'), 'cross', '__UCIS_CGINSTANCE_UCIScross', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 292, 0), )

    
    cross = property(__cross.value, __cross.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_CGINSTANCE_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 294, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__UCIS_CGINSTANCE_name', pyxb.binding.datatypes.string, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 297, 0)
    __name._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 297, 0)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute key uses Python identifier key
    __key = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'key'), 'key', '__UCIS_CGINSTANCE_key', pyxb.binding.datatypes.string, required=True)
    __key._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 298, 0)
    __key._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 298, 0)
    
    key = property(__key.value, __key.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_CGINSTANCE_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 301, 0)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 301, 0)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute excluded uses Python identifier excluded
    __excluded = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excluded'), 'excluded', '__UCIS_CGINSTANCE_excluded', pyxb.binding.datatypes.boolean, unicode_default='false')
    __excluded._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 302, 0)
    __excluded._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 302, 0)
    
    excluded = property(__excluded.value, __excluded.set, None, None)

    
    # Attribute excludedReason uses Python identifier excludedReason
    __excludedReason = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'excludedReason'), 'excludedReason', '__UCIS_CGINSTANCE_excludedReason', pyxb.binding.datatypes.string)
    __excludedReason._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 303, 0)
    __excludedReason._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 303, 0)
    
    excludedReason = property(__excludedReason.value, __excludedReason.set, None, None)

    _ElementMap.update({
        __options.name() : __options,
        __cgId.name() : __cgId,
        __cgParms.name() : __cgParms,
        __coverpoint.name() : __coverpoint,
        __cross.name() : __cross,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __name.name() : __name,
        __key.name() : __key,
        __alias.name() : __alias,
        __excluded.name() : __excluded,
        __excludedReason.name() : __excludedReason
    })
_module_typeBindings.CGINSTANCE = CGINSTANCE
Namespace.addCategoryObject('typeBinding', 'CGINSTANCE', CGINSTANCE)


# Complex type {UCIS}COVERGROUP_COVERAGE with content type ELEMENT_ONLY
class COVERGROUP_COVERAGE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}COVERGROUP_COVERAGE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'COVERGROUP_COVERAGE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 306, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}cgInstance uses Python identifier cgInstance
    __cgInstance = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'cgInstance'), 'cgInstance', '__UCIS_COVERGROUP_COVERAGE_UCIScgInstance', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 308, 0), )

    
    cgInstance = property(__cgInstance.value, __cgInstance.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_COVERGROUP_COVERAGE_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 310, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute metricMode uses Python identifier metricMode
    __metricMode = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'metricMode'), 'metricMode', '__UCIS_COVERGROUP_COVERAGE_metricMode', pyxb.binding.datatypes.string)
    __metricMode._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    __metricMode._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 84)
    
    metricMode = property(__metricMode.value, __metricMode.set, None, None)

    
    # Attribute weight uses Python identifier weight
    __weight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'weight'), 'weight', '__UCIS_COVERGROUP_COVERAGE_weight', pyxb.binding.datatypes.nonNegativeInteger, unicode_default='1')
    __weight._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    __weight._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 136)
    
    weight = property(__weight.value, __weight.set, None, None)

    _ElementMap.update({
        __cgInstance.name() : __cgInstance,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __metricMode.name() : __metricMode,
        __weight.name() : __weight
    })
_module_typeBindings.COVERGROUP_COVERAGE = COVERGROUP_COVERAGE
Namespace.addCategoryObject('typeBinding', 'COVERGROUP_COVERAGE', COVERGROUP_COVERAGE)


# Complex type {UCIS}INSTANCE_COVERAGE with content type ELEMENT_ONLY
class INSTANCE_COVERAGE (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}INSTANCE_COVERAGE with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'INSTANCE_COVERAGE')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 316, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}designParameter uses Python identifier designParameter
    __designParameter = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'designParameter'), 'designParameter', '__UCIS_INSTANCE_COVERAGE_UCISdesignParameter', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 318, 0), )

    
    designParameter = property(__designParameter.value, __designParameter.set, None, None)

    
    # Element {UCIS}id uses Python identifier id
    __id = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'id'), 'id', '__UCIS_INSTANCE_COVERAGE_UCISid', False, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 320, 0), )

    
    id = property(__id.value, __id.set, None, None)

    
    # Element {UCIS}toggleCoverage uses Python identifier toggleCoverage
    __toggleCoverage = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'toggleCoverage'), 'toggleCoverage', '__UCIS_INSTANCE_COVERAGE_UCIStoggleCoverage', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 321, 0), )

    
    toggleCoverage = property(__toggleCoverage.value, __toggleCoverage.set, None, None)

    
    # Element {UCIS}blockCoverage uses Python identifier blockCoverage
    __blockCoverage = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'blockCoverage'), 'blockCoverage', '__UCIS_INSTANCE_COVERAGE_UCISblockCoverage', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 323, 0), )

    
    blockCoverage = property(__blockCoverage.value, __blockCoverage.set, None, None)

    
    # Element {UCIS}conditionCoverage uses Python identifier conditionCoverage
    __conditionCoverage = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'conditionCoverage'), 'conditionCoverage', '__UCIS_INSTANCE_COVERAGE_UCISconditionCoverage', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 325, 0), )

    
    conditionCoverage = property(__conditionCoverage.value, __conditionCoverage.set, None, None)

    
    # Element {UCIS}branchCoverage uses Python identifier branchCoverage
    __branchCoverage = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'branchCoverage'), 'branchCoverage', '__UCIS_INSTANCE_COVERAGE_UCISbranchCoverage', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 327, 0), )

    
    branchCoverage = property(__branchCoverage.value, __branchCoverage.set, None, None)

    
    # Element {UCIS}fsmCoverage uses Python identifier fsmCoverage
    __fsmCoverage = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'fsmCoverage'), 'fsmCoverage', '__UCIS_INSTANCE_COVERAGE_UCISfsmCoverage', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 329, 0), )

    
    fsmCoverage = property(__fsmCoverage.value, __fsmCoverage.set, None, None)

    
    # Element {UCIS}assertionCoverage uses Python identifier assertionCoverage
    __assertionCoverage = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'assertionCoverage'), 'assertionCoverage', '__UCIS_INSTANCE_COVERAGE_UCISassertionCoverage', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 331, 0), )

    
    assertionCoverage = property(__assertionCoverage.value, __assertionCoverage.set, None, None)

    
    # Element {UCIS}covergroupCoverage uses Python identifier covergroupCoverage
    __covergroupCoverage = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'covergroupCoverage'), 'covergroupCoverage', '__UCIS_INSTANCE_COVERAGE_UCIScovergroupCoverage', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 333, 0), )

    
    covergroupCoverage = property(__covergroupCoverage.value, __covergroupCoverage.set, None, None)

    
    # Element {UCIS}userAttr uses Python identifier userAttr
    __userAttr = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), 'userAttr', '__UCIS_INSTANCE_COVERAGE_UCISuserAttr', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 335, 0), )

    
    userAttr = property(__userAttr.value, __userAttr.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__UCIS_INSTANCE_COVERAGE_name', pyxb.binding.datatypes.string, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 338, 0)
    __name._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 338, 0)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute key uses Python identifier key
    __key = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'key'), 'key', '__UCIS_INSTANCE_COVERAGE_key', pyxb.binding.datatypes.string, required=True)
    __key._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 339, 0)
    __key._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 339, 0)
    
    key = property(__key.value, __key.set, None, None)

    
    # Attribute instanceId uses Python identifier instanceId
    __instanceId = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'instanceId'), 'instanceId', '__UCIS_INSTANCE_COVERAGE_instanceId', pyxb.binding.datatypes.integer)
    __instanceId._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 340, 0)
    __instanceId._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 340, 0)
    
    instanceId = property(__instanceId.value, __instanceId.set, None, None)

    
    # Attribute alias uses Python identifier alias
    __alias = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alias'), 'alias', '__UCIS_INSTANCE_COVERAGE_alias', pyxb.binding.datatypes.string)
    __alias._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 341, 0)
    __alias._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 341, 0)
    
    alias = property(__alias.value, __alias.set, None, None)

    
    # Attribute moduleName uses Python identifier moduleName
    __moduleName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'moduleName'), 'moduleName', '__UCIS_INSTANCE_COVERAGE_moduleName', pyxb.binding.datatypes.string)
    __moduleName._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 342, 0)
    __moduleName._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 342, 0)
    
    moduleName = property(__moduleName.value, __moduleName.set, None, None)

    
    # Attribute parentInstanceId uses Python identifier parentInstanceId
    __parentInstanceId = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'parentInstanceId'), 'parentInstanceId', '__UCIS_INSTANCE_COVERAGE_parentInstanceId', pyxb.binding.datatypes.integer)
    __parentInstanceId._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 343, 0)
    __parentInstanceId._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 343, 0)
    
    parentInstanceId = property(__parentInstanceId.value, __parentInstanceId.set, None, None)

    _ElementMap.update({
        __designParameter.name() : __designParameter,
        __id.name() : __id,
        __toggleCoverage.name() : __toggleCoverage,
        __blockCoverage.name() : __blockCoverage,
        __conditionCoverage.name() : __conditionCoverage,
        __branchCoverage.name() : __branchCoverage,
        __fsmCoverage.name() : __fsmCoverage,
        __assertionCoverage.name() : __assertionCoverage,
        __covergroupCoverage.name() : __covergroupCoverage,
        __userAttr.name() : __userAttr
    })
    _AttributeMap.update({
        __name.name() : __name,
        __key.name() : __key,
        __instanceId.name() : __instanceId,
        __alias.name() : __alias,
        __moduleName.name() : __moduleName,
        __parentInstanceId.name() : __parentInstanceId
    })
_module_typeBindings.INSTANCE_COVERAGE = INSTANCE_COVERAGE
Namespace.addCategoryObject('typeBinding', 'INSTANCE_COVERAGE', INSTANCE_COVERAGE)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    """Complex type [anonymous] with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 347, 0)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {UCIS}sourceFiles uses Python identifier sourceFiles
    __sourceFiles = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'sourceFiles'), 'sourceFiles', '__UCIS_CTD_ANON_UCISsourceFiles', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 349, 0), )

    
    sourceFiles = property(__sourceFiles.value, __sourceFiles.set, None, None)

    
    # Element {UCIS}historyNodes uses Python identifier historyNodes
    __historyNodes = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'historyNodes'), 'historyNodes', '__UCIS_CTD_ANON_UCIShistoryNodes', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 351, 0), )

    
    historyNodes = property(__historyNodes.value, __historyNodes.set, None, None)

    
    # Element {UCIS}instanceCoverages uses Python identifier instanceCoverages
    __instanceCoverages = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'instanceCoverages'), 'instanceCoverages', '__UCIS_CTD_ANON_UCISinstanceCoverages', True, pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 353, 0), )

    
    instanceCoverages = property(__instanceCoverages.value, __instanceCoverages.set, None, None)

    
    # Attribute ucisVersion uses Python identifier ucisVersion
    __ucisVersion = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'ucisVersion'), 'ucisVersion', '__UCIS_CTD_ANON_ucisVersion', pyxb.binding.datatypes.string, required=True)
    __ucisVersion._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 356, 0)
    __ucisVersion._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 356, 0)
    
    ucisVersion = property(__ucisVersion.value, __ucisVersion.set, None, None)

    
    # Attribute writtenBy uses Python identifier writtenBy
    __writtenBy = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'writtenBy'), 'writtenBy', '__UCIS_CTD_ANON_writtenBy', pyxb.binding.datatypes.string, required=True)
    __writtenBy._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 357, 0)
    __writtenBy._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 357, 0)
    
    writtenBy = property(__writtenBy.value, __writtenBy.set, None, None)

    
    # Attribute writtenTime uses Python identifier writtenTime
    __writtenTime = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'writtenTime'), 'writtenTime', '__UCIS_CTD_ANON_writtenTime', pyxb.binding.datatypes.dateTime, required=True)
    __writtenTime._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 358, 0)
    __writtenTime._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 358, 0)
    
    writtenTime = property(__writtenTime.value, __writtenTime.set, None, None)

    _ElementMap.update({
        __sourceFiles.name() : __sourceFiles,
        __historyNodes.name() : __historyNodes,
        __instanceCoverages.name() : __instanceCoverages
    })
    _AttributeMap.update({
        __ucisVersion.name() : __ucisVersion,
        __writtenBy.name() : __writtenBy,
        __writtenTime.name() : __writtenTime
    })
_module_typeBindings.CTD_ANON = CTD_ANON


# Complex type {UCIS}USER_ATTR with content type MIXED
class USER_ATTR (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {UCIS}USER_ATTR with content type MIXED"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'USER_ATTR')
    _XSDLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 13, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute key uses Python identifier key
    __key = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'key'), 'key', '__UCIS_USER_ATTR_key', pyxb.binding.datatypes.string, required=True)
    __key._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 14, 1)
    __key._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 14, 1)
    
    key = property(__key.value, __key.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__UCIS_USER_ATTR_type', _module_typeBindings.STD_ANON, required=True)
    __type._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 16, 1)
    __type._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 16, 1)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute len uses Python identifier len
    __len = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'len'), 'len', '__UCIS_USER_ATTR_len', pyxb.binding.datatypes.integer)
    __len._DeclarationLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 30, 1)
    __len._UseLocation = pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 30, 1)
    
    len = property(__len.value, __len.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __key.name() : __key,
        __type.name() : __type,
        __len.name() : __len
    })
_module_typeBindings.USER_ATTR = USER_ATTR
Namespace.addCategoryObject('typeBinding', 'USER_ATTR', USER_ATTR)


UCIS = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'UCIS'), CTD_ANON, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 346, 0))
Namespace.addCategoryObject('elementBinding', UCIS.name().localName(), UCIS)



NAME_VALUE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'name'), pyxb.binding.datatypes.string, scope=NAME_VALUE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 9, 1)))

NAME_VALUE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'value'), pyxb.binding.datatypes.string, scope=NAME_VALUE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 10, 1)))

def _BuildAutomaton ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton
    del _BuildAutomaton
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(NAME_VALUE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'name')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 9, 1))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(NAME_VALUE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'value')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 10, 1))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
NAME_VALUE._Automaton = _BuildAutomaton()




BIN_CONTENTS._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'historyNodeId'), pyxb.binding.datatypes.nonNegativeInteger, scope=BIN_CONTENTS, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 35, 1)))

def _BuildAutomaton_ ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_
    del _BuildAutomaton_
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 35, 1))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(BIN_CONTENTS._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'historyNodeId')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 35, 1))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
BIN_CONTENTS._Automaton = _BuildAutomaton_()




BIN._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'contents'), BIN_CONTENTS, scope=BIN, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 52, 1)))

BIN._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=BIN, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 53, 1)))

def _BuildAutomaton_2 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_2
    del _BuildAutomaton_2
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 53, 1))
    counters.add(cc_0)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(BIN._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'contents')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 52, 1))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(BIN._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 53, 1))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
BIN._Automaton = _BuildAutomaton_2()




HISTORY_NODE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=HISTORY_NODE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 536)))

def _BuildAutomaton_3 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_3
    del _BuildAutomaton_3
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 536))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(HISTORY_NODE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 536))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
HISTORY_NODE._Automaton = _BuildAutomaton_3()




TOGGLE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'bin'), BIN, scope=TOGGLE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2383)))

def _BuildAutomaton_4 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_4
    del _BuildAutomaton_4
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(TOGGLE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'bin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2383))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
TOGGLE._Automaton = _BuildAutomaton_4()




TOGGLE_BIT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'index'), pyxb.binding.datatypes.nonNegativeInteger, scope=TOGGLE_BIT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2655)))

TOGGLE_BIT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'toggle'), TOGGLE, scope=TOGGLE_BIT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2748)))

TOGGLE_BIT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=TOGGLE_BIT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2826)))

def _BuildAutomaton_5 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_5
    del _BuildAutomaton_5
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2655))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2826))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TOGGLE_BIT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'index')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2655))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(TOGGLE_BIT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'toggle')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2748))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(TOGGLE_BIT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 2826))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
TOGGLE_BIT._Automaton = _BuildAutomaton_5()




TOGGLE_OBJECT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'dimension'), DIMENSION, scope=TOGGLE_OBJECT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 3193)))

TOGGLE_OBJECT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'id'), STATEMENT_ID, scope=TOGGLE_OBJECT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 0)))

TOGGLE_OBJECT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'toggleBit'), TOGGLE_BIT, scope=TOGGLE_OBJECT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 44)))

TOGGLE_OBJECT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=TOGGLE_OBJECT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 129)))

def _BuildAutomaton_6 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_6
    del _BuildAutomaton_6
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 3193))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 129))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TOGGLE_OBJECT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'dimension')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 65, 3193))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TOGGLE_OBJECT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'id')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 0))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(TOGGLE_OBJECT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'toggleBit')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 44))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(TOGGLE_OBJECT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 129))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
TOGGLE_OBJECT._Automaton = _BuildAutomaton_6()




METRIC_MODE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=METRIC_MODE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 594)))

def _BuildAutomaton_7 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_7
    del _BuildAutomaton_7
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 594))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(METRIC_MODE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 594))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
METRIC_MODE._Automaton = _BuildAutomaton_7()




TOGGLE_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'toggleObject'), TOGGLE_OBJECT, scope=TOGGLE_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 870)))

TOGGLE_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'metricMode'), METRIC_MODE, scope=TOGGLE_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 961)))

TOGGLE_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=TOGGLE_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1048)))

def _BuildAutomaton_8 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_8
    del _BuildAutomaton_8
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 870))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 961))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1048))
    counters.add(cc_2)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(TOGGLE_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'toggleObject')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 870))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(TOGGLE_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'metricMode')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 961))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(TOGGLE_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1048))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
TOGGLE_COVERAGE._Automaton = _BuildAutomaton_8()




STATEMENT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'id'), STATEMENT_ID, scope=STATEMENT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1814)))

STATEMENT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'bin'), BIN, scope=STATEMENT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1858)))

STATEMENT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=STATEMENT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1894)))

def _BuildAutomaton_9 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_9
    del _BuildAutomaton_9
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1894))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(STATEMENT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'id')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1814))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(STATEMENT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'bin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1858))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(STATEMENT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 1894))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
STATEMENT._Automaton = _BuildAutomaton_9()




BLOCK._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'statementId'), STATEMENT_ID, scope=BLOCK, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2124)))

BLOCK._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'hierarchicalBlock'), BLOCK, scope=BLOCK, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2213)))

BLOCK._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'blockBin'), BIN, scope=BLOCK, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2301)))

BLOCK._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'blockId'), STATEMENT_ID, scope=BLOCK, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2342)))

BLOCK._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=BLOCK, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2391)))

def _BuildAutomaton_10 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_10
    del _BuildAutomaton_10
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2124))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2213))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2391))
    counters.add(cc_2)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(BLOCK._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'statementId')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2124))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(BLOCK._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'hierarchicalBlock')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2213))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(BLOCK._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'blockBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2301))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(BLOCK._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'blockId')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2342))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(BLOCK._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2391))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
BLOCK._Automaton = _BuildAutomaton_10()




PROCESS_BLOCK._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'block'), BLOCK, scope=PROCESS_BLOCK, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2692)))

PROCESS_BLOCK._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=PROCESS_BLOCK, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 0)))

def _BuildAutomaton_11 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_11
    del _BuildAutomaton_11
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2692))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 0))
    counters.add(cc_1)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(PROCESS_BLOCK._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'block')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 68, 2692))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(PROCESS_BLOCK._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 0))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
PROCESS_BLOCK._Automaton = _BuildAutomaton_11()




BLOCK_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'process'), PROCESS_BLOCK, scope=BLOCK_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 328)))

BLOCK_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'block'), BLOCK, scope=BLOCK_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 414)))

BLOCK_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'statement'), STATEMENT, scope=BLOCK_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 490)))

BLOCK_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=BLOCK_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 587)))

def _BuildAutomaton_12 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_12
    del _BuildAutomaton_12
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 587))
    counters.add(cc_0)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(BLOCK_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'process')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 328))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(BLOCK_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'block')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 414))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(BLOCK_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'statement')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 490))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(BLOCK_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 587))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
BLOCK_COVERAGE._Automaton = _BuildAutomaton_12()




EXPR._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'id'), STATEMENT_ID, scope=EXPR, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 818)))

EXPR._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'subExpr'), pyxb.binding.datatypes.string, scope=EXPR, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 862)))

EXPR._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'bin'), BIN, scope=EXPR, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 945)))

EXPR._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'hierarchicalExpr'), EXPR, scope=EXPR, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1017)))

EXPR._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=EXPR, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1103)))

def _BuildAutomaton_13 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_13
    del _BuildAutomaton_13
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1017))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1103))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(EXPR._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'id')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 818))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(EXPR._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'subExpr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 862))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(EXPR._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'bin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 945))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(EXPR._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'hierarchicalExpr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1017))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(EXPR._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1103))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_4._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
EXPR._Automaton = _BuildAutomaton_13()




CONDITION_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'expr'), EXPR, scope=CONDITION_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1750)))

CONDITION_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=CONDITION_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1824)))

def _BuildAutomaton_14 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_14
    del _BuildAutomaton_14
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1750))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1824))
    counters.add(cc_1)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CONDITION_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'expr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1750))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(CONDITION_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 1824))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
CONDITION_COVERAGE._Automaton = _BuildAutomaton_14()




BRANCH._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'id'), STATEMENT_ID, scope=BRANCH, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2059)))

BRANCH._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'nestedBranch'), BRANCH_STATEMENT, scope=BRANCH, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2103)))

BRANCH._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'branchBin'), BIN, scope=BRANCH, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2197)))

BRANCH._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=BRANCH, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2239)))

def _BuildAutomaton_15 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_15
    del _BuildAutomaton_15
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2103))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2239))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(BRANCH._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'id')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2059))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(BRANCH._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'nestedBranch')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2103))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(BRANCH._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'branchBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2197))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(BRANCH._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2239))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
BRANCH._Automaton = _BuildAutomaton_15()




BRANCH_STATEMENT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'id'), STATEMENT_ID, scope=BRANCH_STATEMENT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2450)))

BRANCH_STATEMENT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'branch'), BRANCH, scope=BRANCH_STATEMENT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2494)))

BRANCH_STATEMENT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=BRANCH_STATEMENT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2572)))

def _BuildAutomaton_16 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_16
    del _BuildAutomaton_16
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2494))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2572))
    counters.add(cc_1)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(BRANCH_STATEMENT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'id')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2450))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(BRANCH_STATEMENT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'branch')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2494))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(BRANCH_STATEMENT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 71, 2572))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
BRANCH_STATEMENT._Automaton = _BuildAutomaton_16()




BRANCH_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'statement'), BRANCH_STATEMENT, scope=BRANCH_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 80, 0)))

BRANCH_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=BRANCH_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 82, 0)))

def _BuildAutomaton_17 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_17
    del _BuildAutomaton_17
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 80, 0))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 82, 0))
    counters.add(cc_1)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(BRANCH_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'statement')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 80, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(BRANCH_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 82, 0))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
BRANCH_COVERAGE._Automaton = _BuildAutomaton_17()




FSM_STATE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'stateBin'), BIN, scope=FSM_STATE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 90, 0)))

FSM_STATE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=FSM_STATE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 91, 0)))

def _BuildAutomaton_18 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_18
    del _BuildAutomaton_18
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 91, 0))
    counters.add(cc_0)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(FSM_STATE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'stateBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 90, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(FSM_STATE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 91, 0))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
FSM_STATE._Automaton = _BuildAutomaton_18()




FSM_TRANSITION._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'state'), pyxb.binding.datatypes.string, scope=FSM_TRANSITION, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 100, 0)))

FSM_TRANSITION._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'transitionBin'), BIN, scope=FSM_TRANSITION, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 102, 0)))

FSM_TRANSITION._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=FSM_TRANSITION, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 103, 0)))

def _BuildAutomaton_19 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_19
    del _BuildAutomaton_19
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=2, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 100, 0))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 103, 0))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FSM_TRANSITION._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'state')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 100, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(FSM_TRANSITION._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'transitionBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 102, 0))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(FSM_TRANSITION._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 103, 0))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
FSM_TRANSITION._Automaton = _BuildAutomaton_19()




FSM._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'state'), FSM_STATE, scope=FSM, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 110, 0)))

FSM._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'stateTransition'), FSM_TRANSITION, scope=FSM, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 112, 0)))

FSM._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=FSM, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 114, 0)))

def _BuildAutomaton_20 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_20
    del _BuildAutomaton_20
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 110, 0))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 112, 0))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 114, 0))
    counters.add(cc_2)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(FSM._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'state')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 110, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(FSM._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'stateTransition')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 112, 0))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(FSM._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 114, 0))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
FSM._Automaton = _BuildAutomaton_20()




FSM_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'fsm'), FSM, scope=FSM_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 125, 0)))

FSM_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=FSM_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 127, 0)))

def _BuildAutomaton_21 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_21
    del _BuildAutomaton_21
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 125, 0))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 127, 0))
    counters.add(cc_1)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(FSM_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'fsm')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 125, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(FSM_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 127, 0))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
FSM_COVERAGE._Automaton = _BuildAutomaton_21()




ASSERTION._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'coverBin'), BIN, scope=ASSERTION, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 135, 0)))

ASSERTION._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'passBin'), BIN, scope=ASSERTION, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 137, 0)))

ASSERTION._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'failBin'), BIN, scope=ASSERTION, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 139, 0)))

ASSERTION._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'vacuousBin'), BIN, scope=ASSERTION, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 141, 0)))

ASSERTION._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'disabledBin'), BIN, scope=ASSERTION, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 143, 0)))

ASSERTION._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'attemptBin'), BIN, scope=ASSERTION, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 145, 0)))

ASSERTION._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'activeBin'), BIN, scope=ASSERTION, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 147, 0)))

ASSERTION._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'peakActiveBin'), BIN, scope=ASSERTION, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 150, 0)))

ASSERTION._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=ASSERTION, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 152, 0)))

def _BuildAutomaton_22 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_22
    del _BuildAutomaton_22
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 135, 0))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 137, 0))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 139, 0))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 141, 0))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 143, 0))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 145, 0))
    counters.add(cc_5)
    cc_6 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 147, 0))
    counters.add(cc_6)
    cc_7 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 150, 0))
    counters.add(cc_7)
    cc_8 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 152, 0))
    counters.add(cc_8)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(ASSERTION._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'coverBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 135, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(ASSERTION._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'passBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 137, 0))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(ASSERTION._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'failBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 139, 0))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(ASSERTION._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'vacuousBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 141, 0))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(ASSERTION._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'disabledBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 143, 0))
    st_4 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_5, False))
    symbol = pyxb.binding.content.ElementUse(ASSERTION._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'attemptBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 145, 0))
    st_5 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_6, False))
    symbol = pyxb.binding.content.ElementUse(ASSERTION._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'activeBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 147, 0))
    st_6 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(ASSERTION._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'peakActiveBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 150, 0))
    st_7 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_8, False))
    symbol = pyxb.binding.content.ElementUse(ASSERTION._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 152, 0))
    st_8 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_5, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_5, False) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_6, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_6, False) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, False) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_8, True) ]))
    st_8._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
ASSERTION._Automaton = _BuildAutomaton_22()




ASSERTION_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'assertion'), ASSERTION, scope=ASSERTION_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 162, 0)))

ASSERTION_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=ASSERTION_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 164, 0)))

def _BuildAutomaton_23 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_23
    del _BuildAutomaton_23
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 162, 0))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 164, 0))
    counters.add(cc_1)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(ASSERTION_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'assertion')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 162, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(ASSERTION_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 164, 0))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
ASSERTION_COVERAGE._Automaton = _BuildAutomaton_23()




SEQUENCE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'contents'), BIN_CONTENTS, scope=SEQUENCE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 172, 0)))

SEQUENCE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'seqValue'), pyxb.binding.datatypes.integer, scope=SEQUENCE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 173, 0)))

def _BuildAutomaton_24 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_24
    del _BuildAutomaton_24
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SEQUENCE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'contents')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 172, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(SEQUENCE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'seqValue')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 173, 0))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
SEQUENCE._Automaton = _BuildAutomaton_24()




RANGE_VALUE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'contents'), BIN_CONTENTS, scope=RANGE_VALUE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 180, 0)))

def _BuildAutomaton_25 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_25
    del _BuildAutomaton_25
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(RANGE_VALUE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'contents')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 180, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
RANGE_VALUE._Automaton = _BuildAutomaton_25()




COVERPOINT_BIN._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'range'), RANGE_VALUE, scope=COVERPOINT_BIN, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 189, 0)))

COVERPOINT_BIN._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'sequence'), SEQUENCE, scope=COVERPOINT_BIN, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 191, 0)))

COVERPOINT_BIN._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=COVERPOINT_BIN, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 194, 0)))

def _BuildAutomaton_26 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_26
    del _BuildAutomaton_26
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 194, 0))
    counters.add(cc_0)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(COVERPOINT_BIN._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'range')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 189, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(COVERPOINT_BIN._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'sequence')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 191, 0))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(COVERPOINT_BIN._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 194, 0))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
COVERPOINT_BIN._Automaton = _BuildAutomaton_26()




CROSS_BIN._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'index'), pyxb.binding.datatypes.integer, scope=CROSS_BIN, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 203, 0)))

CROSS_BIN._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'contents'), BIN_CONTENTS, scope=CROSS_BIN, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 205, 0)))

CROSS_BIN._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=CROSS_BIN, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 206, 0)))

def _BuildAutomaton_27 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_27
    del _BuildAutomaton_27
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 206, 0))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CROSS_BIN._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'index')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 203, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CROSS_BIN._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'contents')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 205, 0))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CROSS_BIN._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 206, 0))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CROSS_BIN._Automaton = _BuildAutomaton_27()




CROSS._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'options'), CROSS_OPTIONS, scope=CROSS, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 226, 0)))

CROSS._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'crossExpr'), pyxb.binding.datatypes.string, scope=CROSS, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 227, 0)))

CROSS._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'crossBin'), CROSS_BIN, scope=CROSS, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 229, 0)))

CROSS._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=CROSS, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 231, 0)))

def _BuildAutomaton_28 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_28
    del _BuildAutomaton_28
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 227, 0))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 229, 0))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 231, 0))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CROSS._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'options')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 226, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CROSS._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'crossExpr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 227, 0))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(CROSS._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'crossBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 229, 0))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(CROSS._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 231, 0))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CROSS._Automaton = _BuildAutomaton_28()




COVERPOINT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'options'), COVERPOINT_OPTIONS, scope=COVERPOINT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 250, 0)))

COVERPOINT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'coverpointBin'), COVERPOINT_BIN, scope=COVERPOINT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 251, 0)))

COVERPOINT._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=COVERPOINT, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 253, 0)))

def _BuildAutomaton_29 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_29
    del _BuildAutomaton_29
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 253, 0))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(COVERPOINT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'options')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 250, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(COVERPOINT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'coverpointBin')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 251, 0))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(COVERPOINT._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 253, 0))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
COVERPOINT._Automaton = _BuildAutomaton_29()




CG_ID._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'cginstSourceId'), STATEMENT_ID, scope=CG_ID, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 264, 0)))

CG_ID._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'cgSourceId'), STATEMENT_ID, scope=CG_ID, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 265, 0)))

def _BuildAutomaton_30 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_30
    del _BuildAutomaton_30
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CG_ID._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'cginstSourceId')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 264, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CG_ID._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'cgSourceId')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 265, 0))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CG_ID._Automaton = _BuildAutomaton_30()




CGINSTANCE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'options'), CGINST_OPTIONS, scope=CGINSTANCE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 286, 0)))

CGINSTANCE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'cgId'), CG_ID, scope=CGINSTANCE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 287, 0)))

CGINSTANCE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'cgParms'), NAME_VALUE, scope=CGINSTANCE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 288, 0)))

CGINSTANCE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'coverpoint'), COVERPOINT, scope=CGINSTANCE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 290, 0)))

CGINSTANCE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'cross'), CROSS, scope=CGINSTANCE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 292, 0)))

CGINSTANCE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=CGINSTANCE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 294, 0)))

def _BuildAutomaton_31 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_31
    del _BuildAutomaton_31
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 288, 0))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 292, 0))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 294, 0))
    counters.add(cc_2)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CGINSTANCE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'options')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 286, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CGINSTANCE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'cgId')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 287, 0))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CGINSTANCE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'cgParms')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 288, 0))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CGINSTANCE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'coverpoint')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 290, 0))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(CGINSTANCE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'cross')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 292, 0))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(CGINSTANCE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 294, 0))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_5._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CGINSTANCE._Automaton = _BuildAutomaton_31()




COVERGROUP_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'cgInstance'), CGINSTANCE, scope=COVERGROUP_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 308, 0)))

COVERGROUP_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=COVERGROUP_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 310, 0)))

def _BuildAutomaton_32 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_32
    del _BuildAutomaton_32
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 308, 0))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 310, 0))
    counters.add(cc_1)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(COVERGROUP_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'cgInstance')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 308, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(COVERGROUP_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 310, 0))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
COVERGROUP_COVERAGE._Automaton = _BuildAutomaton_32()




INSTANCE_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'designParameter'), NAME_VALUE, scope=INSTANCE_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 318, 0)))

INSTANCE_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'id'), STATEMENT_ID, scope=INSTANCE_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 320, 0)))

INSTANCE_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'toggleCoverage'), TOGGLE_COVERAGE, scope=INSTANCE_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 321, 0)))

INSTANCE_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'blockCoverage'), BLOCK_COVERAGE, scope=INSTANCE_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 323, 0)))

INSTANCE_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'conditionCoverage'), CONDITION_COVERAGE, scope=INSTANCE_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 325, 0)))

INSTANCE_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'branchCoverage'), BRANCH_COVERAGE, scope=INSTANCE_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 327, 0)))

INSTANCE_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'fsmCoverage'), FSM_COVERAGE, scope=INSTANCE_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 329, 0)))

INSTANCE_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'assertionCoverage'), ASSERTION_COVERAGE, scope=INSTANCE_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 331, 0)))

INSTANCE_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'covergroupCoverage'), COVERGROUP_COVERAGE, scope=INSTANCE_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 333, 0)))

INSTANCE_COVERAGE._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userAttr'), USER_ATTR, scope=INSTANCE_COVERAGE, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 335, 0)))

def _BuildAutomaton_33 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_33
    del _BuildAutomaton_33
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 318, 0))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 321, 0))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 323, 0))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 325, 0))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 327, 0))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 329, 0))
    counters.add(cc_5)
    cc_6 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 331, 0))
    counters.add(cc_6)
    cc_7 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 333, 0))
    counters.add(cc_7)
    cc_8 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 335, 0))
    counters.add(cc_8)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(INSTANCE_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'designParameter')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 318, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(INSTANCE_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'id')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 320, 0))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(INSTANCE_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'toggleCoverage')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 321, 0))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(INSTANCE_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'blockCoverage')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 323, 0))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(INSTANCE_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'conditionCoverage')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 325, 0))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(INSTANCE_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'branchCoverage')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 327, 0))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_5, False))
    symbol = pyxb.binding.content.ElementUse(INSTANCE_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'fsmCoverage')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 329, 0))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_6, False))
    symbol = pyxb.binding.content.ElementUse(INSTANCE_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'assertionCoverage')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 331, 0))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(INSTANCE_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'covergroupCoverage')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 333, 0))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_8, False))
    symbol = pyxb.binding.content.ElementUse(INSTANCE_COVERAGE._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userAttr')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 335, 0))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_5, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_5, False) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_6, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_6, False) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, False) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_8, True) ]))
    st_9._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
INSTANCE_COVERAGE._Automaton = _BuildAutomaton_33()




CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'sourceFiles'), SOURCE_FILE, scope=CTD_ANON, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 349, 0)))

CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'historyNodes'), HISTORY_NODE, scope=CTD_ANON, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 351, 0)))

CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'instanceCoverages'), INSTANCE_COVERAGE, scope=CTD_ANON, location=pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 353, 0)))

def _BuildAutomaton_34 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_34
    del _BuildAutomaton_34
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'sourceFiles')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 349, 0))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'historyNodes')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 351, 0))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'instanceCoverages')), pyxb.utils.utility.Location('/project/fun/py-vsc/py-vsc/packages/pyucis/schema/ucis.xsd', 353, 0))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON._Automaton = _BuildAutomaton_34()




def _BuildAutomaton_35 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_35
    del _BuildAutomaton_35
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    return fac.Automaton(states, counters, True, containing_state=None)
USER_ATTR._Automaton = _BuildAutomaton_35()

