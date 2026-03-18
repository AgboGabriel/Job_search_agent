
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
import asyncio
import json
from datetime import datetime, timedelta
from collections import Counter

from behaviors.notification_behavior import NotificationBehaviour


class ReportingBehaviour(PeriodicBehaviour):
    """
    Behavior for generating and sending reports:
    - Weekly digests
    - Progress tracking
    - Market insights
    """
    
    def __init__(self, period, agent):
        super().__init__(period)
        self.agent = agent
        self.pending_requests = []
        
    async def run(self):
        """Generate and send reports"""
        print(f"\nRunning weekly report generation at {datetime.now().strftime('%H:%M:%S')}")
        
        # Process any pending requests
        if self.pending_requests:
            req = self.pending_requests.pop(0)
            await self.generate_custom_report(req["user_id"], req.get("period", "week"))
        
        # Generate reports for all active users
        await self.generate_weekly_digests()
        
        print(f"Report generation complete")
    
    def add_message(self, msg_data):
        """Add a report request to queue"""
        self.pending_requests.append({
            "user_id": msg_data["sender"],
            "period": msg_data["content"].get("period", "week")
        })
    
    async def generate_weekly_digests(self):
        """Generate weekly digests for all users"""
        for user_id, profile in self.agent.user_profiles.items():
            # Skip users in onboarding
            if profile["conversation_state"]["current_context"] == "onboarding":
                continue
            
            await self.generate_user_digest(user_id, profile)
    
    async def generate_user_digest(self, user_id, profile):
        """Generate digest for a single user"""
        # Calculate date range (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        
        # Get user's match history
        user_matches = [m for m in self.agent.match_history 
                       if m["user_id"] == user_id 
                       and datetime.fromisoformat(m["presented_to_user"]) > week_ago]
        
        # Get user's interactions
        clicked = profile["interaction_history"]["jobs_clicked"]
        saved = profile["interaction_history"]["jobs_saved"]
        ignored = profile["interaction_history"]["jobs_ignored"]
        
       
        
        # Compile stats
        stats = {
            "jobs_found": len(user_matches),
            "jobs_clicked": len(clicked[-10:]),  # Approx
            "jobs_saved": len(saved[-5:]),
            "jobs_ignored": len(ignored[-10:]),
            "applications": len(profile["interaction_history"]["applications_submitted"]),
            "interviews": len(profile["interaction_history"]["interviews_received"])
        }
        
        # Calculate engagement rate
        if stats["jobs_found"] > 0:
            stats["engagement_rate"] = round((stats["jobs_clicked"] / stats["jobs_found"]) * 100)
        else:
            stats["engagement_rate"] = 0
        
        # Get top industries from clicked jobs
        clicked_jobs = []
        for job_id in clicked[-10:]:
            job = self.find_job_by_id(job_id)
            if job:
                clicked_jobs.append(job)
        
        if clicked_jobs:
            industries = Counter([j.get("industry", "Unknown") for j in clicked_jobs])
            top_industry = industries.most_common(1)[0][0] if industries else "None"
            stats["top_industry"] = top_industry
        
        # Get market insights
        market = self.get_market_insights(profile)
        
        # Create digest message
        summary = f"Last week: {stats['jobs_found']} jobs found, you viewed {stats['jobs_clicked']} ({stats['engagement_rate']}% engagement rate)."
        
        # Find notification behavior
        for beh in self.agent.behaviours:
            if isinstance(beh, NotificationBehaviour):
                beh.queue_notification(
                    user_id=user_id,
                    notification_type="digest",
                    content={
                        "summary": summary,
                        "stats": stats,
                        "market": market
                    },
                    priority="normal"
                )
                break
    
    async def generate_custom_report(self, user_id, period):
        """Generate custom report for a user"""
        # Similar to digest but with custom period
        pass
    
    def find_job_by_id(self, job_id):
        """Find job by ID in database"""
        for job in self.agent.job_database:
            if job["id"] == job_id:
                return job
        return None
    
    def get_market_insights(self, profile):
        """Get market insights relevant to user"""
        # Get user's target skills
        user_skills = []
        for skill in profile["skills"]["technical"]:
            if isinstance(skill, dict):
                user_skills.append(skill["name"])
            else:
                user_skills.append(skill)
        
        # Count skill demand in job database
        skill_demand = {}
        for job in self.agent.job_database:
            for skill in job.get("skills_required", []):
                skill_demand[skill] = skill_demand.get(skill, 0) + 1
        
        # Find trending skills (simplified)
        trending = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Find skills user has that are in demand
        in_demand = [s for s in user_skills if s in skill_demand]
        
        # Find skills user lacks that are in demand
        missing_demand = [s for s, count in trending if s not in user_skills][:3]
        
        return {
            "trending_skills": trending,
            "your_in_demand_skills": in_demand[:3],
            "skills_to_consider": missing_demand
        }