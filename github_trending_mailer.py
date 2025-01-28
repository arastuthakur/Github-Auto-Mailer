import requests
from bs4 import BeautifulSoup
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
import logging
import ssl
import win32com.client
import pythoncom

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_trending.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

def get_groq_summary(repositories):
    """Get a concise summary of the repositories using Groq"""
    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        
        # Prepare the repository information for summarization
        repo_info = "\n".join([
            f"• {repo['name']} ({repo['language']}): {repo['description']} [Stars: {repo['stars']}]"
            for repo in repositories
        ])
        
        prompt = f"""Analyze these trending GitHub repositories and provide a very concise summary (max 3-4 sentences):

{repo_info}

Focus on:
1. Most notable project(s)
2. Common technologies/themes
3. Any significant trends"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            stream=False,
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error getting Groq summary: {e}")
        return "AI summary unavailable at the moment."

def get_repo_summary(repo):
    """Get a detailed summary for a specific repository using Groq"""
    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        
        prompt = f"""Analyze this GitHub repository and provide a comprehensive yet concise summary (2-3 sentences):
        Name: {repo['name']}
        Description: {repo['description']}
        Language: {repo['language']}
        Stars: {repo['stars']}
        
        Focus on:
        1. Main purpose and unique features
        2. Technical significance
        3. Potential impact or use cases"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150,
            top_p=1,
            stream=False,
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error getting repo summary for {repo['name']}: {e}")
        return None

def scrape_trending_repos():
    """Scrape the top 10 trending repositories from GitHub"""
    url = "https://github.com/trending"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        repositories = []
        repo_articles = soup.select('article.Box-row', limit=10)
        
        for article in repo_articles:
            try:
                repo_link = article.select_one('h2 a')
                full_repo_name = repo_link['href'].strip('/')
                repo_url = f"https://github.com/{full_repo_name}"
                
                description = article.select_one('p')
                description_text = description.text.strip() if description else "No description available"
                
                language = article.select_one('[itemprop="programmingLanguage"]')
                language_text = language.text.strip() if language else "Not specified"
                
                stars = article.select_one('a[href*="stargazers"]')
                stars_text = stars.text.strip() if stars else "0"
                
                repo_data = {
                    'name': full_repo_name,
                    'url': repo_url,
                    'description': description_text,
                    'language': language_text,
                    'stars': stars_text
                }
                
                # Get repository summary
                repo_data['summary'] = get_repo_summary(repo_data)
                
                repositories.append(repo_data)
                
                # Add a small delay to avoid rate limiting
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error processing repository: {e}")
                continue
        
        return repositories
    except Exception as e:
        logging.error(f"Error scraping GitHub: {e}")
        raise

def create_summary(repositories, ai_summary=None):
    """Create a formatted HTML summary of repositories"""
    css_style = """
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f6f8fa;
            color: #24292e;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            padding: 25px;
            margin: 20px 0;
        }
        .header {
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 2px solid #e1e4e8;
            margin-bottom: 25px;
        }
        h1 {
            color: #24292e;
            font-size: 24px;
            margin: 0;
            padding: 0;
        }
        .date {
            color: #586069;
            font-size: 16px;
            margin-top: 8px;
        }
        .ai-summary {
            background-color: #f1f8ff;
            border: 1px solid #c8e1ff;
            border-radius: 6px;
            padding: 16px;
            margin: 20px 0;
        }
        .ai-summary h2 {
            color: #0366d6;
            font-size: 18px;
            margin-top: 0;
            margin-bottom: 12px;
        }
        .repo-card {
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            background-color: white;
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        .repo-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .repo-title {
            font-size: 20px;
            font-weight: 600;
            margin: 0 0 12px 0;
        }
        .repo-title a {
            color: #0366d6;
            text-decoration: none;
        }
        .repo-title a:hover {
            text-decoration: underline;
        }
        .repo-description {
            color: #586069;
            margin: 8px 0 16px 0;
            font-size: 14px;
            line-height: 1.5;
        }
        .repo-summary {
            background-color: #f6f8fa;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            padding: 16px;
            margin: 16px 0;
            font-size: 14px;
            line-height: 1.6;
            color: #24292e;
        }
        .stats {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-top: 16px;
            color: #586069;
            font-size: 14px;
        }
        .stat-item {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 30px;
            border-top: 1px solid #e1e4e8;
            color: #586069;
        }
        .app-signature {
            margin-bottom: 20px;
            color: #24292e;
            font-size: 15px;
        }
        .dev-signature {
            margin-top: 25px;
            padding: 15px;
            background: linear-gradient(135deg, #f6f8fa 0%, #ffffff 100%);
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            display: inline-block;
        }
        .dev-signature-content {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            font-size: 14px;
            color: #24292e;
            text-align: center;
        }
        .dev-name {
            font-weight: 600;
            font-size: 16px;
            color: #0366d6;
            margin-bottom: 4px;
        }
        .dev-title {
            font-size: 13px;
            color: #586069;
            margin-bottom: 8px;
        }
        .dev-links {
            margin-top: 10px;
            font-size: 13px;
        }
        .dev-links a {
            color: #0366d6;
            text-decoration: none;
            margin: 0 8px;
        }
        .dev-links a:hover {
            text-decoration: underline;
        }
        .emoji-separator {
            margin: 0 3px;
            opacity: 0.9;
        }
    </style>
    """
    
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {css_style}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📈 GitHub Trending Report</h1>
                <div class="date">{datetime.now().strftime('%B %d, %Y')}</div>
            </div>
    """
    
    if ai_summary:
        html_content += f"""
            <div class="ai-summary">
                <h2>🤖 AI Insights</h2>
                <p>{ai_summary.replace('\n', '<br>')}</p>
            </div>
        """
    
    for repo in repositories:
        summary_html = ""
        if repo.get('summary'):
            summary_html = f"""
                <div class="repo-summary">
                    {repo['summary']}
                </div>
            """
        
        html_content += f"""
            <div class="repo-card">
                <h3 class="repo-title"><a href="{repo['url']}">{repo['name']}</a></h3>
                <p class="repo-description">{repo['description']}</p>
                {summary_html}
                <div class="stats">
                    <div class="stat-item">
                        <span>🔤</span>
                        <span>{repo['language']}</span>
                    </div>
                    <div class="stat-item">
                        <span>⭐</span>
                        <span>{repo['stars']}</span>
                    </div>
                </div>
            </div>
        """
    
    html_content += """
            <div class="footer">
                <div class="app-signature">
                    Generated by GitHub Trending Mailer • Stay updated with the latest trends
                </div>
                <div class="dev-signature">
                    <div class="dev-signature-content">
                        <div class="dev-name">
                            <span>🚀</span> Developed by Arastu Thakur <span>💻</span>
                        </div>
                        <div class="dev-title">
                            AI Engineer & Open Source Enthusiast
                        </div>
                        <div class="dev-links">
                            <a href="https://github.com/arastuthakur" target="_blank">
                                <span>⭐</span> GitHub
                            </a>
                            <span class="emoji-separator">•</span>
                            <a href="https://linkedin.com/in/arastuthakur" target="_blank">
                                <span>🔗</span> LinkedIn
                            </a>
                            <span class="emoji-separator">•</span>
                            <a href="mailto:arustuthakur@gmail.com">
                                <span>📧</span> Email
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def save_summary(html_content):
    """Save the summary to a file"""
    summaries_dir = Path("summaries")
    summaries_dir.mkdir(exist_ok=True)
    
    filename = f"github_trending_{datetime.now().strftime('%Y%m%d')}.html"
    file_path = summaries_dir / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return file_path

def send_email_outlook(recipient_email, html_content, summary_path):
    """Send email using local Outlook client"""
    try:
        # Initialize Outlook
        pythoncom.CoInitialize()
        outlook = win32com.client.Dispatch('Outlook.Application')
        
        # Create a new mail item
        mail = outlook.CreateItem(0)  # 0 represents olMailItem
        
        # Set email properties
        mail.To = recipient_email
        mail.Subject = f"📊 GitHub Trending Report - {datetime.now().strftime('%B %d, %Y')}"
        mail.HTMLBody = html_content
        
        # Send the email
        mail.Send()
        
        logging.info(f"Email sent successfully via Outlook! Summary saved at: {summary_path}")
        return True
    except Exception as e:
        logging.error(f"Error sending email via Outlook: {e}")
        return False
    finally:
        pythoncom.CoUninitialize()

def send_email_smtp(recipient_email, html_content, summary_path):
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📊 GitHub Trending Report - {datetime.now().strftime('%B %d, %Y')}"
        sender_email = os.getenv('EMAIL_USER')
        msg['From'] = f"GitHub Trends <{sender_email}>"
        msg['To'] = recipient_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # List of SMTP configurations to try
        smtp_configs = [
            {
                'name': 'Gmail',
                'host': 'smtp.gmail.com',
                'port': 465,
                'use_ssl': True
            },
            {
                'name': 'Outlook',
                'host': 'smtp-mail.outlook.com',
                'port': 587,
                'use_ssl': False,
                'use_tls': True
            }
        ]
        
        for config in smtp_configs:
            try:
                logging.info(f"Attempting to send email using {config['name']}...")
                
                if config.get('use_ssl', False):
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL(config['host'], config['port'], context=context) as server:
                        server.login(sender_email, os.getenv('EMAIL_PASSWORD'))
                        server.send_message(msg)
                        logging.info(f"Email sent successfully via {config['name']} SSL!")
                        return True
                else:
                    with smtplib.SMTP(config['host'], config['port']) as server:
                        server.ehlo()
                        if config.get('use_tls', False):
                            server.starttls()
                            server.ehlo()
                        server.login(sender_email, os.getenv('EMAIL_PASSWORD'))
                        server.send_message(msg)
                        logging.info(f"Email sent successfully via {config['name']} TLS!")
                        return True
                        
            except Exception as e:
                logging.warning(f"Error with {config['name']}: {str(e)}")
                continue
        
        return False
    except Exception as e:
        logging.error(f"Error preparing email: {e}")
        return False

def send_email(recipient_email, html_content, summary_path):
    """Try multiple methods to send email"""
    # First try using local Outlook
    if send_email_outlook(recipient_email, html_content, summary_path):
        return True
        
    # If Outlook fails, try SMTP
    if send_email_smtp(recipient_email, html_content, summary_path):
        return True
        
    logging.warning("All email sending methods failed")
    logging.info("To fix email issues:")
    logging.info("1. Check if Outlook is properly configured")
    logging.info("2. Verify your email credentials in the .env file")
    logging.info("3. Check if your antivirus or firewall is blocking email")
    logging.info(f"Summary is still saved at: {summary_path}")
    return False

def daily_task(recipient_email):
    """Main task to run daily"""
    try:
        logging.info("Starting daily GitHub trending repositories task")
        repositories = scrape_trending_repos()
        ai_summary = get_groq_summary(repositories)
        html_content = create_summary(repositories, ai_summary)
        summary_path = save_summary(html_content)
        send_email(recipient_email, html_content, summary_path)
        logging.info("Daily task completed successfully")
    except Exception as e:
        logging.error(f"Error in daily task: {e}")

def main():
    recipient_email = "naughtyarastu@gmail.com"
    
    # Verify required environment variables
    required_vars = ['GROQ_API_KEY', 'EMAIL_USER', 'EMAIL_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return
    
    # Schedule the task to run daily at 9:00 AM
    schedule.every().day.at("09:00").do(daily_task, recipient_email)
    
    logging.info("GitHub Trending Mailer started. Press Ctrl+C to exit.")
    
    # Run the task once immediately
    daily_task(recipient_email)
    
    # Keep the script running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logging.info("Service stopped by user")

if __name__ == "__main__":
    main() 