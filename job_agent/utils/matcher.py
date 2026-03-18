
class JobMatcher:
    """
    Handles job matching logic:
    - Calculate match scores
    - Generate explanations
    - Identify skill gaps
    """
    
    def __init__(self):
        self.weights = {
            "required_skills": 0.5,
            "preferred_skills": 0.2,
            "experience": 0.15,
            "preferences": 0.15
        }
    
    def calculate_match_score(self, job, profile):
        """
        Calculate how well a job matches a user profile
        Returns score from 0-100
        """
        score = 0
        
        # Skill match (required skills)
        required_score = self.calculate_skill_match(
            job.get("skills_required", []),
            profile["skills"]["technical"]
        )
        score += required_score * self.weights["required_skills"]
        
        # Preferred skills match
        preferred_score = self.calculate_skill_match(
            job.get("skills_preferred", []),
            profile["skills"]["technical"],
            required=False
        )
        score += preferred_score * self.weights["preferred_skills"]
        
        # Experience match
        exp_score = self.calculate_experience_match(
            job.get("experience_years", "0-0"),
            profile["basic_info"]["years_experience"]
        )
        score += exp_score * self.weights["experience"]
        
        # Preferences match
        pref_score = self.calculate_preference_match(job, profile["preferences"])
        score += pref_score * self.weights["preferences"]
        
        # Convert to percentage
        return int(score * 100)
    
    def calculate_skill_match(self, job_skills, user_skills, required=True):
        """
        Calculate skill match score (0-1)
        """
        if not job_skills:
            return 1.0
        
        # Extract skill names from user skills
        user_skill_names = []
        for skill in user_skills:
            if isinstance(skill, dict):
                user_skill_names.append(skill["name"])
            else:
                user_skill_names.append(skill)
        
        # Count matches
        matches = 0
        for skill in job_skills:
            if skill in user_skill_names:
                matches += 1
        
        if required:
            # Required skills: full score only if all match
            return matches / len(job_skills)
        else:
            # Preferred skills: partial credit
            return matches / len(job_skills) if job_skills else 1.0
    
    def calculate_experience_match(self, job_exp_range, user_years):
        """
        Calculate experience match (0-1)
        """
        try:
            # Parse range like "1-3" or "0-2"
            if "-" in job_exp_range:
                min_exp, max_exp = map(int, job_exp_range.split("-"))
            else:
                # Handle "3+" type strings
                if "+" in job_exp_range:
                    min_exp = int(job_exp_range.replace("+", ""))
                    max_exp = 99
                else:
                    min_exp = max_exp = int(job_exp_range)
            
            # User years in range
            if min_exp <= user_years <= max_exp:
                return 1.0
            elif user_years < min_exp:
                # Underqualified - partial credit based on proximity
                return max(0.3, user_years / min_exp)
            else:
                # Overqualified - still good, but slight penalty
                return 0.9
        except:
            # If parsing fails, assume match
            return 0.8
    
    def calculate_preference_match(self, job, preferences):
        """
        Calculate preference match (0-1)
        """
        score = 0
        factors = 0
        
        # Industry match
        job_industry = job.get("industry", "")
        pref_industries = preferences.get("industries", [])
        if pref_industries:
            if job_industry in pref_industries:
                score += 1
            factors += 1
        
        # Work arrangement match
        job_arrangement = job.get("work_arrangement", "")
        pref_arrangement = preferences.get("work_arrangement", "")
        if pref_arrangement:
            if job_arrangement == pref_arrangement:
                score += 1
            elif pref_arrangement == "Hybrid" and job_arrangement == "Remote":
                score += 0.7  # Hybrid users often accept remote
            elif pref_arrangement == "Remote" and job_arrangement == "Hybrid":
                score += 0.8  # Remote users might accept hybrid
            factors += 1
        
        # Check excluded items
        exclude = preferences.get("exclude", [])
        for excluded in exclude:
            if excluded.lower() in job.get("title", "").lower():
                return 0  # Hard exclude
            if excluded in job.get("industry", ""):
                return 0
        
        if factors == 0:
            return 1.0
        
        return score / factors
    
    def generate_explanation(self, job, profile, score):
        """
        Generate human-readable explanation for match
        """
        explanation_parts = []
        
        # Overall assessment
        if score >= 90:
            explanation_parts.append("Excellent match!")
        elif score >= 80:
            explanation_parts.append("Strong match")
        elif score >= 70:
            explanation_parts.append("Good potential match")
        else:
            explanation_parts.append("Possible match")
        
        # Skill matches
        user_skills = []
        for skill in profile["skills"]["technical"]:
            if isinstance(skill, dict):
                user_skills.append(skill["name"])
            else:
                user_skills.append(skill)
        
        required = job.get("skills_required", [])
        matching_required = [s for s in required if s in user_skills]
        if matching_required:
            explanation_parts.append(f"Matches: {', '.join(matching_required[:3])}")
        
        # Skill gaps
        missing_required = [s for s in required if s not in user_skills]
        if missing_required and score < 80:
            explanation_parts.append(f"Gap: {', '.join(missing_required[:2])}")
        
        # Experience
        job_exp = job.get("experience_years", "")
        user_exp = profile["basic_info"]["years_experience"]
        explanation_parts.append(f"Your {user_exp} years vs {job_exp} required")
        
        # Industry
        job_industry = job.get("industry", "")
        pref_industries = profile["preferences"].get("industries", [])
        if job_industry and pref_industries and job_industry in pref_industries:
            explanation_parts.append(f"Matches your {job_industry} preference")
        
        return " | ".join(explanation_parts)