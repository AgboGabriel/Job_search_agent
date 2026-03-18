
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import json
from datetime import datetime

from utils.parser import CV_Parser
from utils.helpers import save_json
from config.settings import USER_PROFILES_PATH, WELCOME_MESSAGE, PROFILE_COMPLETE_MESSAGE


class OnboardingBehaviour(CyclicBehaviour):
    """
    Behavior for onboarding new users:
    - Process CV uploads
    - Ask preference questions
    - Build initial profile
    """
    
    def __init__(self, period=None):
        super().__init__()
        self.pending_onboardings = []  # Queue of users to onboard
        self.onboarding_state = {}      # Track state for each user
        
    async def run(self):
        """Process any pending onboarding requests"""
        if self.pending_onboardings:
            # Get next onboarding
            onboarding = self.pending_onboardings.pop(0)
            await self.process_onboarding(onboarding)
        
        await asyncio.sleep(1)
    
    def add_message(self, msg_data):
        """Add a new onboarding request to queue"""
        self.pending_onboardings.append(msg_data)
        print(f"Added user {msg_data['sender']} to onboarding queue")
    
    async def process_onboarding(self, onboarding):
        """Process a single user onboarding"""
        sender = onboarding["sender"]
        content = onboarding["content"]
        
        # Extract user data
        user_data = content.get("user_data", {})
        cv_content = content.get("cv", None)
        
        # Step 1: Parse CV if provided
        if cv_content:
            parsed_data = self.agent.parser.parse_cv(cv_content)
            # Merge parsed data with provided data
            user_data.update(parsed_data)
        
        # Step 2: Create initial profile
        user_id = sender
        self.agent.user_profiles[user_id] = {
            "user_id": user_id,
            "basic_info": {
                "name": user_data.get("name", "User"),
                "years_experience": user_data.get("experience", 0),
                "current_role": user_data.get("current_role", ""),
                "target_role": user_data.get("target_role", ""),
                "education": user_data.get("education", "")
            },
            "skills": {
                "technical": user_data.get("skills", []),
                "soft": user_data.get("soft_skills", [])
            },
            "preferences": {
                "role_types": [],
                "industries": [],
                "locations": [],
                "work_arrangement": "",
                "exclude": []
            },
            "learning": {
                "in_progress": [],
                "completed": user_data.get("certifications", []),
                "recommended": []
            },
            "interaction_history": {
                "jobs_clicked": [],
                "jobs_saved": [],
                "jobs_ignored": [],
                "applications_submitted": [],
                "interviews_received": []
            },
            "conversation_state": {
                "current_context": "onboarding",
                "step": 1,
                "last_interaction": datetime.now().isoformat(),
                "pending_questions": []
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save to file
        save_json(USER_PROFILES_PATH, self.agent.user_profiles)
        
        # Step 3: Send welcome message
        welcome = WELCOME_MESSAGE.format(
            name=self.agent.user_profiles[user_id]["basic_info"]["name"]
        )
        
        await self.send_message(sender, {
            "type": "welcome",
            "message": welcome
        })
        
        # Step 4: Start asking questions
        await self.ask_next_question(sender)
    
    async def ask_next_question(self, user_id):
        """Ask the next onboarding question"""
        profile = self.agent.user_profiles.get(user_id)
        if not profile:
            return
        
        step = profile["conversation_state"]["step"]
        
        questions = [
            {
                "step": 1,
                "question": "What type of role are you most interested in?",
                "options": ["Backend Developer", "Frontend Developer", "Full Stack", 
                           "Data Scientist", "DevOps", "Mobile Developer", "Qt/C++ Developer"]
            },
            {
                "step": 2,
                "question": "Do you have any industry preferences?",
                "options": ["Technology", "Finance", "Healthcare", "Automotive", 
                           "Gaming", "Education", "No preference"]
            },
            {
                "step": 3,
                "question": "What work arrangement do you prefer?",
                "options": ["Remote", "Hybrid", "On-site", "No preference"]
            },
            {
                "step": 4,
                "question": "Are there any roles or industries you want to avoid?",
                "options": ["None", "Embedded Systems", "Legacy Code", 
                           "Finance", "Healthcare", "Other (specify in response)"]
            }
        ]
        
        if step <= len(questions):
            q = questions[step-1]
            await self.send_message(user_id, {
                "type": "onboarding_question",
                "question_id": f"onboard_q{step}",
                "step": step,
                "question": q["question"],
                "options": q["options"]
            })
            
            # Update state
            profile["conversation_state"]["step"] = step
            profile["conversation_state"]["last_interaction"] = datetime.now().isoformat()
            profile["conversation_state"]["pending_questions"].append(f"onboard_q{step}")
            
        else:
            # Onboarding complete
            await self.complete_onboarding(user_id)
    
    async def process_response(self, user_id, question_id, response):
        """Process user response to onboarding question"""
        profile = self.agent.user_profiles.get(user_id)
        if not profile:
            return
        
        # Remove from pending
        if question_id in profile["conversation_state"]["pending_questions"]:
            profile["conversation_state"]["pending_questions"].remove(question_id)
        
        # Extract step number from question_id
        if question_id.startswith("onboard_q"):
            step = int(question_id.replace("onboard_q", ""))
            
            # Update profile based on step
            if step == 1:
                profile["preferences"]["role_types"] = [response]
            elif step == 2:
                if response != "No preference":
                    profile["preferences"]["industries"] = [response]
            elif step == 3:
                if response != "No preference":
                    profile["preferences"]["work_arrangement"] = response
            elif step == 4:
                if response != "None":
                    profile["preferences"]["exclude"] = [response]
            
            profile["updated_at"] = datetime.now().isoformat()
            
            # Move to next question
            profile["conversation_state"]["step"] += 1
            await self.ask_next_question(user_id)
    
    async def complete_onboarding(self, user_id):
        """Mark onboarding as complete"""
        profile = self.agent.user_profiles.get(user_id)
        if not profile:
            return
        
        profile["conversation_state"]["current_context"] = "active"
        profile["updated_at"] = datetime.now().isoformat()
        
        # Save profile
        save_json(USER_PROFILES_PATH, self.agent.user_profiles)
        
        # Send completion message
        focus = profile["preferences"]["role_types"][0] if profile["preferences"]["role_types"] else "various"
        industries = ", ".join(profile["preferences"]["industries"]) if profile["preferences"]["industries"] else "any"
        arrangement = profile["preferences"]["work_arrangement"] if profile["preferences"]["work_arrangement"] else "any"
        
        message = PROFILE_COMPLETE_MESSAGE.format(
            focus=focus,
            industries=industries,
            arrangement=arrangement
        )
        
        await self.send_message(user_id, {
            "type": "onboarding_complete",
            "message": message
        })
        
        print(f"Onboarding complete for {user_id}")
    
    async def send_message(self, to, content):
        """Helper to send JSON messages"""
        msg = Message(to=str(to))
        msg.set_metadata("performative", "inform")
        msg.body = json.dumps(content)
        await self.send(msg)