
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
import asyncio
import json
import random
from datetime import datetime

from config.settings import EXCELLENT_MATCH_SCORE


class JobSearchBehaviour(PeriodicBehaviour):
    """
    Periodically searches for new job matches and notifies users
    """
    
    def __init__(self, period, agent):
        super().__init__(period)
        self.agent = agent
        self.last_search = datetime.now()
        self.search_count = 0
        
    async def run(self):
        """Run periodic job search"""
        self.search_count += 1
        print(f"\nRunning scheduled job search #{self.search_count} at {datetime.now().strftime('%H:%M:%S')}")
        
        # Simulate finding new jobs (for demo purposes)
        new_jobs = self.simulate_new_jobs()
        
        if new_jobs:
            print(f"Found {len(new_jobs)} new jobs")
            # Add to database
            for job in new_jobs:
                job["id"] = 1000 + len(self.agent.job_database) + 1
                self.agent.job_database.append(job)
            
            # Notify users about new matches
            await self.notify_users(new_jobs)
        else:
            print(f"No new jobs found")
        
        self.last_search = datetime.now()
    
    def simulate_new_jobs(self):
        """Simulate finding new job postings (for prototype)"""
        # 40% chance of finding new jobs
        if random.random() < 0.4:
            job_templates = [
                {
                    "title": "Junior Qt/C++ Developer",
                    "company": "AutoTech Innovations",
                    "location": "Munich (Hybrid)",
                    "skills_required": ["C++", "Qt"],
                    "skills_preferred": ["CMake"],
                    "experience_years": "0-2",
                    "industry": "Automotive",
                    "description": "New position for junior Qt developer...",
                    "welcomes_career_changers": True,
                    "work_arrangement": "Hybrid"
                },
                {
                    "title": "Python Developer",
                    "company": "StartupHub",
                    "location": "Remote",
                    "skills_required": ["Python", "SQL"],
                    "skills_preferred": ["Django"],
                    "experience_years": "1-3",
                    "industry": "Technology",
                    "description": "Growing startup seeks Python developer...",
                    "welcomes_career_changers": False,
                    "work_arrangement": "Remote"
                },
                {
                    "title": "Data Analyst",
                    "company": "FinTech Corp",
                    "location": "London (Hybrid)",
                    "skills_required": ["Python", "SQL", "Excel"],
                    "skills_preferred": ["Tableau"],
                    "experience_years": "2-4",
                    "industry": "Finance",
                    "description": "Financial data analysis role...",
                    "welcomes_career_changers": True,
                    "work_arrangement": "Hybrid"
                }
            ]
            
            # Return 1-2 random jobs
            count = random.randint(1, 2)
            selected = random.sample(job_templates, min(count, len(job_templates)))
            
            # Add timestamps
            for job in selected:
                job["posted_date"] = datetime.now().strftime("%Y-%m-%d")
                job["salary_min"] = random.randint(50000, 70000)
                job["salary_max"] = job["salary_min"] + random.randint(10000, 20000)
                job["currency"] = random.choice(["USD", "EUR"])
            
            return selected
        return []
    
    async def notify_users(self, new_jobs):
        """Notify all users about new matching jobs"""
        for user_id, profile in self.agent.user_profiles.items():
            # Skip users still in onboarding
            if profile["conversation_state"]["current_context"] == "onboarding":
                continue
            
            # Find matches for this user
            user_matches = []
            for job in new_jobs:
                score = self.agent.matcher.calculate_match_score(job, profile)
                
                if score >= 60:  # Minimum threshold
                    explanation = self.agent.matcher.generate_explanation(job, profile, score)
                    user_matches.append({
                        "job": job,
                        "score": score,
                        "explanation": explanation
                    })
            
            if user_matches:
                # Determine urgency
                urgent = any(m["score"] >= EXCELLENT_MATCH_SCORE for m in user_matches)
                
                # Send notification
                msg = Message(to=user_id)
                msg.set_metadata("performative", "inform")
                msg.body = json.dumps({
                    "type": "new_jobs_alert",
                    "urgent": urgent,
                    "count": len(user_matches),
                    "matches": user_matches
                })
                
                await self.send(msg)
                print(f"Notified {user_id} about {len(user_matches)} new jobs")
                
                # Record in match history
                for match in user_matches:
                    match_record = {
                        "match_id": f"m-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id[:5]}",
                        "user_id": user_id,
                        "job_id": match["job"]["id"],
                        "match_score": match["score"],
                        "presented_to_user": datetime.now().isoformat(),
                        "user_action": None
                    }
                    self.agent.match_history.append(match_record)