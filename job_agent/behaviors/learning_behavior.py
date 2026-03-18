
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
import asyncio
import json
from datetime import datetime, timedelta
from collections import Counter

from config.settings import LEARNING_RESOURCES
from utils.helpers import save_json
from config.settings import USER_PROFILES_PATH


class LearningBehaviour(PeriodicBehaviour):
    """
    Behavior for learning from user interactions:
    - Track clicks, saves, ignores
    - Detect preference patterns
    - Update user profiles
    - Suggest learning resources
    """
    
    def __init__(self, period, agent):
        super().__init__(period)
        self.agent = agent
        self.pending_messages = []
        
    async def run(self):
        """Run periodic learning analysis"""
        print(f"\n Running learning analysis at {datetime.now().strftime('%H:%M:%S')}")
        
        # Process any pending messages
        if self.pending_messages:
            msg_data = self.pending_messages.pop(0)
            await self.process_job_preference(msg_data)
        
        # Analyze patterns for all active users
        await self.analyze_all_users()
        
        print(f"Learning analysis complete")
    
    def add_message(self, msg_data):
        """Add a message to the queue"""
        self.pending_messages.append(msg_data)
    
    async def process_job_preference(self, msg_data):
        """Process user job preference (click/save/ignore)"""
        sender = msg_data["sender"]
        content = msg_data["content"]
        
        job_id = content.get("job_id")
        action = content.get("action")  # "clicked", "saved", "ignored"
        
        if sender not in self.agent.user_profiles:
            return
        
        profile = self.agent.user_profiles[sender]
        
        # Record the action
        if action == "clicked":
            if job_id not in profile["interaction_history"]["jobs_clicked"]:
                profile["interaction_history"]["jobs_clicked"].append(job_id)
                print(f"{sender} clicked job {job_id}")
                
        elif action == "saved":
            if job_id not in profile["interaction_history"]["jobs_saved"]:
                profile["interaction_history"]["jobs_saved"].append(job_id)
                print(f"{sender} saved job {job_id}")
                
        elif action == "ignored":
            if job_id not in profile["interaction_history"]["jobs_ignored"]:
                profile["interaction_history"]["jobs_ignored"].append(job_id)
                print(f"{sender} ignored job {job_id}")
        
        # Update match history
        for match in self.agent.match_history:
            if match["user_id"] == sender and match["job_id"] == job_id:
                match["user_action"] = action
                match["action_timestamp"] = datetime.now().isoformat()
                break
        
        profile["updated_at"] = datetime.now().isoformat()
        save_json(USER_PROFILES_PATH, self.agent.user_profiles)
    
    async def analyze_all_users(self):
        """Analyze patterns for all active users"""
        for user_id, profile in self.agent.user_profiles.items():
            # Skip users in onboarding
            if profile["conversation_state"]["current_context"] == "onboarding":
                continue
            
            # Analyze click patterns
            await self.analyze_user_patterns(user_id, profile)
            
            # Analyze skill gaps
            await self.analyze_skill_gaps(user_id, profile)
    
    async def analyze_user_patterns(self, user_id, profile):
        """Analyze user interaction patterns"""
        clicked = profile["interaction_history"]["jobs_clicked"]
        ignored = profile["interaction_history"]["jobs_ignored"]
        
        # Need enough data to analyze
        if len(clicked) + len(ignored) < 5:
            return
        
        # Find jobs that were clicked and ignored
        clicked_jobs = []
        ignored_jobs = []
        
        for job_id in clicked[-10:]:  # Last 10 clicks
            job = self.find_job_by_id(job_id)
            if job:
                clicked_jobs.append(job)
        
        for job_id in ignored[-10:]:  # Last 10 ignores
            job = self.find_job_by_id(job_id)
            if job:
                ignored_jobs.append(job)
        
        # Analyze patterns
        if clicked_jobs:
            # What industries are they clicking?
            clicked_industries = Counter([j.get("industry", "Unknown") for j in clicked_jobs])
            top_clicked = clicked_industries.most_common(1)
            
            # What role types?
            clicked_roles = Counter([j.get("title", "").split()[0] for j in clicked_jobs])
            
            # Compare with current preferences
            current_prefs = profile["preferences"].get("industries", [])
            
            # If strong pattern detected and different from preferences
            if top_clicked and top_clicked[0][0] not in current_prefs and top_clicked[0][1] >= 3:
                # Suggest preference update
                await self.suggest_preference_update(user_id, top_clicked[0][0])
    
    async def analyze_skill_gaps(self, user_id, profile):
        """Identify common skill gaps for user"""
        # Get jobs user clicked but didn't meet all requirements
        clicked = profile["interaction_history"]["jobs_clicked"]
        
        if len(clicked) < 3:
            return
        
        # Track missing skills
        missing_skills = Counter()
        
        for job_id in clicked:
            job = self.find_job_by_id(job_id)
            if not job:
                continue
            
            # Get user skills
            user_skills = []
            for skill in profile["skills"]["technical"]:
                if isinstance(skill, dict):
                    user_skills.append(skill["name"])
                else:
                    user_skills.append(skill)
            
            # Check required skills
            required = job.get("skills_required", [])
            for skill in required:
                if skill not in user_skills:
                    missing_skills[skill] += 1
            
            # Check preferred skills
            preferred = job.get("skills_preferred", [])
            for skill in preferred:
                if skill not in user_skills:
                    missing_skills[skill] += 0.5  # Half weight for preferred
        
        # Find skills missing in multiple jobs
        top_gaps = [skill for skill, count in missing_skills.items() if count >= 2]
        
        if top_gaps and len(top_gaps) <= 3:
            # Suggest learning for top gaps
            await self.suggest_learning(user_id, top_gaps[0])
    
    def find_job_by_id(self, job_id):
        """Find job by ID in database"""
        for job in self.agent.job_database:
            if job["id"] == job_id:
                return job
        return None
    
    async def suggest_preference_update(self, user_id, new_industry):
        """Suggest updating user preferences"""
        # Check if we already suggested recently
        profile = self.agent.user_profiles.get(user_id)
        if not profile:
            return
        
        last_suggestion = profile.get("last_preference_suggestion")
        if last_suggestion:
            last = datetime.fromisoformat(last_suggestion)
            if datetime.now() - last < timedelta(days=3):
                return  # Don't spam
        
        await self.send_message(user_id, {
            "type": "pattern_insight",
            "observation": f"I notice you've been clicking on many {new_industry} jobs. Would you like me to add {new_industry} to your industry preferences?",
            "suggestion": f"Update preferences to include {new_industry}",
            "requires_confirmation": True
        })
        
        profile["last_preference_suggestion"] = datetime.now().isoformat()
    
    async def suggest_learning(self, user_id, skill):
        """Suggest learning resources for a skill"""
        # Check if already learning
        profile = self.agent.user_profiles.get(user_id)
        if not profile:
            return
        
        if skill in profile["learning"]["in_progress"] or skill in profile["learning"]["completed"]:
            return
        
        # Check if we already suggested recently
        last_suggestion = profile.get("last_learning_suggestion")
        if last_suggestion:
            last = datetime.fromisoformat(last_suggestion)
            if datetime.now() - last < timedelta(days=7):
                return  # Don't spam
        
        # Get resources
        skill_key = skill.lower()
        resources = LEARNING_RESOURCES.get(skill_key, [])
        
        if resources:
            await self.send_message(user_id, {
                "type": "learning_suggestion",
                "skill": skill,
                "message": f"I notice many jobs you're interested in require {skill}. Would you like to learn it?",
                "resources": resources[:2]  # Top 2 resources
            })
            
            profile["learning"]["recommended"].append(skill)
            profile["last_learning_suggestion"] = datetime.now().isoformat()
            save_json(USER_PROFILES_PATH, self.agent.user_profiles)
    
    async def send_message(self, to, content):
        """Helper to send JSON messages"""
        msg = Message(to=str(to))
        msg.set_metadata("performative", "inform")
        msg.body = json.dumps(content)
        await self.send(msg)