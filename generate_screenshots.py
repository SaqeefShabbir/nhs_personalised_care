"""
Generate Screenshots for NHS Personalised Care PWA
Run: python generate_screenshots.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_screenshot(title, description, features, filename, color="#005EB8"):
    """Create a screenshot image"""
    width, height = 1080, 1920
    
    img = Image.new('RGB', (width, height), '#F5F7FA')
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([0, 0, width, 80], fill=color)
    draw.text((30, 25), "NHS Personalised Care", fill='white', size=28)
    
    draw.rectangle([30, 100, width-30, 160], fill='white', outline='#E8ECF0')
    draw.text((50, 120), f"📊 {title}", fill='#212121', size=32)
    
    draw.text((50, 180), description, fill='#6B6B6B', size=24)
    
    y_pos = 240
    for i, feature in enumerate(features):
        if y_pos > height - 100:
            break
            
        draw.rounded_rectangle([50, y_pos, width-50, y_pos+120], radius=16, fill='white', outline='#E8ECF0', width=2)
        
        draw.text((80, y_pos+20), feature['title'], fill='#212121', size=26)
        draw.text((80, y_pos+60), feature['desc'], fill='#6B6B6B', size=20)
        
        badge_color = feature.get('color', '#E8F5E9')
        draw.rounded_rectangle([width-200, y_pos+20, width-80, y_pos+60], radius=12, fill=badge_color)
        draw.text((width-180, y_pos+30), feature.get('status', 'Active'), fill=feature.get('text_color', '#2E7D32'), size=18)
        
        y_pos += 140
    
    draw.rectangle([0, height-60, width, height], fill=color)
    draw.text((30, height-45), "NHS England - Personalised Care Model v2.0", fill='white', size=18)
    
    img.save(filename)
    print(f"✅ Generated {filename}")

def main():
    os.makedirs('static/screenshots', exist_ok=True)
    
    screenshots = [
        {
            'title': 'Dashboard',
            'desc': 'Overview of your personalised care',
            'filename': 'static/screenshots/dashboard.png',
            'features': [
                {'title': 'PAM Score: 68', 'desc': 'Level 3 - Taking Action', 'status': 'Improving', 'color': '#E3F2FD', 'text_color': '#005EB8'},
                {'title': 'Goals: 8', 'desc': '3 completed, 5 in progress', 'status': 'On Track', 'color': '#E8F5E9', 'text_color': '#2E7D32'},
                {'title': 'Risk Assessment', 'desc': 'Low Risk • Score: 0.25', 'status': 'Stable', 'color': '#E8F5E9', 'text_color': '#2E7D32'},
                {'title': 'Recent Activity', 'desc': 'Goal completed: Walk 30 minutes', 'status': 'New', 'color': '#FFF3E0', 'text_color': '#E65100'},
            ]
        },
        {
            'title': 'Patients',
            'desc': 'Manage your patient list',
            'filename': 'static/screenshots/patients.png',
            'features': [
                {'title': 'NHS123456', 'desc': 'Sarah Johnson • Age: 59', 'status': 'Active', 'color': '#E3F2FD', 'text_color': '#005EB8'},
                {'title': 'NHS789012', 'desc': 'James Smith • Age: 46', 'status': 'Active', 'color': '#E3F2FD', 'text_color': '#005EB8'},
                {'title': 'NHS345678', 'desc': 'Aisha Patel • Age: 34', 'status': 'Active', 'color': '#E3F2FD', 'text_color': '#005EB8'},
            ]
        },
        {
            'title': 'Goals',
            'desc': 'Track your health goals',
            'filename': 'static/screenshots/goals.png',
            'features': [
                {'title': 'Walk 30 minutes daily', 'desc': 'Physical Health • Target: Dec 2024', 'status': 'In Progress', 'color': '#E3F2FD', 'text_color': '#005EB8'},
                {'title': 'Join community walking group', 'desc': 'Social Wellbeing • No target', 'status': 'Achieved', 'color': '#E8F5E9', 'text_color': '#2E7D32'},
                {'title': 'Reduce blood pressure', 'desc': 'Physical Health • Target: 120/80', 'status': 'Planned', 'color': '#FFF3E0', 'text_color': '#E65100'},
            ]
        },
        {
            'title': 'Outcomes',
            'desc': 'Monitor health metrics',
            'filename': 'static/screenshots/outcomes.png',
            'features': [
                {'title': 'Blood Pressure', 'desc': 'Current: 135/85 • Target: 120/80', 'status': 'In Progress', 'color': '#E3F2FD', 'text_color': '#005EB8'},
                {'title': 'Heart Rate', 'desc': 'Current: 82 • Target: 70', 'status': 'In Progress', 'color': '#E3F2FD', 'text_color': '#005EB8'},
                {'title': 'Mood Score', 'desc': 'Current: 7 • Target: 8', 'status': 'Achieved', 'color': '#E8F5E9', 'text_color': '#2E7D32'},
            ]
        },
        {
            'title': 'AI Insights',
            'desc': 'Intelligent health predictions',
            'filename': 'static/screenshots/insights.png',
            'features': [
                {'title': 'Risk Assessment', 'desc': 'Low Risk • Score: 0.25', 'status': 'Stable', 'color': '#E8F5E9', 'text_color': '#2E7D32'},
                {'title': 'PAM Prediction', 'desc': 'Predicted Score: 72 • Improving', 'status': 'Trending Up', 'color': '#E8F5E9', 'text_color': '#2E7D32'},
                {'title': 'Recommendations', 'desc': '1. Review Goals (High Priority)', 'status': 'Action Needed', 'color': '#FFF3E0', 'text_color': '#E65100'},
            ]
        },
        {
            'title': 'Clinical Notes',
            'desc': 'Document your health journey',
            'filename': 'static/screenshots/notes.png',
            'features': [
                {'title': 'Feeling more energetic', 'desc': 'Walking 20 min daily • Knee pain improving', 'status': 'Positive', 'color': '#E8F5E9', 'text_color': '#2E7D32'},
                {'title': 'Blood pressure elevated', 'desc': 'Need to reduce salt intake', 'status': 'Neutral', 'color': '#FFF8E1', 'text_color': '#F57F17'},
            ]
        },
        {
            'title': 'Settings',
            'desc': 'Application configuration',
            'filename': 'static/screenshots/settings.png',
            'features': [
                {'title': 'Current Patient', 'desc': 'Sarah Johnson (NHS123456)', 'status': 'Active', 'color': '#E3F2FD', 'text_color': '#005EB8'},
                {'title': 'Notifications', 'desc': 'Push notifications enabled', 'status': 'On', 'color': '#E8F5E9', 'text_color': '#2E7D32'},
                {'title': 'Data Management', 'desc': 'Export or clear your data', 'status': 'Available', 'color': '#F3E5F5', 'text_color': '#7B1FA2'},
            ]
        }
    ]
    
    for screenshot in screenshots:
        create_screenshot(
            screenshot['title'],
            screenshot['desc'],
            screenshot['features'],
            screenshot['filename']
        )
    
    print("\n" + "="*50)
    print("✅ All screenshots generated successfully!")
    print("📁 Location: static/screenshots/")
    print("="*50)

if __name__ == '__main__':
    try:
        from PIL import Image, ImageDraw, ImageFont
        main()
    except ImportError:
        print("❌ Pillow not installed. Install with: pip install Pillow")
        print("\nCreating fallback screenshots...")
        create_fallback_screenshots()

def create_fallback_screenshots():
    """Create minimal screenshots using PIL if available"""
    try:
        from PIL import Image, ImageDraw
        
        os.makedirs('static/screenshots', exist_ok=True)
        
        colors = ['#005EB8', '#009639', '#FFB81C', '#DA291C', '#7B1FA2', '#E65100', '#2E7D32']
        titles = ['dashboard', 'patients', 'goals', 'outcomes', 'insights', 'notes', 'settings']
        
        for i, (color, title) in enumerate(zip(colors, titles)):
            img = Image.new('RGB', (1080, 1920), '#F5F7FA')
            draw = ImageDraw.Draw(img)
            
            draw.rectangle([0, 0, 1080, 200], fill=color)
            draw.text((50, 80), f'NHS Personalised Care - {title.capitalize()}', fill='white', size=40)
            
            for j in range(4):
                y = 250 + j * 380
                draw.rounded_rectangle([50, y, 1030, y+330], radius=20, fill='white', outline='#E8ECF0', width=3)
                draw.text((80, y+140), f'Screenshot: {title.capitalize()} - Panel {j+1}', fill='#6B6B6B', size=30)
            
            img.save(f'static/screenshots/{title}.png')
            print(f'✅ Generated screenshot: {title}.png')
        
        print("\n✅ Fallback screenshots created!")
    except:
        print("⚠️ Could not create screenshots. Please install Pillow:")
        print("   pip install Pillow")