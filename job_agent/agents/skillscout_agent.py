
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import json
import os
from datetime import datetime

from config.settings import (
    AGENT_JID, AGENT_PASSWORD, SAMPLE_JOBS_PATH, 
    USER_PROFILES_PATH, MINIMUM_MATCH_SCORE
)
from behaviors.onboarding_behavior import OnboardingBehaviour
from behaviors.search_behavior import JobSearchBehaviour
from behaviors.conversation_behavior import ConversationBehaviour
from behaviors.learning_behavior import LearningBehaviour
from behaviors.notification_behavior import NotificationBehaviour
from behaviors.reporting_behavior import ReportingBehaviour
from utils.matcher import JobMatcher
from utils.parser import CV_Parser
from utils.helpers import load_json, save_json, generate_id


class SkillScoutAgent(Agent):
    """
    Main SkillScout Agent class for job matching
    """
    
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.user_profiles = {}      # Store user profiles
        self.job_database = []        # Store job listings - MUST be a list
        self.match_history = []       # Store match records
        self.conversations = {}        # Track active conversations
        self.matcher = JobMatcher()    # Job matching utility
        self.parser = CV_Parser()       # CV parsing utility
        
    async def setup(self):
        """Setup the agent with initial data and behaviors"""
        print(f"\n{'='*60}")
        print(f"SkillScout Agent {self.jid} starting up...")
        print(f"{'='*60}")
        
        # Load sample data
        await self.load_sample_data()
        
        # Add all behaviors
        self.add_behaviour(self.MessageHandlerBehaviour())
        self.add_behaviour(OnboardingBehaviour(period=None))  # Event-driven
        self.add_behaviour(JobSearchBehaviour(period=60, agent=self))  # Every 60 seconds
        self.add_behaviour(ConversationBehaviour(period=None))  # Event-driven
        self.add_behaviour(LearningBehaviour(period=300, agent=self))  # Every 5 minutes
        self.add_behaviour(NotificationBehaviour(period=None))  # Event-driven
        self.add_behaviour(ReportingBehaviour(period=86400, agent=self))  # Every 24 hours
        
        print(f" Behaviors registered:")
        print(f"   - MessageHandler (always active)")
        print(f"   - Onboarding (event-driven)")
        print(f"   - JobSearch (every 60s)")
        print(f"   - Conversation (event-driven)")
        print(f"   - Learning (every 300s)")
        print(f"   - Notification (event-driven)")
        print(f"   - Reporting (every 86400s)")
        
        print(f"\n SkillScout Agent ready!")
        print(f"{'='*60}\n")
        
    async def load_sample_data(self):
        """Load sample job and user data from files"""
        try:
            # Always start with default jobs
            default_jobs = self.create_default_jobs()
            self.job_database = default_jobs  # Ensure it's a list
            print(f"Created {len(self.job_database)} default jobs")
            
            # Try to load from file to enhance (but don't replace)
            if os.path.exists(SAMPLE_JOBS_PATH):
                try:
                    file_jobs = load_json(SAMPLE_JOBS_PATH)
                    if file_jobs and isinstance(file_jobs, list):
                        # Merge with existing jobs
                        existing_ids = [job.get("id") for job in self.job_database]
                        for job in file_jobs:
                            if job.get("id") not in existing_ids:
                                self.job_database.append(job)
                        print(f" Added {len(file_jobs)} jobs from file")
                except Exception as e:
                    print(f"Could not load from file: {e}")
            
            # Load user profiles
            if os.path.exists(USER_PROFILES_PATH):
                profiles = load_json(USER_PROFILES_PATH)
                if profiles and isinstance(profiles, dict):
                    self.user_profiles = profiles
                    print(f"Loaded {len(self.user_profiles)} existing user profiles")
                else:
                    self.user_profiles = {}
                    save_json(USER_PROFILES_PATH, self.user_profiles)
            else:
                self.user_profiles = {}
                save_json(USER_PROFILES_PATH, self.user_profiles)
                print(f"Created empty user profiles database")
                
        except Exception as e:
            print(f"Error loading sample data: {e}")
            # Ensure we always have jobs as a list
            if not isinstance(self.job_database, list) or len(self.job_database) == 0:
                self.job_database = self.create_default_jobs()
                print(f"Created fallback {len(self.job_database)} default jobs")
    
    def create_default_jobs(self):
        """Create default job listings"""
        print("Creating default job listings...")
        jobs = [
            {
                "id": 101,
                "title": "Junior Qt Developer",
                "company": "AutoTech Solutions",
                "location": "Munich (Hybrid)",
                "skills_required": ["C++", "Qt"],
                "skills_preferred": ["CMake", "QML"],
                "experience_years": "1-3",
                "industry": "Automotive",
                "description": "Looking for a junior Qt developer to work on automotive infotainment systems. Welcomes career changers with programming experience in other languages.",
                "welcomes_career_changers": True,
                "work_arrangement": "Hybrid",
                "salary_min": 55000,
                "salary_max": 70000,
                "currency": "EUR",
                "posted_date": "2026-03-14"
            },
            {
                "id": 102,
                "title": "Python Backend Developer",
                "company": "TechLogic Solutions",
                "location": "Remote",
                "skills_required": ["Python", "SQL", "REST APIs"],
                "skills_preferred": ["Flask", "Docker", "PostgreSQL"],
                "experience_years": "0-2",
                "industry": "Technology",
                "description": "Entry-level backend position for recent graduates. Mentorship program available.",
                "welcomes_career_changers": False,
                "work_arrangement": "Remote",
                "salary_min": 65000,
                "salary_max": 85000,
                "currency": "USD",
                "posted_date": "2026-03-15"
            },
            {
                "id": 103,
                "title": "Associate Data Scientist",
                "company": "FinCorp Analytics",
                "location": "New York (Hybrid)",
                "skills_required": ["Python", "SQL", "Machine Learning"],
                "skills_preferred": ["Finance", "Tableau", "Pandas"],
                "experience_years": "3-5",
                "industry": "Financial Services",
                "description": "Data scientist with finance background preferred. Will consider career changers with strong domain expertise.",
                "welcomes_career_changers": True,
                "work_arrangement": "Hybrid",
                "salary_min": 110000,
                "salary_max": 140000,
                "currency": "USD",
                "posted_date": "2026-03-13"
            },
            {
                "id": 104,
                "title": "Junior C++ Developer",
                "company": "GameWorks Studio",
                "location": "Remote",
                "skills_required": ["C++", "Data Structures"],
                "skills_preferred": ["Unreal Engine", "Game Development"],
                "experience_years": "0-2",
                "industry": "Gaming",
                "description": "Entry-level C++ role for game development. Training provided.",
                "welcomes_career_changers": False,
                "work_arrangement": "Remote",
                "salary_min": 60000,
                "salary_max": 80000,
                "currency": "USD",
                "posted_date": "2026-03-12"
            },
            {
                "id": 105,
                "title": "Qt/QML Developer",
                "company": "MedTech Devices",
                "location": "Berlin (Hybrid)",
                "skills_required": ["C++", "Qt", "QML"],
                "skills_preferred": ["Medical device experience", "UI/UX"],
                "experience_years": "2-4",
                "industry": "Medical Technology",
                "description": "Develop interfaces for medical devices. Qt expertise required.",
                "welcomes_career_changers": False,
                "work_arrangement": "Hybrid",
                "salary_min": 65000,
                "salary_max": 85000,
                "currency": "EUR",
                "posted_date": "2026-03-14"
            }
        ]
        print(f"Created {len(jobs)} default jobs")
        return jobs
    
    def find_matching_jobs(self, user_id, limit=5):
        """Find jobs matching user profile"""
        if user_id not in self.user_profiles:
            return []
        
        profile = self.user_profiles[user_id]
        matches = []
        
        for job in self.job_database:
            score = self.matcher.calculate_match_score(job, profile)
            
            if score >= MINIMUM_MATCH_SCORE:
                explanation = self.matcher.generate_explanation(job, profile, score)
                matches.append({
                    "job": job,
                    "score": score,
                    "explanation": explanation
                })
        
        # Sort by score descending
        matches.sort(key=lambda x: x["score"], reverse=True)
        
        # Create match records
        for match in matches[:limit]:
            match_record = {
                "match_id": generate_id("match"),
                "user_id": user_id,
                "job_id": match["job"]["id"],
                "match_score": match["score"],
                "presented_to_user": datetime.now().isoformat(),
                "user_action": None
            }
            self.match_history.append(match_record)
        
        return matches[:limit]
    
    class MessageHandlerBehaviour(CyclicBehaviour):
        """Main behavior for handling incoming messages"""
        
        async def run(self):
            """Wait for and process incoming messages"""
            msg = await self.receive(timeout=5)
            
            if msg:
                sender = str(msg.sender)
                print(f"\nReceived message from {sender}")
                
                try:
                    content = json.loads(msg.body)
                    message_type = content.get("type", "unknown")
                    
                    print(f"   Type: {message_type}")
                    
                    # Route to appropriate behavior based on message type
                    if message_type == "new_user":
                        # Forward to onboarding behavior
                        await self.forward_to_onboarding(sender, content)
                        
                    elif message_type == "user_response":
                        # Forward to conversation behavior
                        await self.forward_to_conversation(sender, content)
                        
                    elif message_type == "job_preference":
                        # Forward to learning behavior
                        await self.forward_to_learning(sender, content)
                        
                    elif message_type == "request_jobs":
                        # Handle directly - find and send matches
                        await self.handle_job_request(sender, content)
                        
                    elif message_type == "request_report":
                        # Forward to reporting behavior
                        await self.forward_to_reporting(sender, content)
                        
                    elif message_type == "command":
                        # Handle system commands
                        await self.handle_command(sender, content)
                        
                    else:
                        print(f" Unknown message type: {message_type}")
                        await self.send_error(sender, f"Unknown message type: {message_type}")
                        
                except json.JSONDecodeError:
                    print(f"Invalid message format: {msg.body}")
                    await self.send_error(sender, "Invalid message format")
            
        async def forward_to_onboarding(self, sender, content):
            """Forward message to onboarding behavior"""
            # Find onboarding behavior
            for beh in self.agent.behaviours:
                if isinstance(beh, OnboardingBehaviour):
                    # Store in queue or trigger directly
                    beh.add_message({"sender": sender, "content": content})
                    print(f"   Forwarded to OnboardingBehaviour")
                    return
            
            await self.send_error(sender, "Onboarding behavior not available")
        
        async def forward_to_conversation(self, sender, content):
            """Forward message to conversation behavior"""
            for beh in self.agent.behaviours:
                if isinstance(beh, ConversationBehaviour):
                    beh.add_message({"sender": sender, "content": content})
                    print(f"   Forwarded to ConversationBehaviour")
                    return
            
            await self.send_error(sender, "Conversation behavior not available")
        
        async def forward_to_learning(self, sender, content):
            """Forward message to learning behavior"""
            for beh in self.agent.behaviours:
                if isinstance(beh, LearningBehaviour):
                    beh.add_message({"sender": sender, "content": content})
                    print(f"   Forwarded to LearningBehaviour")
                    return
            
            await self.send_error(sender, "Learning behavior not available")
        
        async def forward_to_reporting(self, sender, content):
            """Forward message to reporting behavior"""
            for beh in self.agent.behaviours:
                if isinstance(beh, ReportingBehaviour):
                    beh.add_message({"sender": sender, "content": content})
                    print(f"   Forwarded to ReportingBehaviour")
                    return
            
            await self.send_error(sender, "Reporting behavior not available")
        
        async def handle_job_request(self, sender, content):
            """Handle direct job request from user"""
            limit = content.get("limit", 5)
            matches = self.agent.find_matching_jobs(sender, limit)
            
            response = {
                "type": "job_matches",
                "count": len(matches),
                "matches": matches
            }
            
            await self.send_message(sender, response)
        
        async def handle_command(self, sender, content):
            """Handle system commands"""
            command = content.get("command", "")
            
            if command == "list_users":
                users = list(self.agent.user_profiles.keys())
                await self.send_message(sender, {
                    "type": "command_response",
                    "data": {"users": users}
                })
                
            elif command == "list_jobs":
                await self.send_message(sender, {
                    "type": "command_response",
                    "data": {"job_count": len(self.agent.job_database)}
                })
                
            elif command == "status":
                await self.send_message(sender, {
                    "type": "command_response",
                    "data": {
                        "users": len(self.agent.user_profiles),
                        "jobs": len(self.agent.job_database),
                        "matches": len(self.agent.match_history),
                        "behaviors": len(self.agent.behaviours)
                    }
                })
                
            else:
                await self.send_error(sender, f"Unknown command: {command}")
        
        async def send_message(self, to, content):
            """Helper to send JSON messages"""
            msg = Message(to=str(to))
            msg.set_metadata("performative", "inform")
            msg.body = json.dumps(content)
            await self.send(msg)
            print(f"Sent message to {to}")
        
        async def send_error(self, to, error_message):
            """Send error message"""
            await self.send_message(to, {
                "type": "error",
                "message": error_message
            })