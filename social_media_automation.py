import os
import json
import schedule
import time
import argparse
from datetime import datetime
import pandas as pd
from pathlib import Path

class SocialMediaManager:
    def __init__(self, calendar_file="detailed_social_media_schedule.md", preview_mode=False):
        self.content_calendar = {}
        self.assets_dir = Path("Social Media Assets")
        self.calendar_file = calendar_file
        self.preview_mode = preview_mode
        self.setup_directories()
        
    def setup_directories(self):
        """Create necessary directories for content management"""
        directories = [
            "Templates",
            "Images/Stock Photos",
            "Images/Custom Photos",
            "Images/Infographics",
            "Videos/Short Form",
            "Videos/Long Form",
            "Brand Assets/Logos",
            "Brand Assets/Icons",
            "Brand Assets/Fonts"
        ]
        
        print("Setting up directory structure...")
        for directory in directories:
            dir_path = Path(self.assets_dir / directory)
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {dir_path}")
            
    def load_content_calendar(self):
        """Load content calendar from markdown file"""
        try:
            with open(self.calendar_file, 'r') as f:
                content = f.read()
                
            print(f"\nLoading content calendar from {self.calendar_file}...")
            
            # Parse the markdown content into structured data
            sections = content.split('##')
            for section in sections:
                if 'Week' in section:
                    week_content = {}
                    posts = section.split('###')
                    for post in posts:
                        if post.strip():
                            platform_posts = post.split('**')
                            for platform_post in platform_posts:
                                if platform_post.strip():
                                    try:
                                        platform, content = platform_post.split(':', 1)
                                        week_content[platform.strip()] = content.strip()
                                    except ValueError:
                                        print(f"Warning: Could not parse platform post: {platform_post}")
                    self.content_calendar[section.split('\n')[0].strip()] = week_content
            
            print("✓ Content calendar loaded successfully")
            return True
            
        except FileNotFoundError:
            print(f"Error: Could not find calendar file: {self.calendar_file}")
            return False
        except Exception as e:
            print(f"Error loading content calendar: {str(e)}")
            return False
                
    def generate_post_content(self, platform, template_type, content_data):
        """Generate post content using templates"""
        templates = {
            'fact_check': {
                'instagram': """
┌────────────────────────┐
│     FACT CHECK         │
│  {background_image}    │
│                        │
│  MYTH:                 │
│  {myth}               │
│                        │
│  FACT:                 │
│  {fact}               │
│                        │
│  SOURCE: {source}     │
└────────────────────────┘
""",
                'linkedin': """
FACT CHECK: {title}

MYTH: {myth}

FACT: {fact}

SOURCE: {source}

#FactCheck #EnvironmentalConflict
"""
            },
            'success_story': {
                'instagram': """
┌────────────────────────┐
│     SUCCESS STORY      │
│  {background_image}    │
│                        │
│  CHALLENGE:            │
│  {challenge}          │
│                        │
│  SOLUTION:             │
│  {solution}           │
│                        │
│  IMPACT: {impact}     │
└────────────────────────┘
""",
                'linkedin': """
SUCCESS STORY: {title}

CHALLENGE: {challenge}

SOLUTION: {solution}

IMPACT: {impact}

#EnvironmentalSuccess #ConflictResolution
"""
            }
        }
        
        try:
            return templates[template_type][platform].format(**content_data)
        except KeyError:
            print(f"Warning: Template not found for {platform} - {template_type}")
            return content_data
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return content_data
        
    def schedule_posts(self):
        """Schedule posts based on content calendar"""
        print("\nScheduling posts...")
        scheduled_count = 0
        
        for week, posts in self.content_calendar.items():
            print(f"\nProcessing {week}:")
            for platform, content in posts.items():
                try:
                    # Extract time from content
                    time_str = content.split(' - ')[0] if ' - ' in content else '9:00 AM'
                    platform_name = platform.split(' ')[0].lower()
                    
                    # Schedule the post
                    schedule.every().day.at(time_str).do(
                        self.post_content,
                        platform=platform_name,
                        content=content
                    )
                    scheduled_count += 1
                    print(f"✓ Scheduled post for {platform_name} at {time_str}")
                except Exception as e:
                    print(f"Warning: Could not schedule post for {platform}: {str(e)}")
        
        print(f"\n✓ Successfully scheduled {scheduled_count} posts")
                
    def post_content(self, platform, content):
        """Post content to social media platform"""
        if self.preview_mode:
            print(f"\n[PREVIEW] Would post to {platform} at {datetime.now()}:")
            print("-" * 50)
            print(content)
            print("-" * 50)
        else:
            # This is where you would integrate with social media APIs
            print(f"\nPosting to {platform} at {datetime.now()}:")
            print("-" * 50)
            print(content)
            print("-" * 50)
        
    def preview_schedule(self):
        """Show all scheduled posts without actually posting"""
        print("\nPreview of scheduled posts:")
        print("=" * 50)
        for week, posts in self.content_calendar.items():
            print(f"\n{week}:")
            for platform, content in posts.items():
                time_str = content.split(' - ')[0] if ' - ' in content else '9:00 AM'
                platform_name = platform.split(' ')[0].lower()
                print(f"- {time_str} - {platform_name}")
        print("=" * 50)
        
    def run(self):
        """Run the social media manager"""
        if not self.load_content_calendar():
            return
            
        if self.preview_mode:
            self.preview_schedule()
            return
            
        self.schedule_posts()
        
        print("\nStarting social media manager...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\nStopping social media manager...")

def main():
    parser = argparse.ArgumentParser(description='Social Media Content Manager')
    parser.add_argument('--calendar', default='detailed_social_media_schedule.md',
                      help='Path to content calendar file')
    parser.add_argument('--preview', action='store_true',
                      help='Preview mode - show scheduled posts without posting')
    
    args = parser.parse_args()
    
    manager = SocialMediaManager(
        calendar_file=args.calendar,
        preview_mode=args.preview
    )
    manager.run()

if __name__ == "__main__":
    main() 