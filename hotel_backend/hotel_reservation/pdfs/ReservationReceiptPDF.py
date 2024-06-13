from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import mm, cm
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.paragraph import Paragraph, ParagraphStyle
from reportlab.platypus.flowables import Spacer
from reportlab.platypus.tables import Table, TableStyle
from reportlab import fonts
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader

import os
obj_of_symbol = {
    'eur': '€',
    'usd': '$',
    'lek': 'Lek',
}

class ReservationReceiptPDF:
    def __init__(self, data):
        self.data = data
        self.styles = getSampleStyleSheet()
        self.title_paragraph_center = ParagraphStyle(name='title_Paragraph_center', fontName='Times-Roman', fontSize=28,
                                              alignment=TA_CENTER, style=self.styles['Normal'], leading=40,
                                            )
        self.normal_paragraph_center = ParagraphStyle(name='normal_Paragraph_center', fontName='Times-Roman', fontSize=20,
                                              alignment=TA_CENTER, style=self.styles['Normal'], leading=25,)
        self.small_paragraph_center = ParagraphStyle(name='small_Paragraph_center', fontName='Times-Roman', fontSize=15,
                                              alignment=TA_CENTER, style=self.styles['Normal'], leading=20,)
        self.small_footer_paragraph_left = ParagraphStyle(name="small_footer_paragraph_left", fontName='Times-Roman', fontSize=12,
                                              alignment=TA_LEFT, style=self.styles['Normal'], leading=20,)

        self.margin = {
            'leftMargin': 2 * mm,
            'rightMargin': 2 * mm,
            'topMargin': 30 * mm,
            'bottomMargin': 20 * mm
        }
        self.small_spacer = Spacer(0.5 * cm, 0.5 * cm)
        self.mid_spacer = Spacer(0.75 * cm, 0.75 * cm)
        self.big_spacer = Spacer(1 * cm, 1 * cm)
        self.icon_path = os.path.dirname(__file__) + '\\images\\moto_icon.jpg'
        self.check_for_null_value = lambda x: x if x else '-'


    def _first_page(self):
        title_paragraph = Paragraph("Hotel Moto Moto", style=self.title_paragraph_center)
        normal_paragraph = Paragraph("We thank you for choosing us! The information below shows the information for this receipt", style=self.normal_paragraph_center)
        below_normal_paragraph = Paragraph("This Receipt is different for different customers.", style=self.normal_paragraph_center)
        print(self.icon_path)
        return [
            title_paragraph,
            self.small_spacer,
            normal_paragraph,
            below_normal_paragraph,
            self.mid_spacer
        ]


    @property
    def the_table_style(self):
        return TableStyle(
            [
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, -2), (0, -1), 'CENTER')
            ]
        )

    def table_page(self):
        data = self.data.get('guest_information', self.data.get('guest_user'))
        data_of_table = [
            [
                Paragraph("First Name", style=self.normal_paragraph_center),
                Paragraph(f'{self.check_for_null_value(data.get("first_name"))}', style=self.normal_paragraph_center),
            ],
            [
                Paragraph("Fathers_name", style=self.normal_paragraph_center),
                Paragraph(f'{self.check_for_null_value(data.get("fathers_name", "-"))}', style=self.normal_paragraph_center),
            ],
            [
                Paragraph('Last Name', style=self.normal_paragraph_center),
                Paragraph(f'{self.check_for_null_value(data.get("last_name"))}', style=self.normal_paragraph_center)
            ],
            [
                Paragraph('Email', style=self.normal_paragraph_center),
                Paragraph(f'{self.check_for_null_value(data.get("email"))}', style=self.normal_paragraph_center)
            ],
            [
                Paragraph('Phone_number', style=self.normal_paragraph_center),
                Paragraph(f'{self.check_for_null_value(data.get("phone_number"))}', style=self.normal_paragraph_center)
            ],
            [
                Paragraph('Number of Reservation', style=self.normal_paragraph_center),
                Paragraph(f'{self.check_for_null_value(self.data.get("id"))}', style=self.normal_paragraph_center),
            ],
            [
                Paragraph('Start Date', style=self.normal_paragraph_center),
                Paragraph(f'{self.check_for_null_value(self.data.get("start_date"))}', style=self.normal_paragraph_center),
            ],
            [
                Paragraph('End Date', style=self.normal_paragraph_center),
                Paragraph(f'{self.check_for_null_value(self.data.get("end_date"))}', style=self.normal_paragraph_center),
            ],
            [
                Paragraph('Total Payment', style=self.normal_paragraph_center),
                Paragraph(f'{self.check_for_null_value(self.data.get("total_payment"))} €',
                          style=self.normal_paragraph_center),
            ],
            [
                Paragraph('Room number/s', style=self.normal_paragraph_center),
                Paragraph(f'{self.check_for_null_value(self.data.get("room_numbers"))}', style=self.normal_paragraph_center)
            ],
            # [
            #     Paragraph('Room Type/s', style=self.normal_paragraph_center),
            #     Paragraph(f'{self.data.get("room_types")}', style=self.normal_paragraph_center)
            # ]


        ]
        return [Table(data_of_table, style=self.the_table_style, colWidths=[80 * mm, 100 * mm])]

    def get_flowables(self):
        flowables = []
        flowables.extend(self._first_page())
        flowables.extend(self.table_page())
        return flowables

    def header_and_footer(self, canvas: Canvas, _):
        canvas.saveState()
        logo = ImageReader(self.icon_path)
        canvas.drawImage(logo, 50, A4[1] - 100, 100, 100)
        # p = Paragraph('CONTACT US', style=self.small_paragraph_center)
        # p.wrap(100, 50)
        # p.drawOn(canvas, 10, 70)
        # p1 = Paragraph("email", style=self.small_footer_paragraph_left)
        # p1.wrap(75, 50)
        # p1.drawOn(canvas, x=10, y=50)
        canvas.restoreState()

    def main(self, request):
        flowables = self.get_flowables()
        simple_doc_template = SimpleDocTemplate(request, pagesize=A4, left_margin=self.margin.get('leftMargin'), right_margin=self.margin.get('rightMargin'),
                                                topMargin=self.margin.get('topMargin'), bottomMargin=self.margin.get('bottomMargin'))
        simple_doc_template.build(flowables, onFirstPage=self.header_and_footer, canvasmaker=Canvas)