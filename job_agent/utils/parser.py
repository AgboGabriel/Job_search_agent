
import re
from datetime import datetime


class CV_Parser:
    """
    Parses CV documents to extract:
    - Skills
    - Experience
    - Education
    - Certifications
    """
    
    def __init__(self):
        self.skill_keywords = {
            "programming_languages": ["Python", "Java", "JavaScript", "C++", "C#", "Ruby", "Go", "Rust", "PHP", "Swift", "Kotlin", "TypeScript"],
            "frameworks": ["React", "Angular", "Vue", "Django", "Flask", "Spring", "Qt", ".NET", "Node.js", "Express", "TensorFlow", "PyTorch"],
            "databases": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQLite", "Redis", "Elasticsearch"],
            "tools": ["Git", "Docker", "Kubernetes", "Jenkins", "AWS", "Azure", "GCP", "Linux", "CMake", "Maven", "Gradle"],
            "data_science": ["Machine Learning", "Data Analysis", "Statistics", "Pandas", "NumPy", "Tableau", "Power BI", "Excel"],
            "soft_skills": ["Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management", "Project Management"]
        }
        
    def parse_cv(self, cv_content):
        """
        Parse CV content and return structured data
        For prototype, simulates parsing
        """
        # In a real implementation, this would use NLP or regex
        # For prototype, return simulated data based on content analysis
        
        result = {
            "name": self.extract_name(cv_content),
            "experience": self.extract_experience(cv_content),
            "current_role": self.extract_current_role(cv_content),
            "target_role": "",
            "skills": self.extract_skills(cv_content),
            "soft_skills": self.extract_soft_skills(cv_content),
            "education": self.extract_education(cv_content),
            "certifications": self.extract_certifications(cv_content)
        }
        
        return result
    
    def extract_name(self, content):
        """Extract name from CV"""
        # Simple simulation
        if isinstance(content, str):
            # Look for common patterns
            lines = content.split('\n')
            if lines and len(lines[0]) < 50:
                return lines[0].strip()
        return "User"
    
    def extract_experience(self, content):
        """Extract years of experience"""
        # Simulate - in real implementation would parse dates
        if isinstance(content, str):
            # Look for patterns like "5 years" or "5+ years"
            import re
            matches = re.findall(r'(\d+)[\+]?\s*years?', content.lower())
            if matches:
                return int(matches[0])
        return 2  # Default
    
    def extract_current_role(self, content):
        """Extract current job title"""
        if isinstance(content, str):
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "developer" in line.lower() or "engineer" in line.lower() or "analyst" in line.lower():
                    return line.strip()
        return "Software Developer"
    
    def extract_skills(self, content):
        """Extract technical skills"""
        found_skills = []
        
        if isinstance(content, str):
            content_lower = content.lower()
            
            for category, skills in self.skill_keywords.items():
                if category in ["programming_languages", "frameworks", "databases", "tools", "data_science"]:
                    for skill in skills:
                        if skill.lower() in content_lower:
                            found_skills.append({
                                "name": skill,
                                "level": "intermediate",  # Default
                                "years": 1  # Default
                            })
        
        # If no skills found, provide defaults for demo
        if not found_skills:
            found_skills = [
                {"name": "JavaScript", "level": "advanced", "years": 3},
                {"name": "Python", "level": "intermediate", "years": 1},
                {"name": "SQL", "level": "intermediate", "years": 1}
            ]
        
        return found_skills
    
    def extract_soft_skills(self, content):
        """Extract soft skills"""
        found_skills = []
        
        if isinstance(content, str):
            content_lower = content.lower()
            for skill in self.skill_keywords["soft_skills"]:
                if skill.lower() in content_lower:
                    found_skills.append(skill)
        
        # Default
        if not found_skills:
            found_skills = ["Communication", "Problem Solving", "Teamwork"]
        
        return found_skills
    
    def extract_education(self, content):
        """Extract education information"""
        if isinstance(content, str):
            if "bachelor" in content.lower() or "bsc" in content.lower():
                return "Bachelor's Degree"
            elif "master" in content.lower() or "msc" in content.lower():
                return "Master's Degree"
            elif "phd" in content.lower() or "doctorate" in content.lower():
                return "PhD"
        return "Bachelor's Degree"
    
    def extract_certifications(self, content):
        """Extract certifications"""
        found_certs = []
        
        if isinstance(content, str):
            cert_keywords = ["certified", "certification", "certificate", "professional", "aws", "azure", "google", "oracle", "cisco", "comptia"]
            
            lines = content.split('\n')
            for line in lines:
                line_lower = line.lower()
                for keyword in cert_keywords:
                    if keyword in line_lower and len(line) < 100:
                        found_certs.append(line.strip())
                        break
        
        return found_certs[:3]  # Limit to 3