"""
Implementación del generador de PDFs usando ReportLab.
Versión empresarial COMPACTA - Todo en 1 página.
"""

import os
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from django.conf import settings

from ...ports.services import PDFGeneratorService


class ReportLabPDFGenerator(PDFGeneratorService):
    """
    Generador de PDFs empresarial COMPACTO (1 página).
    Diseño tipo barbería premium con todo el contenido optimizado.
    """
    
    def __init__(self):
        self.output_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Paleta de colores PREMIUM
        self.gold = colors.HexColor('#D4AF37')
        self.dark_gold = colors.HexColor('#B8941E')
        self.black = colors.HexColor('#1a1a1a')
        self.dark_gray = colors.HexColor('#2d2d2d')
        self.light_gray = colors.HexColor('#f5f5f5')
        self.white = colors.white
        self.cream = colors.HexColor('#FAF7F0')
    
    def generate_report(self, analysis_data: Dict[str, Any], recommendations: Dict[str, Any]) -> str:
        """Genera el PDF compacto en 1 página."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analisis_facial_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Márgenes reducidos para aprovechar espacio
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=30,
            leftMargin=30,
            topMargin=25,
            bottomMargin=25
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # === HEADER COMPACTO ===
        story.extend(self._build_compact_header(analysis_data, styles))
        story.append(Spacer(1, 0.15*inch))
        
        # === ANÁLISIS EN 2 COLUMNAS ===
        story.extend(self._build_two_column_analysis(analysis_data, styles))
        story.append(Spacer(1, 0.15*inch))
        
        # === RECOMENDACIONES COMPACTAS ===
        story.extend(self._build_compact_recommendations(recommendations, styles))
        story.append(Spacer(1, 0.1*inch))
        
        # === FOOTER ===
        story.extend(self._build_compact_footer(styles))
        
        doc.build(story)
        return os.path.join('reports', filename)
    
    def _build_compact_header(self, analysis_data, styles):
        """Header compacto con logo y resultado principal"""
        elements = []
        
        # Barra dorada superior
        header_table = Table([['']],  colWidths=[7.5*inch], rowHeights=[0.08*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.gold),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Logo y resultado en una tabla compacta
        primary_shape = analysis_data.get('primary_shape', 'No detectado')
        confidence = analysis_data.get('primary_confidence', 0)
        
        header_data = [[
            Paragraph(
                "<b><font size='20'>✂️ BARBERIA</font></b><br/>"
                "<font size='7'>Estilo y Elegancia</font>",
                ParagraphStyle('Logo', alignment=TA_CENTER, textColor=self.black)
            ),
            Paragraph(
                "<b><font size='11'>ANÁLISIS FACIAL</font></b><br/>"
                f"<font size='8'>{datetime.now().strftime('%d/%m/%Y')}</font>",
                ParagraphStyle('Date', alignment=TA_CENTER, textColor=self.dark_gray)
            ),
            Paragraph(
                f"<b><font size='14' color='#D4AF37'>{primary_shape}</font></b><br/>"
                f"<font size='8'>Precisión: {confidence:.0f}%</font>",
                ParagraphStyle('Result', alignment=TA_CENTER)
            )
        ]]
        
        header_info = Table(header_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
        header_info.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (2, 0), (2, 0), self.cream),
            ('BOX', (2, 0), (2, 0), 1.5, self.gold),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(header_info)
        
        return elements
    
    def _build_two_column_analysis(self, analysis_data, styles):
        """Análisis en 2 columnas: gráfico + métricas"""
        elements = []
        
        # Título de sección
        title = ParagraphStyle(
            'SecTitle',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=self.black,
            fontName='Helvetica-Bold',
            spaceAfter=5
        )
        elements.append(Paragraph("📊 ANÁLISIS DETALLADO", title))
        
        line = Drawing(500, 3)
        line.add(Line(0, 1, 500, 1, strokeColor=self.gold, strokeWidth=2))
        elements.append(line)
        elements.append(Spacer(1, 0.1*inch))
        
        # Crear 2 columnas: gráfico a la izquierda, métricas a la derecha
        col1_content = []  # Gráfico
        col2_content = []  # Métricas
        
        # COLUMNA 1: Gráfico horizontal compacto
        if analysis_data.get('face_shape_results'):
            shapes = [str(item[0]) for item in analysis_data['face_shape_results']]
            percentages = [float(item[1]) for item in analysis_data['face_shape_results']]
            
            drawing = Drawing(220, 120)
            chart = HorizontalBarChart()
            chart.x = 10
            chart.y = 10
            chart.width = 150
            chart.height = 100
            chart.data = [percentages]
            chart.categoryAxis.categoryNames = shapes
            chart.categoryAxis.labels.fontSize = 7
            chart.categoryAxis.labels.fontName = 'Helvetica'
            chart.valueAxis.valueMin = 0
            chart.valueAxis.valueMax = 100
            chart.valueAxis.valueStep = 25
            chart.valueAxis.labels.fontSize = 6
            chart.bars[0].fillColor = self.gold
            chart.bars[0].strokeColor = self.dark_gold
            chart.bars[0].strokeWidth = 0.5
            
            drawing.add(chart)
            col1_content.append(drawing)
        
        # COLUMNA 2: Tabla de métricas compacta
        if analysis_data.get('measurements'):
            measurements = analysis_data['measurements']
            
            def sf(value, decimals=1):
                try:
                    return f"{float(value):.{decimals}f}"
                except:
                    return "—"
            
            metrics_data = [
                ['MÉTRICA', 'VALOR'],
                ['Largo Rostro', f"{sf(measurements.get('face_height', 0))} cm"],
                ['Ancho Facial', f"{sf(measurements.get('face_width', 0))} px"],
                ['Ratio A/A', sf(measurements.get('ratio', 0), 2)],
                ['Ancho Frente', f"{sf(measurements.get('forehead_width', 0))} cm"],
                ['Ancho Mandíbula', f"{sf(measurements.get('jaw_width', 0))} cm"],
                ['Simetría', f"{sf(measurements.get('symmetry', 0))}%"],
            ]
            
            metrics_table = Table(metrics_data, colWidths=[1.8*inch, 1*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.gold),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, self.dark_gray),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.cream])
            ]))
            col2_content.append(metrics_table)
        
        # Combinar columnas en una tabla
        two_columns = Table([[col1_content, col2_content]], colWidths=[3.5*inch, 3.5*inch])
        two_columns.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(two_columns)
        
        return elements
    
    def _build_compact_recommendations(self, recommendations, styles):
        """Recomendaciones en formato compacto"""
        elements = []
        
        title = ParagraphStyle(
            'RecTitle',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=self.black,
            fontName='Helvetica-Bold',
            spaceAfter=5
        )
        elements.append(Paragraph("✂️ RECOMENDACIONES PERSONALIZADAS", title))
        
        line = Drawing(500, 3)
        line.add(Line(0, 1, 500, 1, strokeColor=self.gold, strokeWidth=2))
        elements.append(line)
        elements.append(Spacer(1, 0.08*inch))
        
        # Top 3 cortes en formato ultra compacto
        if recommendations and recommendations.get('cortes'):
            cortes = recommendations.get('cortes', [])[:3]
            
            rec_data = [['#', 'CORTE', 'DESCRIPCIÓN']]
            
            for i, corte in enumerate(cortes, 1):
                rec_data.append([
                    f"{i}",
                    corte.get('nombre', 'N/A'),
                    corte.get('descripcion', 'Sin descripción')[:80] + '...' if len(corte.get('descripcion', '')) > 80 else corte.get('descripcion', 'N/A')
                ])
            
            rec_table = Table(rec_data, colWidths=[0.3*inch, 1.8*inch, 4.9*inch])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.gold),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, self.dark_gray),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.cream]),
                ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(rec_table)
        
        # Barba (si hay espacio)
        if recommendations and recommendations.get('barba'):
            elements.append(Spacer(1, 0.08*inch))
            beard_title = ParagraphStyle(
                'BeardT',
                parent=styles['Normal'],
                fontSize=9,
                textColor=self.dark_gray,
                fontName='Helvetica-Bold',
                spaceAfter=3
            )
            elements.append(Paragraph("🧔 ESTILOS DE BARBA:", beard_title))
            
            beard_styles = recommendations.get('barba', [])[:2]
            beard_text = " | ".join([
                f"<b>{b.get('nombre', 'N/A')}</b>" 
                for b in beard_styles if isinstance(b, dict)
            ])
            
            beard_para = Paragraph(
                f"<font size='7'>{beard_text}</font>",
                ParagraphStyle('BeardP', parent=styles['Normal'])
            )
            elements.append(beard_para)
        
        return elements
    
    def _build_compact_footer(self, styles):
        """Footer ultra compacto"""
        elements = []
        
        line = Drawing(500, 2)
        line.add(Line(0, 1, 500, 1, strokeColor=self.gold, strokeWidth=1))
        elements.append(line)
        elements.append(Spacer(1, 0.05*inch))
        
        footer = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=6,
            textColor=self.dark_gray,
            alignment=TA_CENTER,
        )
        
        elements.append(Paragraph(
            "<b>💈 BABERAI</b> | "
            "📍 Av. Principal 123 | 📞 +1 (555) 123-4567 | "
            "📧 contacto@baberai.com | 🌐 www.baberai.com | "
            f"© {datetime.now().year}",
            footer
        ))
        
        return elements