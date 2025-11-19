"""
Enhanced email sender with professional HTML formatting.
Uses custom cover letter body provided by user.
- Bold text in body is BLACK
- Signature in BLUE
- Left-aligned format
- Professional email style
"""

import yagmail
import logging
from config import SENDER_EMAIL, SENDER_PASSWORD, RESUME_PATH, DRY_RUN

# Set up logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_html_email(job_title, company, recipient_email):
    """
    Create a professional HTML-formatted email with custom cover letter.
    - Bold text in body is BLACK
    - Signature is BLUE
    - Left-aligned
    """
    
    # Personalization - UPDATE THESE WITH YOUR INFO
    sender_name = "Surya Teja"
    sender_phone = "(518) 600-1847"
    sender_linkedin = "www.linkedin.com/in/suryaj14"
    
    # Custom email body with formatting - ALL ON ONE LINE
    html_body = f"<html><head><meta charset='UTF-8'><style>body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; text-align: left; }} .email-content {{ max-width: 100%; padding: 0; }} p {{ margin: 12px 0; font-size: 14px; line-height: 1.6; }} .highlight {{ color: #000; font-weight: bold; }} .bullet-point {{ margin-left: 20px; margin-top: 5px; font-size: 14px; line-height: 1.5; }} .section-title {{ color: #000; font-weight: bold; margin-top: 12px; margin-bottom: 8px; font-size: 14px; }} .signature {{ margin-top: 15px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 13px; }} .signature-name {{ font-weight: bold; color: #0077b5; font-size: 15px; margin-bottom: 3px; }} .signature-detail {{ margin: 2px 0; color: #0077b5; font-size: 13px; }} .signature-link {{ color: #0077b5; text-decoration: none; }} .signature-link:hover {{ text-decoration: underline; }}</style></head><body><div class='email-content'><p>Hi,</p><p>I hope this message finds you well.</p><p>My name is Surya Teja Jakka, and I am a <span class='highlight'>Senior Workday HCM Consultant with over 11 years of experience</span> delivering large-scale Workday implementations, advanced reporting, integrations, and production support for Fortune 500 clients.</p><p>Throughout my career, I have successfully:</p><div class='bullet-point'>&#8226; <span class='highlight'>Designed and implemented 200+ custom Workday reports</span> (Advanced, Matrix, Composite, Dashboards)</div><div class='bullet-point'>&#8226; <span class='highlight'>Led end-to-end implementations and ERP migrations</span>, including PeopleSoft-to-Workday transitions</div><div class='bullet-point'>&#8226; <span class='highlight'>Configured and optimized key Workday modules:</span> Core HCM, Compensation, Payroll, Benefits, Absence, Time Tracking, Recruiting, Security Administration</div><div class='bullet-point'>&#8226; <span class='highlight'>Developed integrations using EIB, Core Connectors, and Workday Studio</span> ensuring seamless data flow with third-party systems</div><div class='bullet-point'>&#8226; <span class='highlight'>Directed test strategy, UAT, and defect management</span>, achieving 99%+ resolution across multiple projects</div><p>I have had the privilege of working with leading clients including <span class='highlight'>Wells Fargo, Moody's, State of Wisconsin, and GEICO</span>, consistently delivering solutions that align technology with business goals.</p><p>I would greatly appreciate it if you could let me know about any opportunities that align with my profile. My updated resume is attached for your reference.</p><p>Thank you for your time and consideration. I look forward to hearing from you.</p><p>Best regards,</p><div class='signature'><div class='signature-name'>{sender_name}</div><div class='signature-detail'><span class='highlight'>Senior Workday HCM Consultant</span></div><div class='signature-detail'>Phone: {sender_phone}</div><div class='signature-detail'>Email: {SENDER_EMAIL}</div><div class='signature-detail'>LinkedIn: <a href='{sender_linkedin}' class='signature-link'>{sender_linkedin}</a></div><div class='signature-detail' style='margin-top: 8px; font-size: 12px; color: #888;'>Open to: Remote & Local Opportunities | Available for Immediate Engagement</div></div></div></body></html>"
    
    return html_body


def send_application(job_title, company, recipient_email):
    """
    Send a professional job application email with resume.
    
    Args:
        job_title (str): Job title
        company (str): Company name
        recipient_email (str): Recipient email address
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    
    try:
        # Email subject with job title and company
        subject = f"Experienced Senior Workday HCM Consultant | Open to New Opportunities"
        
        # Generate HTML email body
        html_body = create_html_email(job_title, company, recipient_email)
        
        # DRY RUN MODE: Show email preview instead of sending
        if DRY_RUN:
            print(f"\n{'='*70}")
            print(f"[DRY RUN MODE - Email NOT Actually Sent]")
            print(f"{'='*70}")
            print(f"To: {recipient_email}")
            print(f"Subject: {subject}")
            print(f"\nEmail Preview:")
            print(f"{'-'*70}")
            print(f"Hi,")
            print(f"\nI hope this message finds you well.")
            print(f"\nI'm reaching out to express my interest in current or upcoming")
            print(f"opportunities for a {job_title} role within your client network.")
            print(f"With over 12 years of experience in enterprise-scale application")
            print(f"development, cloud-native architecture, and full-stack engineering,")
            print(f"I've successfully delivered large-scale modernization programs for")
            print(f"top financial, regulatory, and public sector clients including")
            print(f"Wells Fargo, Moody's, and the State of Wisconsin.")
            print(f"\nIn my current role as a Principal Engineer at Wells Fargo...")
            print(f"\n[Professional cover letter with achievements, expertise, and outcomes]")
            print(f"\nBest regards,")
            print(f"\nSurya Teja")
            print(f"Principal Engineer | Full-Stack Java Developer")
            print(f"📱 Phone: (480) 580-4821")
            print(f"📧 Email: {SENDER_EMAIL}")
            print(f"💼 LinkedIn: www.linkedin.com/in/teja-j14")
            print(f"\nAttachment: resume.pdf")
            print(f"{'='*70}\n")
            
            logging.info(f"[DRY RUN] Email prepared to {recipient_email} for {job_title} at {company}")
            return True
        
        # LIVE MODE: Actually send the email
        print(f"\n   Sending email to {recipient_email}...")
        
        # Create SMTP connection using yagmail
        yag = yagmail.SMTP(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Send email with HTML body and attachment
        yag.send(
            to=recipient_email,
            subject=subject,
            contents=[html_body],  # HTML body
            attachments=RESUME_PATH  # Attach resume
        )
        
        yag.close()
        
        logging.info(f"✓ Email sent successfully to {recipient_email} for {job_title} at {company}")
        print(f"   ✓ Email sent successfully!")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"✗ Failed to send email to {recipient_email}: {error_msg}")
        print(f"   ✗ Failed to send email: {error_msg}")
        return False

def test_html_email():
    """Test HTML email formatting."""
    print("\n" + "="*70)
    print("HTML EMAIL TEST")
    print("="*70 + "\n")
    
    html = create_html_email("Principal Java Full-Stack Engineer", "Client Company", "test@example.com")
    
    # Save to file for preview
    with open('email_preview.html', 'w') as f:
        f.write(html)
    
    print("✓ HTML email template created!")
    print("✓ Saved to: email_preview.html")
    print("\nYou can open this file in your browser to see the formatted email.")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_html_email()
