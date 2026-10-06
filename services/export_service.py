import csv, io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def _text(v):
    if isinstance(v, list):
        return '\n'.join(f'• {x}' if not isinstance(x, dict) else f"• {x.get('task','')}" for x in v)
    if isinstance(v, dict):
        return ', '.join(f'{k}: {val}' for k,val in v.items())
    return str(v or '')


def meeting_csv(meeting):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(['Field','Value'])
    for key in ['id','title','created_at','language','summary','key_points','decisions','action_items','participants','deadlines','priorities']:
        w.writerow([key.replace('_',' ').title(), _text(meeting.get(key))])
    return out.getvalue().encode('utf-8')


def meeting_pdf(meeting):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36,leftMargin=36,topMargin=36,bottomMargin=36)
    styles = getSampleStyleSheet()
    story = [Paragraph('AI-Career Intelligence Platform', styles['Title']),
             Paragraph(meeting.get('title','Meeting Report'), styles['Heading2']),
             Spacer(1,10)]
    fields = [('Meeting ID',meeting.get('id')),('Date',meeting.get('created_at')),('Language',meeting.get('language')),
              ('Summary',meeting.get('summary')),('Key Points',meeting.get('key_points')),('Decisions',meeting.get('decisions')),
              ('Action Items',meeting.get('action_items')),('Participants',meeting.get('participants')),
              ('Deadlines',meeting.get('deadlines')),('Priorities',meeting.get('priorities'))]
    data = [['Section','Details']]
    for k,v in fields: data.append([k, _text(v)])
    table=Table(data,colWidths=[100,400])
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0f766e')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#d7dfdb')),('VALIGN',(0,0),(-1,-1),'TOP'),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6)]))
    story.append(table)
    doc.build(story)
    return buf.getvalue()
