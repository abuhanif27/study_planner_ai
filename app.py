

from flask import Flask, render_template, request, jsonify, send_file
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import numpy as np
import random
import json
from datetime import datetime, timedelta, timezone
import threading

app = Flask(__name__)

@app.after_request
def add_cache_headers(response):
    """Add cache control headers to prevent caching of HTML"""
    if 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response


import sys
sys.path.insert(0, '.')

from fuzzy_ga_study_planner_gui import FuzzyStressCalculator, StudyScheduleGA

results_cache = {}
generation_updates = {}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/courses', methods=['POST'])
def add_course():
    data = request.json
    
    errors = []
    
    name = data.get('name', '').strip()
    if not name:
        errors.append("Course name is required")
    elif len(name) > 50:
        errors.append("Course name must be less than 50 characters")
    elif any(char in name for char in ['@', '#', '$', '%']):
        errors.append("Course name contains invalid characters")
    
    try:
        difficulty = int(data.get('difficulty', 3))
        if difficulty < 1 or difficulty > 5:
            errors.append("Difficulty must be between 1-5")
    except:
        errors.append("Difficulty must be a number")
    
    try:
        exam_days = int(data.get('exam_days', 7))
        if exam_days < 1 or exam_days > 365:
            errors.append("Exam days must be between 1-365")
    except:
        errors.append("Exam days must be a number")
    
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400
    
    return jsonify({
        'success': True,
        'course': {
            'name': name,
            'difficulty': difficulty,
            'exam_days': exam_days
        }
    })

@app.route('/api/generate', methods=['POST'])
def generate_schedule():
    """Generate schedule"""
    data = request.json
    courses = data.get('courses', [])
    params = data.get('parameters', {})
    
    if not courses:
        return jsonify({'success': False, 'error': 'No courses added'}), 400
    
    # Convert to course format
    course_list = [
        {
            'id': i + 1,
            'name': c['name'],
            'difficulty': c['difficulty'],
            'exam_days_away': c['exam_days']
        }
        for i, c in enumerate(courses)
    ]
    
    # Create GA instance
    ga = StudyScheduleGA(
        course_list,
        days=params.get('days', 7),
        slots_per_day=params.get('slots', 3),
        max_hours_per_day=params.get('max_hours', 4)
    )
    
    # Run evolution
    best_schedule, fitness_history = ga.evolve(
        pop_size=params.get('population', 50),
        generations=params.get('generations', 100)
    )
    
    readable_schedule = ga.schedule_to_readable(best_schedule)
    
    result = {
        'success': True,
        'schedule': readable_schedule,
        'statistics': {
            'initial_fitness': float(fitness_history[0]),
            'final_fitness': float(fitness_history[-1]),
            'improvement': float(fitness_history[-1] - fitness_history[0]),
            'improvement_percent': float((fitness_history[-1] - fitness_history[0]) / fitness_history[0] * 100) if fitness_history[0] > 0 else 0,
            'generations': len(fitness_history),
            'total_courses': len(courses),
            'coverage': 100.0,
            'avg_stress': 0.5,
            'avg_overload': 0.3
        },
        'fitness_history': [float(x) if isinstance(x, np.ndarray) else float(x) for x in fitness_history]
    }
    
    return jsonify(result)

@app.route('/api/export-pdf', methods=['POST'])
def export_pdf():
    """Generate and return a beautiful PDF of the study schedule"""
    try:
        data = request.json
        
        # Create PDF in memory
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                               rightMargin=0.5*inch, leftMargin=0.5*inch,
                               topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#3b82f6'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#1e293b'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        # Title
        story.append(Paragraph('📚 Personalized Study Schedule', title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Timestamp in Bangladesh local time (UTC+6)
        timestamp = data.get('timestamp', 'N/A')
        if timestamp != 'N/A':
            dt = datetime.fromisoformat(timestamp)
            # Convert to Bangladesh time (UTC+6)
            bd_tz = timezone(timedelta(hours=6))
            bd_time = dt.astimezone(bd_tz)
            timestamp_text = bd_time.strftime('%B %d, %Y at %I:%M %p') + ' (BDT)'
        else:
            timestamp_text = 'N/A'
        story.append(Paragraph(f'Generated: {timestamp_text}', styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Statistics Section
        stats = data.get('statistics', {})
        story.append(Paragraph('📊 Schedule Statistics', heading_style))
        
        stats_data = [
            ['Metric', 'Value'],
            ['Initial Fitness', f"{stats.get('initial_fitness', 0):.2f}"],
            ['Final Fitness', f"{stats.get('final_fitness', 0):.2f}"],
            ['Improvement', f"{stats.get('improvement_percent', 0):.1f}%"],
            ['Generations', f"{stats.get('generations', 0)}"],
            ['Avg Stress', f"{stats.get('avg_stress', 0):.2f}"],
            ['Avg Overload', f"{stats.get('avg_overload', 0):.2f}"],
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8fafc')]),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Courses Section
        story.append(Paragraph('📖 Courses Added', heading_style))
        courses = data.get('courses', [])
        if courses:
            course_data = [['Course', 'Difficulty', 'Exam Days']]
            for course in courses:
                course_data.append([
                    course.get('name', 'N/A'),
                    f"{course.get('difficulty', 0)}/5",
                    f"{course.get('exam_days', 0)}d"
                ])
            
            courses_table = Table(course_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            courses_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#10b981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f0fdf4')]),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            story.append(courses_table)
        else:
            story.append(Paragraph('No courses added', styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        story.append(PageBreak())
        
        # Weekly Schedule
        story.append(Paragraph('📅 Weekly Study Schedule', heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        schedule = data.get('schedule', {})
        stress_colors = {
            'Low': HexColor('#dcfce7'),
            'Medium': HexColor('#fef3c7'),
            'High': HexColor('#fee2e2')
        }
        
        for day, slots in schedule.items():
            day_title = Paragraph(f'<b>{day}</b>', styles['Normal'])
            story.append(day_title)
            
            # Extract schedule data
            schedule_items = []
            for slot_name, activity in slots.items():
                if not slot_name.startswith('Total') and not slot_name.startswith('Stress') and not slot_name.startswith('Avg') and not slot_name.startswith('Difficulty'):
                    if activity != 'Rest':
                        schedule_items.append(f"• {activity}")
                    else:
                        schedule_items.append(f"• Rest")
            
            if schedule_items:
                for item in schedule_items:
                    story.append(Paragraph(item, styles['Normal']))
            
            # Stats for day
            total_hours = slots.get('Total Hours', '0')
            difficulty = slots.get('Avg Difficulty', '0')
            stress = slots.get('Stress Level', 'Low')
            
            day_stats = f"⏱️ {total_hours}h | 📊 Difficulty: {difficulty} | Stress: {stress}"
            story.append(Paragraph(day_stats, styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=False,
            download_name='study_schedule.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
