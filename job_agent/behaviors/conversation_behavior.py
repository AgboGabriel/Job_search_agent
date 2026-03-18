
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import json
from datetime import datetime

from behaviors.onboarding_behavior import OnboardingBehaviour


class ConversationBehaviour(CyclicBehaviour):
    """
    Behavior for managing conversations with users:
    - Handle responses to questions
    - Answer user queries
    - Maintain conversation context
    """
    
    def __init__(self, period=None):
        super().__init__()
        self.pending_messages = []
        self.conversation_templates = {
            "greeting": [
                "Hello! How can I help with your job search today?",
                "Hi there! Looking for new opportunities?",
                "Welcome back! Ready to find some jobs?"
            ],
            "help": [
                "I can help you find jobs matching your skills. Just tell me what you're looking for, or ask me about your matches.",
                "Try asking me about new jobs, updating your preferences, or learning resources."
            ],
            "thanks": [
                "You're welcome! Happy to help.",
                "Glad I could assist!",
                "Anytime! That's what I'm here for."
            ]
        }
        
    async def run(self):
        """Process any pending conversation messages"""
        if self.pending_messages:
            msg_data = self.pending_messages.pop(0)
            await self.process_conversation(msg_data)
        
        await asyncio.sleep(1)
    
    def add_message(self, msg_data):
        """Add a new message to the conversation queue"""
        self.pending_messages.append(msg_data)
    
    async def process_conversation(self, msg_data):
        """Process a conversation message"""
        sender = msg_data["sender"]
        content = msg_data["content"]
        
        # Check if this is a response to an onboarding question
        if content.get("in_response_to", "").startswith("onboard_q"):
            # Forward to onboarding behavior
            await self.forward_to_onboarding(sender, content)
            return
        
        # Handle different message types
        message_type = content.get("type", "unknown")
        
        if message_type == "user_response":
            await self.handle_user_response(sender, content)
        elif message_type == "user_query":
            await self.handle_user_query(sender, content)
        elif message_type == "feedback":
            await self.handle_feedback(sender, content)
        else:
            await self.handle_general_message(sender, content)
    
    async def forward_to_onboarding(self, sender, content):
        """Forward response to onboarding behavior"""
        for beh in self.agent.behaviours:
            if isinstance(beh, OnboardingBehaviour):
                # Extract question info
                question_id = content.get("in_response_to")
                response = content.get("response", "")
                
                # Process in onboarding
                await beh.process_response(sender, question_id, response)
                return
        
        # Fallback
        await self.send_message(sender, {
            "type": "error",
            "message": "Could not process onboarding response"
        })
    
    async def handle_user_response(self, sender, content):
        """Handle general user responses"""
        response = content.get("response", "")
        
        # Simple response handling
        if "hello" in response.lower() or "hi" in response.lower():
            await self.send_greeting(sender)
        elif "thank" in response.lower():
            await self.send_thanks_response(sender)
        elif "help" in response.lower():
            await self.send_help_response(sender)
        else:
            # Default response
            await self.send_message(sender, {
                "type": "acknowledgment",
                "message": f"I understand. Is there anything specific about your job search you'd like help with?"
            })
    
    async def handle_user_query(self, sender, content):
        """Handle specific user queries"""
        query = content.get("query", "").lower()
        
        if "new jobs" in query or "matches" in query:
            # User wants to see new matches
            await self.trigger_job_search(sender)
            
        elif "profile" in query or "preferences" in query:
            # User wants to see/update profile
            await self.show_profile(sender)
            
        elif "learn" in query or "course" in query or "skill" in query:
            # User wants learning resources
            await self.suggest_learning(sender, query)
            
        elif "market" in query or "trend" in query:
            # User wants market insights
            await self.show_market_insights(sender)
            
        else:
            # Unknown query
            await self.send_message(sender, {
                "type": "query_response",
                "message": "I'm not sure about that. You can ask me about new jobs, your profile, learning resources, or market trends."
            })
    
    async def handle_feedback(self, sender, content):
        """Handle user feedback"""
        feedback = content.get("feedback", "")
        rating = content.get("rating", None)
        
        print(f"Received feedback from {sender}: {feedback}")
        
        # Store feedback (could save to file)
        
        await self.send_message(sender, {
            "type": "feedback_ack",
            "message": "Thank you for your feedback! It helps me improve."
        })
    
    async def handle_general_message(self, sender, content):
        """Handle general messages"""
        message = content.get("message", "")
        
        if message:
            # Try to interpret the message
            if "?" in message:
                # Treat as question
                await self.handle_user_query(sender, {"query": message})
            else:
                # Treat as statement
                await self.send_message(sender, {
                    "type": "response",
                    "message": "Thanks for your message. How can I help with your job search today?"
                })
    
    async def send_greeting(self, sender):
        """Send greeting message"""
        import random
        greeting = random.choice(self.conversation_templates["greeting"])
        await self.send_message(sender, {
            "type": "greeting",
            "message": greeting
        })
    
    async def send_help_response(self, sender):
        """Send help message"""
        help_msg = random.choice(self.conversation_templates["help"])
        await self.send_message(sender, {
            "type": "help",
            "message": help_msg
        })
    
    async def send_thanks_response(self, sender):
        """Send thanks response"""
        thanks = random.choice(self.conversation_templates["thanks"])
        await self.send_message(sender, {
            "type": "acknowledgment",
            "message": thanks
        })
    
    async def trigger_job_search(self, sender):
        """Trigger immediate job search for user"""
        matches = self.agent.find_matching_jobs(sender, limit=3)
        
        if matches:
            await self.send_message(sender, {
                "type": "job_matches",
                "message": f"I found {len(matches)} jobs matching your profile:",
                "matches": matches
            })
        else:
            await self.send_message(sender, {
                "type": "job_matches",
                "message": "I don't have any new matches for you right now. I'll keep searching!"
            })
    
    async def show_profile(self, sender):
        """Show user their profile"""
        profile = self.agent.user_profiles.get(sender)
        if profile:
            # Create a summary
            summary = {
                "name": profile["basic_info"]["name"],
                "experience": f"{profile['basic_info']['years_experience']} years",
                "skills": [s["name"] if isinstance(s, dict) else s for s in profile["skills"]["technical"]][:5],
                "preferences": profile["preferences"]
            }
            
            await self.send_message(sender, {
                "type": "profile_summary",
                "profile": summary
            })
        else:
            await self.send_message(sender, {
                "type": "error",
                "message": "I don't have a profile for you yet. Please upload your CV first."
            })
    
    async def suggest_learning(self, sender, query):
        """Suggest learning resources"""
        from config.settings import LEARNING_RESOURCES
        
        # Try to extract skill from query
        skill = None
        for known_skill in LEARNING_RESOURCES.keys():
            if known_skill in query:
                skill = known_skill
                break
        
        if skill:
            resources = LEARNING_RESOURCES.get(skill, [])
            await self.send_message(sender, {
                "type": "learning_resources",
                "skill": skill,
                "resources": resources
            })
        else:
            # Show available skills
            skills = list(LEARNING_RESOURCES.keys())
            await self.send_message(sender, {
                "type": "learning_help",
                "message": f"I have resources for: {', '.join(skills)}. Which skill are you interested in?"
            })
    
    async def show_market_insights(self, sender):
        """Show job market insights"""
        # Simple insights based on job database
        job_count = len(self.agent.job_database)
        
        # Count by industry
        industries = {}
        for job in self.agent.job_database:
            ind = job.get("industry", "Unknown")
            industries[ind] = industries.get(ind, 0) + 1
        
        # Most in-demand skills
        skills_count = {}
        for job in self.agent.job_database:
            for skill in job.get("skills_required", []):
                skills_count[skill] = skills_count.get(skill, 0) + 1
        
        top_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        await self.send_message(sender, {
            "type": "market_insights",
            "total_jobs": job_count,
            "industries": industries,
            "top_skills": top_skills
        })
    
    async def send_message(self, to, content):
        """Helper to send JSON messages"""
        msg = Message(to=str(to))
        msg.set_metadata("performative", "inform")
        msg.body = json.dumps(content)
        await self.send(msg)