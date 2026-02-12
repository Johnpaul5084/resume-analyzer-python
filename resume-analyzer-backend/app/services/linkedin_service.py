"""
LinkedIn Integration Service
Handles LinkedIn OAuth, job scraping, and auto-apply functionality
"""

import os
import time
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import google.generativeai as genai
from app.core.config import settings

class LinkedInService:
    """Service for LinkedIn integration and automation"""
    
    def __init__(self):
        self.driver = None
        self.wait_time = 10
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.ai_model = genai.GenerativeModel('gemini-1.5-flash')
        
    def _init_driver(self, headless: bool = False):
        """Initialize Selenium WebDriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login_to_linkedin(self, email: str, password: str) -> Dict:
        """
        Login to LinkedIn using credentials
        
        Args:
            email: LinkedIn email
            password: LinkedIn password
            
        Returns:
            Dict with success status and message
        """
        try:
            self._init_driver(headless=False)
            self.driver.get('https://www.linkedin.com/login')
            
            # Wait for login form
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # Enter credentials
            email_field = wait.until(EC.presence_of_element_located((By.ID, 'username')))
            password_field = self.driver.find_element(By.ID, 'password')
            
            email_field.send_keys(email)
            password_field.send_keys(password)
            
            # Click login
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()
            
            # Wait for redirect to feed
            time.sleep(5)
            
            # Check if login successful
            if 'feed' in self.driver.current_url or 'mynetwork' in self.driver.current_url:
                # Save cookies for future sessions
                cookies = self.driver.get_cookies()
                return {
                    'success': True,
                    'message': 'Successfully logged into LinkedIn',
                    'cookies': cookies
                }
            else:
                return {
                    'success': False,
                    'message': 'Login failed. Please check credentials or handle 2FA manually.'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error during login: {str(e)}'
            }
    
    def search_jobs(self, 
                   keywords: str, 
                   location: str = '', 
                   experience_level: str = '',
                   job_type: str = '',
                   max_results: int = 25) -> List[Dict]:
        """
        Search for jobs on LinkedIn
        
        Args:
            keywords: Job search keywords (e.g., "Python Developer")
            location: Location filter (e.g., "Bangalore, India")
            experience_level: Entry level, Mid-Senior level, etc.
            job_type: Full-time, Part-time, Contract, etc.
            max_results: Maximum number of jobs to return
            
        Returns:
            List of job dictionaries with details
        """
        try:
            if not self.driver:
                self._init_driver()
            
            # Build search URL
            base_url = 'https://www.linkedin.com/jobs/search/?'
            params = {
                'keywords': keywords,
                'location': location,
                'f_E': self._get_experience_code(experience_level),
                'f_JT': self._get_job_type_code(job_type)
            }
            
            # Remove empty params
            params = {k: v for k, v in params.items() if v}
            search_url = base_url + '&'.join([f'{k}={v}' for k, v in params.items()])
            
            self.driver.get(search_url)
            time.sleep(3)
            
            jobs = []
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # Scroll to load more jobs
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Extract job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div.job-search-card')
            
            for card in job_cards[:max_results]:
                try:
                    job_data = self._extract_job_data(card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    print(f"Error extracting job: {e}")
                    continue
            
            return jobs
            
        except Exception as e:
            print(f"Error searching jobs: {e}")
            return []
    
    def _extract_job_data(self, card) -> Optional[Dict]:
        """Extract job information from a job card"""
        try:
            title = card.find_element(By.CSS_SELECTOR, 'h3.base-search-card__title').text
            company = card.find_element(By.CSS_SELECTOR, 'h4.base-search-card__subtitle').text
            location = card.find_element(By.CSS_SELECTOR, 'span.job-search-card__location').text
            link = card.find_element(By.CSS_SELECTOR, 'a.base-card__full-link').get_attribute('href')
            
            # Try to get posted date
            try:
                posted_date = card.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime')
            except:
                posted_date = None
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'link': link,
                'posted_date': posted_date,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            return None
    
    def apply_to_job(self, job_url: str, resume_data: Dict, cover_letter: str = None) -> Dict:
        """
        Apply to a job on LinkedIn
        
        Args:
            job_url: URL of the job posting
            resume_data: User's resume data
            cover_letter: Optional custom cover letter
            
        Returns:
            Dict with application status
        """
        try:
            self.driver.get(job_url)
            time.sleep(3)
            
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # Click "Easy Apply" button
            try:
                easy_apply_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.jobs-apply-button'))
                )
                easy_apply_button.click()
                time.sleep(2)
            except:
                return {
                    'success': False,
                    'message': 'Easy Apply not available for this job'
                }
            
            # Fill application form
            application_result = self._fill_application_form(resume_data, cover_letter)
            
            return application_result
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error applying to job: {str(e)}'
            }
    
    def _fill_application_form(self, resume_data: Dict, cover_letter: str = None) -> Dict:
        """Fill out the LinkedIn Easy Apply form"""
        try:
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # Handle multi-step form
            max_steps = 5
            current_step = 0
            
            while current_step < max_steps:
                try:
                    # Check for text inputs
                    text_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
                    for input_field in text_inputs:
                        label = self._get_field_label(input_field)
                        value = self._get_field_value(label, resume_data)
                        if value:
                            input_field.clear()
                            input_field.send_keys(value)
                    
                    # Check for textareas (cover letter, additional info)
                    textareas = self.driver.find_elements(By.TAG_NAME, 'textarea')
                    for textarea in textareas:
                        if cover_letter:
                            textarea.clear()
                            textarea.send_keys(cover_letter)
                    
                    # Check for radio buttons and checkboxes
                    self._handle_radio_checkboxes()
                    
                    # Click Next or Submit
                    next_button = self._find_next_button()
                    if next_button:
                        next_button.click()
                        time.sleep(2)
                        current_step += 1
                    else:
                        # No more steps, application submitted
                        break
                        
                except Exception as e:
                    print(f"Error in form step {current_step}: {e}")
                    break
            
            # Check if application was successful
            time.sleep(3)
            if self._check_application_success():
                return {
                    'success': True,
                    'message': 'Application submitted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Application may not have been submitted'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error filling form: {str(e)}'
            }
    
    def generate_cover_letter(self, job_title: str, company: str, resume_text: str) -> str:
        """
        Generate a personalized cover letter using AI
        
        Args:
            job_title: Title of the job
            company: Company name
            resume_text: User's resume content
            
        Returns:
            Generated cover letter
        """
        try:
            prompt = f"""
            Generate a professional cover letter for the following job application:
            
            Job Title: {job_title}
            Company: {company}
            
            Candidate's Resume:
            {resume_text[:2000]}  # Limit resume text
            
            Requirements:
            - Professional and concise (200-250 words)
            - Highlight relevant skills and experience
            - Show enthusiasm for the role
            - Mention specific achievements from resume
            - End with a call to action
            
            Generate the cover letter:
            """
            
            response = self.ai_model.generate_content(prompt)
            cover_letter = response.text.strip()
            
            return cover_letter
            
        except Exception as e:
            print(f"Error generating cover letter: {e}")
            return ""
    
    def auto_apply_batch(self, 
                        jobs: List[Dict], 
                        resume_data: Dict,
                        max_applications: int = 20,
                        generate_cover_letters: bool = True) -> Dict:
        """
        Apply to multiple jobs automatically
        
        Args:
            jobs: List of job dictionaries
            resume_data: User's resume data
            max_applications: Maximum applications per session
            generate_cover_letters: Whether to generate custom cover letters
            
        Returns:
            Summary of applications
        """
        results = {
            'total_jobs': len(jobs),
            'applied': 0,
            'failed': 0,
            'skipped': 0,
            'applications': []
        }
        
        for i, job in enumerate(jobs[:max_applications]):
            try:
                # Generate cover letter if enabled
                cover_letter = None
                if generate_cover_letters:
                    cover_letter = self.generate_cover_letter(
                        job['title'],
                        job['company'],
                        resume_data.get('text', '')
                    )
                
                # Apply to job
                application_result = self.apply_to_job(
                    job['link'],
                    resume_data,
                    cover_letter
                )
                
                if application_result['success']:
                    results['applied'] += 1
                else:
                    results['failed'] += 1
                
                results['applications'].append({
                    'job': job,
                    'result': application_result,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Rate limiting: wait between applications
                time.sleep(30)  # 30 seconds between applications
                
            except Exception as e:
                print(f"Error applying to {job['title']}: {e}")
                results['failed'] += 1
                continue
        
        return results
    
    def _get_experience_code(self, level: str) -> str:
        """Convert experience level to LinkedIn code"""
        codes = {
            'entry': '1',
            'associate': '2',
            'mid-senior': '3',
            'director': '4',
            'executive': '5'
        }
        return codes.get(level.lower(), '')
    
    def _get_job_type_code(self, job_type: str) -> str:
        """Convert job type to LinkedIn code"""
        codes = {
            'full-time': 'F',
            'part-time': 'P',
            'contract': 'C',
            'temporary': 'T',
            'internship': 'I'
        }
        return codes.get(job_type.lower(), '')
    
    def _get_field_label(self, input_field) -> str:
        """Get the label for an input field"""
        try:
            # Try to find associated label
            field_id = input_field.get_attribute('id')
            if field_id:
                label = self.driver.find_element(By.CSS_SELECTOR, f'label[for="{field_id}"]')
                return label.text.lower()
        except:
            pass
        
        # Try to get placeholder
        placeholder = input_field.get_attribute('placeholder')
        if placeholder:
            return placeholder.lower()
        
        return ''
    
    def _get_field_value(self, label: str, resume_data: Dict) -> str:
        """Get the appropriate value for a form field based on its label"""
        label = label.lower()
        
        if 'phone' in label or 'mobile' in label:
            return resume_data.get('phone', '')
        elif 'email' in label:
            return resume_data.get('email', '')
        elif 'first name' in label:
            return resume_data.get('first_name', '')
        elif 'last name' in label:
            return resume_data.get('last_name', '')
        elif 'city' in label or 'location' in label:
            return resume_data.get('location', '')
        elif 'linkedin' in label:
            return resume_data.get('linkedin_url', '')
        elif 'website' in label or 'portfolio' in label:
            return resume_data.get('website', '')
        
        return ''
    
    def _handle_radio_checkboxes(self):
        """Handle radio buttons and checkboxes intelligently"""
        try:
            # For yes/no questions, default to 'yes' for eligibility
            radio_groups = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
            for radio in radio_groups:
                label = self._get_field_label(radio)
                if 'authorized to work' in label or 'require sponsorship' in label:
                    # Click appropriate option
                    radio.click()
        except:
            pass
    
    def _find_next_button(self):
        """Find the Next or Submit button"""
        try:
            # Try to find "Next" button
            next_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Continue"]')
            return next_button
        except:
            pass
        
        try:
            # Try to find "Submit" button
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Submit"]')
            return submit_button
        except:
            pass
        
        return None
    
    def _check_application_success(self) -> bool:
        """Check if application was submitted successfully"""
        try:
            # Look for success message
            success_indicators = [
                'application sent',
                'application submitted',
                'successfully applied'
            ]
            
            page_text = self.driver.page_source.lower()
            return any(indicator in page_text for indicator in success_indicators)
        except:
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
