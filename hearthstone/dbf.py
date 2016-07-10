from collections import OrderedDict
from xml.etree import ElementTree


class Dbf:
	@classmethod
	def load(cls, filename):
		ret = cls()
		with open(filename, "r") as f:
			ret.populate(f)
		return ret

	def __init__(self):
		self.name = None
		self.source_fingerprint = None

	def __repr__(self):
		return "<%s: %s>" % (self.__class__.__name__, self.name)

	@property
	def records(self):
		for e in self.xml.findall("Record"):
			yield self._deserialize_record(e)

	def populate(self, file):
		self.xml = ElementTree.parse(file)
		self.name = self.xml.getroot().attrib.get("name", "")
		self.columns = OrderedDict()
		for column in self.xml.findall("Column"):
			self.columns[column.attrib["name"]] = column.attrib["type"]

		for fingerprint in self.xml.findall("SourceFingerprint"):
			self.source_fingerprint = fingerprint.text

	def _deserialize_record(self, element):
		ret = {}
		for field in element.findall("Field"):
			colname = field.attrib["column"]
			coltype = self.columns[colname]
			ret[colname] = self._deserialize_value(field, coltype)

		return ret

	def _deserialize_value(self, element, coltype):
		if element.text is None:
			return
		if coltype in ("Int", "Long", "ULong"):
			return int(element.text)
		elif coltype == "Bool":
			return element.text == "True"
		elif coltype in ("String", "AssetPath"):
			return element.text
		elif coltype == "LocString":
			return {e.tag: e.text for e in element}
		raise NotImplementedError("Unknown DBF Data Type: %r" % (coltype))
