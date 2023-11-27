#!/usr/bin/python3

import dnfile
from dnfile import dnPE
from dnfile.mdtable import MethodDefRow
from dnfile.enums import MetadataTables


from dncil.cil.body import CilMethodBody
from dncil.clr.token import Token, StringToken, InvalidToken
from typing import TYPE_CHECKING, Any, Union, Optional
from dncil.cil.error import MethodBodyFormatError
from dncil.cil.body.reader import CilMethodBodyReaderBase

import os
from zipfile import ZipFile
import hashlib
import shutil
import sys

# key token indexes to dotnet meta tables
DOTNET_META_TABLES_BY_INDEX = {table.value: table.name for table in MetadataTables}

class DnfileMethodBodyReader(CilMethodBodyReaderBase):
	def __init__(self, pe: dnPE, row: MethodDefRow):
		""" """
		self.pe: dnPE = pe
		self.offset: int = self.pe.get_offset_from_rva(row.Rva)

	def read(self, n: int) -> bytes:
		""" """
		data: bytes = self.pe.get_data(self.pe.get_rva_from_offset(self.offset), n)
		self.offset += n
		return data

	def tell(self) -> int:
		""" """
		return self.offset

	def seek(self, offset: int) -> int:
		""" """
		self.offset = offset
		return self.offset


def read_dotnet_user_string(pe: dnfile.dnPE, token: StringToken) -> Union[str, InvalidToken]:
	"""read user string from #US stream"""
	try:
		user_string: Optional[dnfile.stream.UserString] = pe.net.user_strings.get_us(token.rid)
	except UnicodeDecodeError as e:
		return InvalidToken(token.value)

	if user_string is None:
		return InvalidToken(token.value)

	return user_string.value


def resolve_token(pe: dnPE, token: Token) -> Any:
	""" """
	if isinstance(token, StringToken):
		return read_dotnet_user_string(pe, token)

	table_name: str = DOTNET_META_TABLES_BY_INDEX.get(token.table, "")
	if not table_name:
		# table_index is not valid
		return InvalidToken(token.value)

	table: Any = getattr(pe.net.mdtables, table_name, None)
	if table is None:
		# table index is valid but table is not present
		return InvalidToken(token.value)

	try:
		return table.rows[token.rid - 1]
	except IndexError:
		# table index is valid but row index is not valid
		return InvalidToken(token.value)

def read_method_body(pe: dnPE, row: MethodDefRow) -> CilMethodBody:
	""" """
	return CilMethodBody(DnfileMethodBodyReader(pe, row))


def format_operand(pe: dnPE, operand: Any) -> str:
	""" """
	if isinstance(operand, Token):
		operand = resolve_token(pe, operand)

	if isinstance(operand, str):
		return f'"{operand}"'
	elif isinstance(operand, int):
		return hex(operand)
	elif isinstance(operand, list):
		return f"[{', '.join(['({:04X})'.format(x) for x in operand])}]"
	elif isinstance(operand, dnfile.mdtable.MemberRefRow):
		if isinstance(operand.Class.row, (dnfile.mdtable.TypeRefRow,)):
			return f"{str(operand.Class.row.TypeNamespace)}.{operand.Class.row.TypeName}::{operand.Name}"
	elif isinstance(operand, dnfile.mdtable.TypeRefRow):
		return f"{str(operand.TypeNamespace)}.{operand.TypeName}"
	elif isinstance(operand, (dnfile.mdtable.FieldRow, dnfile.mdtable.MethodDefRow)):
		return f"{operand.Name}"
	elif operand is None:
		return ""

	return str(operand)


def process_dll(dllname):
	d = dnfile.dnPE(dllname)

	dirname = "export_%s" % dllname
	for res in d.net.resources:
		print("Resource", res)
		for resfile in res.data.entries:
			print("Resource file", resfile)
			
			if not resfile.data:
				continue
			
			lastChar = None
			index = 0
			#print(type(resfile.data))
			for byte in resfile.data:
				if lastChar and lastChar == ord("P") and byte == ord("K"):
					#ZIP!
					print("Found ZIP file!")
					
					try:
						shutil.rmtree(dirname)
					except Exception as e:
						pass
					
					os.mkdir(dirname)
					with open("./%s/out.zip" % dirname, "wb+") as f:
						f.write(resfile.data[index-1:])
						
					break

				if index > 100:
					break
				
				lastChar = byte
				index += 1

	result = {}


	for row in d.net.mdtables.MethodDef:
		#print("Method", row.Name)
		name = row.Name

		try:
			body: CilMethodBody = read_method_body(d, row)
		except MethodBodyFormatError as e:
			print(e)
			continue
		
		lastData = None
		for ins in body.instructions:
			op = format_operand(d, ins.operand)
			if name == "get_getEXEname" and op:
				result["getEXEname"] = op[1:-1]
			
			if name == "get_getEXEversion" and op:
				result["getEXEversion"] = op[1:-1]
			
			if name == "get_getPluginID" and op:
				result["getPluginID"] = int(op, 16)
			
			if op == "plugindatapassword" and lastData and "plugindatapassword" not in result:
				result["plugindatapassword"] = lastData[1:-1]
			
			lastData = op

	print("Result", result)

	#fuck them ZIP
	base = result["plugindatapassword"] + str(result["getPluginID"]) + result["getEXEname"] + result["getEXEversion"]
	pw = hashlib.md5(base.encode("ascii")).hexdigest().upper()

	print("ZIP password", pw)

	with ZipFile("./%s/out.zip" % dirname) as zf:
		zf.extractall("./%s" % dirname, pwd=pw.encode("ascii"))
		
	for currentpath, folders, files in os.walk('./%s' % dirname):
		for file in files:
			print(os.path.join(currentpath, file))
		
	print("DONE")


if __name__ == "__main__":
	process_dll(sys.argv[1])
	
	
