
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import json
from datetime import datetime


class NotificationBehaviour(CyclicBehaviour):
    """
    Behavior for sending notifications to users:
    - Job alerts
    - Learning suggestions
    - Reminders
    """
    
    def __init__(self, period=None):
        super().__init__()
        self.notification_queue = []  # Queue of notifications to send
        
    async def run(self):
        """Process any pending notifications"""
        if self.notification_queue:
            notification = self.notification_queue.pop(0)
            await self.send_notification(notification)
        
        await asyncio.sleep(2)
    
    def queue_notification(self, user_id, notification_type, content, priority="normal"):
        """Add notification to queue"""
        self.notification_queue.append({
            "user_id": user_id,
            "type": notification_type,
            "content": content,
            "priority": priority,
            "created": datetime.now().isoformat()
        })
        
        priority_flag = "🔴" if priority == "high" else "🟡"
        print(f"{priority_flag} Queued {notification_type} notification for {user_id}")
    
    async def send_notification(self, notification):
        """Send a single notification"""
        user_id = notification["user_id"]
        notif_type = notification["type"]
        content = notification["content"]
        
        # Format notification based on type
        if notif_type == "job_alert":
            message = {
                "type": "notification",
                "notification_type": "job_alert",
                "title": f" {content.get('count', 0)} New Job Matches",
                "body": content.get('message', 'Check out your new matches!'),
                "data": content.get('jobs', [])
            }
            
        elif notif_type == "learning_suggestion":
            message = {
                "type": "notification",
                "notification_type": "learning",
                "title": f"Learning Suggestion",
                "body": content.get('message', 'Consider learning a new skill'),
                "data": content.get('resources', [])
            }
            
        elif notif_type == "reminder":
            message = {
                "type": "notification",
                "notification_type": "reminder",
                "title": f" Reminder",
                "body": content.get('message', ''),
                "data": {}
            }
            
        elif notif_type == "digest":
            message = {
                "type": "notification",
                "notification_type": "digest",
                "title": f"Your Weekly Job Search Digest",
                "body": content.get('summary', ''),
                "data": content.get('stats', {})
            }
            
        else:
            message = {
                "type": "notification",
                "notification_type": "general",
                "title": content.get('title', 'Notification'),
                "body": content.get('message', ''),
                "data": {}
            }
        
        # Add priority
        message["priority"] = notification["priority"]
        
        # Send
        await self.send_message(user_id, message)
        
        print(f"Sent {notif_type} notification to {user_id}")
    
    async def send_message(self, to, content):
        """Helper to send JSON messages"""
        msg = Message(to=str(to))
        msg.set_metadata("performative", "inform")
        msg.body = json.dumps(content)
        await self.send(msg)