from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import hashlib
import csv
import argparse
import os
from reportlab.lib.units import inch


parser = argparse.ArgumentParser(description='Generator sertifikat, author: LombokDev')
parser.add_argument('--data', type=str, required=True, help='data peserta path')
parser.add_argument('--template', type=str, required=True, help='template pdf path')
parser.add_argument('--out_path', type=str, required=True, help='output path')
parser.add_argument('--alignment', type=int, default=3, help='1 untuk kiri, 2 untuk tengah, 3 untuk kanan')
parser.add_argument('--xy', type=str, required=True, help='Center x dan y dalam inci. misal: 5,2.3 (tanpa spasi)')
parser.add_argument('--font_face', type=str, default="Helvetica", help='Jenis fonts')
parser.add_argument('--font_size', type=int, default="20", help='Ukuran fonts')
parser.add_argument('--fullname_column', type=str, default="FULLNAME", help='Ukuran fonts')
args = parser.parse_args()


def read_tsv(filename):
	"""
	Reader function to handle some file such as tsv, csv
	dict_result = read_cst()

	"""
	datas = []
	with open(filename) as _file:
		_reader = csv.DictReader(_file, dialect='excel-tab')
		for row in _reader:
			datas.append(row)
	return datas


def encode(attendant_name):
	"""
		Encode filename. Using:
		- Lowercase the attendant name
		- Remove space
		- then hash it using md5
	"""
	lower_name = attendant_name.lower()
	no_space = attendant_name.replace(' ','').encode('utf-8')
	hashed = hashlib.md5(no_space)

	return hashed.hexdigest()



data_peserta = read_tsv(args.data)

# read your existing PDF


x, y = map(float, args.xy.split(','))


for peserta in data_peserta:

	nama_peserta = peserta[args.fullname_column]
	
	print("writing for: ", nama_peserta)

	packet = io.BytesIO()
	

	can = canvas.Canvas(packet, pagesize=letter)
	can.setFont(args.font_face, args.font_size)

	if args.alignment == 1: # rata kiri
		can.drawString(x, y, nama_peserta)	
	if args.alignment == 2: # rata tengah
		can.drawCentredString(x, y, nama_peserta)	
	if args.alignment == 3: # rata kanan
		print(x,y, type(x), type(y))
		can.drawRightString(x*inch, y*inch, nama_peserta)	
	
	can.save()

	packet.seek(0)
	new_pdf = PdfFileReader(packet)

	existing_pdf = PdfFileReader(open(args.template, "rb"))

	output = PdfFileWriter()
	# add the "watermark" (which is the new pdf) on the existing page
	page = existing_pdf.getPage(0)
	page.mergePage(new_pdf.getPage(0))
	output.addPage(page)

	hashed = encode(nama_peserta)
	
	print("output filename: ", hashed)
	
	# finally, write "output" to a real file
	outputStream = open(os.path.join(args.out_path, hashed + ".pdf"), "wb")
	output.write(outputStream)
	outputStream.close()

