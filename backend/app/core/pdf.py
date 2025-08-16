from __future__ import annotations

from io import BytesIO
from typing import List, TypedDict, Literal

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, HRFlowable


def extract_first_two_pages_text(file_bytes: bytes) -> str:
	"""Extract text from the first two pages of a PDF.

	If the PDF has fewer than two pages, extract whatever is available.
	Returns a best-effort plain text string.
	"""
	buffer = BytesIO(file_bytes)
	reader = PdfReader(buffer)

	pages_to_read: List[int] = []
	if len(reader.pages) > 0:
		pages_to_read.append(0)
	if len(reader.pages) > 1:
		pages_to_read.append(1)

	texts: List[str] = []
	for page_index in pages_to_read:
		page = reader.pages[page_index]
		text = page.extract_text() or ""
		texts.append(text.strip())

	return "\n\n".join([t for t in texts if t])


# --- PDF rendering ---
BlockType = Literal['heading', 'subheading', 'meta', 'paragraph', 'list']

class ParsedBlock(TypedDict, total=False):
	type: BlockType
	text: str
	items: List[str]

class ParsedSection(TypedDict):
	blocks: List[ParsedBlock]


def _register_base_fonts() -> None:
	# Use built-in Helvetica stack to avoid bundling fonts; register for bold/italic variants
	try:
		pdfmetrics.registerFont(TTFont('Inter', 'Inter.ttf'))  # optional if available
	except Exception:
		# Fallback to Helvetica family present in most PDF readers
		pass


def render_cv_pdf_from_sections(sections: List[ParsedSection], title: str = "Curriculum Vitae") -> bytes:
	buffer = BytesIO()
	_doc = SimpleDocTemplate(
		buffer,
		pagesize=letter,
		leftMargin=0.8 * inch,
		rightMargin=0.8 * inch,
		topMargin=0.8 * inch,
		bottomMargin=0.8 * inch,
	)

	styles = getSampleStyleSheet()
	# Base styles
	styles.add(ParagraphStyle(name='CVTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, spaceAfter=8, textColor=colors.HexColor('#0f172a')))
	styles.add(ParagraphStyle(name='SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor('#0f172a')))
	styles.add(ParagraphStyle(name='Subheading', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=10.5, textColor=colors.HexColor('#334155')))
	styles.add(ParagraphStyle(name='Meta', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, textColor=colors.HexColor('#64748b')))
	styles.add(ParagraphStyle(name='Body', parent=styles['Normal'], fontName='Helvetica', fontSize=10.5, leading=14))
	bullet_style = ParagraphStyle(name='Bullet', parent=styles['Body'], leftIndent=12)

	story: List[object] = []

	# Title
	story.append(Paragraph(title, styles['CVTitle']))
	story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#dbe7ff')))
	story.append(Spacer(1, 8))

	def _render_inline(text: str) -> str:
		# Basic markdown-like conversion for **bold** and *italic*
		# ReportLab uses <b></b> and <i></i> in its mini markup
		out = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
		# bold
		import re
		out = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", out)
		# italic
		out = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", out)
		return out

	for section in sections:
		for block in section.get('blocks', []):
			btype: BlockType = block.get('type', 'paragraph')  # type: ignore
			if btype == 'heading':
				text = _render_inline((block.get('text') or '').strip())
				if text:
					story.append(Spacer(1, 6))
					story.append(Paragraph(text, styles['SectionHeading']))
			elif btype == 'subheading':
				text = _render_inline((block.get('text') or '').strip())
				if text:
					story.append(Paragraph(text, styles['Subheading']))
			elif btype == 'meta':
				text = _render_inline((block.get('text') or '').strip())
				if text:
					story.append(Paragraph(text, styles['Meta']))
			elif btype == 'paragraph':
				text = _render_inline((block.get('text') or '').strip())
				if text:
					story.append(Paragraph(text, styles['Body']))
			elif btype == 'list':
				items = block.get('items') or []
				if items:
					lf = ListFlowable(
						[ListItem(Paragraph(_render_inline(it), styles['Body'])) for it in items],
						bulletType='bullet',
						start='•',
						leftIndent=12,
					)
					story.append(lf)
		# space between sections
		story.append(Spacer(1, 6))

	_doc.build(story)
	pdf_bytes = buffer.getvalue()
	buffer.close()
	return pdf_bytes


def parse_text_to_sections(text: str) -> List[ParsedSection]:
	"""Mirror the frontend parsing to keep formatting consistent for PDF."""
	lines = [ln.strip() for ln in text.splitlines()]
	sections: List[ParsedSection] = []
	current: ParsedSection | None = None

	import re
	def start_section() -> None:
		nonlocal current
		if current is None:
			current = {'blocks': []}

	def push_section_if_not_empty() -> None:
		nonlocal current
		if current and current['blocks']:
			sections.append(current)
			current = None

	is_bold_heading = lambda line: re.match(r'^(?:##\s+|\*\*[^*]+\*\*)$', line) is not None
	extract_heading_text = lambda line: re.sub(r'^##\s+', '', re.sub(r'^\*\*|\*\*$', '', line))
	is_italic_solo = lambda line: re.match(r'^\*[^*]+\*$', line) is not None
	extract_italic_text = lambda line: re.sub(r'^\*|\*$', '', line)
	is_meta_date = lambda line: re.search(r'(\b\d{4}\b\s*[–-]\s*(?:\b\d{4}\b|Present))|([A-Za-z]{3,9}\s+\d{4}\s*[–-]\s*(?:[A-Za-z]{3,9}\s+)?(?:\d{4}|Present))', line, re.I) is not None
	is_bullet = lambda line: re.match(r'^[-•]\s+', line) is not None

	for raw in lines:
		if not raw:
			continue
		if is_bold_heading(raw):
			push_section_if_not_empty()
			current = {'blocks': [{'type': 'heading', 'text': extract_heading_text(raw)}]}
			continue
		if current is None:
			start_section()
		if is_italic_solo(raw):
			current['blocks'].append({'type': 'subheading', 'text': extract_italic_text(raw)})
			continue
		if is_meta_date(raw):
			current['blocks'].append({'type': 'meta', 'text': raw})
			continue
		if is_bullet(raw):
			item_text = re.sub(r'^[-•]\s+', '', raw)
			if current['blocks'] and current['blocks'][-1]['type'] == 'list':
				current['blocks'][-1]['items'].append(item_text)  # type: ignore
			else:
				current['blocks'].append({'type': 'list', 'items': [item_text]})
			continue
		current['blocks'].append({'type': 'paragraph', 'text': raw})

	push_section_if_not_empty()
	return sections if sections else [{'blocks': [{'type': 'paragraph', 'text': text}]}] 