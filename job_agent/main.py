
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from agents.skillscout_agent import SkillScoutAgent
from config.settings import AGENT_JID, AGENT_PASSWORD
import json
from datetime import datetime


async def create_default_users(agent):
    """Create default users from the scenarios"""
    print("\nCreating default users from scenarios...")
    
    # Default users data
    default_users = [
        {
            "jid": "daniel@localhost",
            "name": "Daniel Chen",
            "experience": 4,
            "current_role": "JavaScript Developer",
            "target_role": "Qt Developer",
            "skills": [
                {"name": "JavaScript", "level": "expert", "years": 4},
                {"name": "React", "level": "advanced", "years": 3},
                {"name": "Node.js", "level": "intermediate", "years": 2},
                {"name": "C++", "level": "beginner", "years": 0.5},
                {"name": "Qt", "level": "beginner", "years": 0.3}
            ],
            "certifications": ["C++ Fundamentals", "Qt Basics"],
            "preferences": {
                "role_types": ["Qt Developer", "C++ Developer"],
                "industries": ["Automotive", "Technology"],
                "work_arrangement": "Hybrid",
                "locations": ["Remote", "Munich"]
            }
        },
        {
            "jid": "sarah@localhost",
            "name": "Sarah Okonkwo",
            "experience": 0.5,
            "current_role": "CS Student",
            "target_role": "Backend Developer",
            "skills": [
                {"name": "Python", "level": "intermediate", "years": 2},
                {"name": "Java", "level": "intermediate", "years": 1.5},
                {"name": "SQL", "level": "intermediate", "years": 1},
                {"name": "JavaScript", "level": "beginner", "years": 0.5}
            ],
            "education": "Bachelor's in Computer Science (graduating)",
            "preferences": {
                "role_types": ["Backend Developer", "Full Stack"],
                "industries": ["Technology", "Finance"],
                "work_arrangement": "Remote",
                "locations": ["Remote"]
            }
        },
        {
            "jid": "marcus@localhost",
            "name": "Marcus Adebayo",
            "experience": 6,
            "current_role": "Financial Analyst",
            "target_role": "Data Scientist",
            "skills": [
                {"name": "Excel", "level": "expert", "years": 6},
                {"name": "SQL", "level": "advanced", "years": 4},
                {"name": "Python", "level": "intermediate", "years": 2},
                {"name": "Pandas", "level": "intermediate", "years": 1.5},
                {"name": "Tableau", "level": "intermediate", "years": 1}
            ],
            "certifications": ["Python for Data Science", "Machine Learning Fundamentals"],
            "preferences": {
                "role_types": ["Data Scientist", "Data Analyst"],
                "industries": ["Finance", "Technology"],
                "work_arrangement": "Hybrid",
                "locations": ["New York", "Remote"]
            }
        }
    ]
    
    for user_data in default_users:
        user_jid = user_data["jid"]
        
        # Create profile structure
        agent.user_profiles[user_jid] = {
            "user_id": user_jid,
            "basic_info": {
                "name": user_data["name"],
                "years_experience": user_data["experience"],
                "current_role": user_data["current_role"],
                "target_role": user_data["target_role"],
                "education": user_data.get("education", "Bachelor's Degree")
            },
            "skills": {
                "technical": user_data["skills"],
                "soft": ["Communication", "Problem Solving", "Teamwork"]
            },
            "preferences": user_data["preferences"],
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
                "current_context": "active",
                "step": 5,  # Completed onboarding
                "last_interaction": datetime.now().isoformat(),
                "pending_questions": []
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        print(f" Created user: {user_data['name']} ({user_jid})")
    
    print(f" Total default users created: {len(default_users)}")


async def register_new_user(agent):
    """Allow registering a new user via console"""
    print("\n REGISTER NEW USER")
    print("="*50)
    
    name = input("Enter user's full name: ").strip()
    if not name:
        print("Registration cancelled.")
        return
    
    jid = input("Enter user JID (e.g., username@localhost): ").strip()
    if not jid:
        # Generate default JID from name
        jid = f"{name.lower().replace(' ', '.')}@localhost"
        print(f"   Using default JID: {jid}")
    
    if jid in agent.user_profiles:
        print(f"User {jid} already exists!")
        return
    
    try:
        experience = int(input("Enter years of experience: ").strip() or "0")
    except:
        experience = 0
        print("   Using default: 0 years")
    
    current_role = input("Enter current role: ").strip() or "Not specified"
    target_role = input("Enter target role: ").strip() or "Not specified"
    
    # Get skills (comma-separated)
    skills_input = input("Enter skills (comma-separated, e.g., Python, SQL, Java): ").strip()
    skills = []
    if skills_input:
        for skill in skills_input.split(','):
            skill_name = skill.strip()
            if skill_name:
                skills.append({"name": skill_name, "level": "intermediate", "years": 1})
    
    # Create profile
    agent.user_profiles[jid] = {
        "user_id": jid,
        "basic_info": {
            "name": name,
            "years_experience": experience,
            "current_role": current_role,
            "target_role": target_role,
            "education": "Not specified"
        },
        "skills": {
            "technical": skills if skills else [{"name": "Not specified", "level": "beginner", "years": 0}],
            "soft": ["Communication", "Problem Solving"]
        },
        "preferences": {
            "role_types": [target_role] if target_role != "Not specified" else [],
            "industries": [],
            "work_arrangement": "",
            "locations": []
        },
        "learning": {
            "in_progress": [],
            "completed": [],
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
            "current_context": "active",
            "step": 5,
            "last_interaction": datetime.now().isoformat(),
            "pending_questions": []
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    print(f"\n User {name} registered successfully with JID: {jid}")
    
    # Save to file
    from utils.helpers import save_json
    from config.settings import USER_PROFILES_PATH
    save_json(USER_PROFILES_PATH, agent.user_profiles)


async def simulate_user_interactions(agent):
    """
    Simulate user interactions to demonstrate agent capabilities
    This runs alongside the agent to show its behavior
    """
    print("\n" + "="*70)
    print("SIMULATED USER INTERACTIONS - DEMO MODE")
    print("="*70)
    
    await asyncio.sleep(3)  # Give agent time to start
    
    # =========================================================
    # SIMULATION 1: Daniel - Career Changer
    # =========================================================
    print("\n" + "-"*70)
    print("SCENARIO 1: Daniel (Career Changer - JavaScript to C++)")
    print("-"*70)
    
    # Step 1: Daniel requests jobs
    print("\n[1.1] Daniel requests job matches...")
    from spade.message import Message
    
    msg = Message(to=AGENT_JID)
    msg.set_metadata("performative", "inform")
    msg.body = json.dumps({
        "type": "request_jobs",
        "limit": 3
    })
    await agent.send(msg)
    print("Job request sent")
    
    await asyncio.sleep(3)
    
    # Step 2: Daniel clicks on a job
    print("\n[1.2] Daniel clicks on a job (showing interest)...")
    msg = Message(to=AGENT_JID)
    msg.set_metadata("performative", "inform")
    msg.body = json.dumps({
        "type": "job_preference",
        "job_id": 101,
        "action": "clicked"
    })
    await agent.send(msg)
    print("Job click recorded")
    
    await asyncio.sleep(2)
    
    # =========================================================
    # SIMULATION 2: Sarah - Recent Graduate
    # =========================================================
    print("\n" + "-"*70)
    print("SCENARIO 2: Sarah (Recent Graduate)")
    print("-"*70)
    
    # Sarah requests jobs
    print("\n[2.1] Sarah requests job matches...")
    msg = Message(to=AGENT_JID)
    msg.set_metadata("performative", "inform")
    msg.body = json.dumps({
        "type": "request_jobs",
        "limit": 3
    })
    await agent.send(msg)
    print("Job request sent")
    
    await asyncio.sleep(2)
    
    # =========================================================
    # SIMULATION 3: Marcus - Industry Switcher
    # =========================================================
    print("\n" + "-"*70)
    print("📱 SCENARIO 3: Marcus (Industry Switcher - Finance to Data Science)")
    print("-"*70)
    
    # Marcus requests jobs
    print("\n[3.1] Marcus requests job matches...")
    msg = Message(to=AGENT_JID)
    msg.set_metadata("performative", "inform")
    msg.body = json.dumps({
        "type": "request_jobs",
        "limit": 3
    })
    await agent.send(msg)
    print("Job request sent")
    
    await asyncio.sleep(2)
    
    print("\n" + "="*70)
    print("All simulations complete! Agent is still running...")
    print("="*70)
    print("\nCommands you can use:")
    print("  - Type 'users' to see all users")
    print("  - Type 'list_jobs' to see all jobs")
    print("  - Type 'register' to add a new user")
    print("  - Type 'matches <user>' to see matches")
    print("  - Type 'status' for agent status")
    print("  - Type 'help' for all commands")
    print("="*70)


async def console_command_handler(agent):
    """Handle console commands for demo interaction"""
    print("\n Console command handler ready. Type 'help' for commands.\n")
    
    while True:
        try:
            command = await asyncio.get_event_loop().run_in_executor(None, input, ">> ")
            cmd_lower = command.lower().strip()
            
            if cmd_lower == "help":
                print("\nAVAILABLE COMMANDS:")
                print("="*50)
                print("  users          - Show all registered users with details")
                print("  list_users     - Same as 'users'")
                print("  list_jobs      - Show all jobs in database")
                print("  register       - Register a new user")
                print("  matches <user> - Show job matches for a specific user")
                print("  status         - Show agent status")
                print("  help           - Show this help message")
                print("  exit/quit      - Stop the agent")
                print("="*50)
                
            elif cmd_lower in ["users", "list_users"]:
                users = list(agent.user_profiles.keys())
                print(f"\nREGISTERED USERS ({len(users)}):")
                print("="*60)
                
                if not users:
                    print("No users registered yet. Type 'register' to add one.")
                else:
                    for i, user in enumerate(users, 1):
                        profile = agent.user_profiles[user]
                        print(f"\n👤 USER {i}: {user}")
                        print("-"*40)
                        
                        # Basic Info
                        basic = profile.get("basic_info", {})
                        print(f" Name: {basic.get('name', 'N/A')}")
                        print(f" Current: {basic.get('current_role', 'N/A')}")
                        print(f" Target: {basic.get('target_role', 'Not specified')}")
                        print(f" Experience: {basic.get('years_experience', 0)} years")
                        
                        # Skills
                        skills = profile.get("skills", {})
                        tech_skills = skills.get("technical", [])
                        if tech_skills:
                            skill_names = []
                            for s in tech_skills[:5]:
                                if isinstance(s, dict):
                                    skill_names.append(s.get('name', 'Unknown'))
                                else:
                                    skill_names.append(s)
                            print(f"Skills: {', '.join(skill_names)}")
                        
                        # Preferences
                        prefs = profile.get("preferences", {})
                        if prefs.get("role_types"):
                            print(f"Looking for: {', '.join(prefs['role_types'])}")
                        if prefs.get("work_arrangement"):
                            print(f"Work: {prefs.get('work_arrangement')}")
                        
                        print("-"*40)
                
            elif cmd_lower == "register":
                await register_new_user(agent)
                
            elif cmd_lower == "list_jobs":
                jobs = agent.job_database
                print(f"\nJOB DATABASE ({len(jobs)} jobs):")
                print("="*60)
                
                if not jobs:
                    print("No jobs in database.")
                else:
                    for i, job in enumerate(jobs, 1):
                        print(f"\nJOB #{i}: {job.get('title', 'N/A')}")
                        print(f"    {job.get('company', 'N/A')} - {job.get('location', 'N/A')}")
                        print(f"    Industry: {job.get('industry', 'N/A')}")
                        print(f"    Required: {', '.join(job.get('skills_required', []))}")
                    
                    print(f"\nTotal: {len(jobs)} jobs")
                
            elif cmd_lower == "status":
                print(f"\n AGENT STATUS:")
                print("="*40)
                print(f"Users: {len(agent.user_profiles)}")
                print(f"Jobs: {len(agent.job_database)}")
                print(f"Match history: {len(agent.match_history)}")
                print(f"Behaviors: {len(agent.behaviours)}")
                print(f"Agent is running")
                print("="*40)
                
            elif cmd_lower.startswith("matches"):
                parts = command.split()
                if len(parts) < 2:
                    print("\nPlease specify a user. Usage: matches <user_jid>")
                    print("Example: matches daniel@localhost")
                    print("\nAvailable users:")
                    for u in agent.user_profiles.keys():
                        name = agent.user_profiles[u]["basic_info"]["name"]
                        print(f"  - {u} ({name})")
                else:
                    user_jid = parts[1]
                    if user_jid not in agent.user_profiles:
                        print(f"\n User {user_jid} not found.")
                        print("\nAvailable users:")
                        for u in agent.user_profiles.keys():
                            name = agent.user_profiles[u]["basic_info"]["name"]
                            print(f"  - {u} ({name})")
                    else:
                        profile = agent.user_profiles[user_jid]
                        print(f"\nMATCHES FOR {profile['basic_info']['name']} ({user_jid})")
                        print("="*70)
                        
                        matches = agent.find_matching_jobs(user_jid, limit=10)
                        
                        if not matches:
                            print("No matches found for this user.")
                        else:
                            for i, match in enumerate(matches, 1):
                                job = match['job']
                                score = match['score']
                                explanation = match['explanation']
                                
                                # Score indicator
                                if score >= 90:
                                    indicator = "EXCELLENT"
                                elif score >= 80:
                                    indicator = "STRONG"
                                elif score >= 70:
                                    indicator = "🟡 GOOD"
                                else:
                                    indicator = "🔵 POTENTIAL"
                                
                                print(f"\n{i}. {indicator} ({score}%)")
                                print(f"   {job.get('title')} at {job.get('company')}")
                                print(f"   {explanation}")
                            
                            print(f"\nTotal: {len(matches)} matches")
                
            elif cmd_lower in ["exit", "quit"]:
                print("\n Shutting down...")
                break
                
            else:
                print(f"\n Unknown command: {command}")
                print("Type 'help' for available commands.\n")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Main entry point"""
    print("\n" + "="*70)
    print(" SKILLSCOUT - Intelligent Job Matching Agent")
    print("="*70)
    print(f"Agent JID: {AGENT_JID}")
    print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Create and start agent
    agent = SkillScoutAgent(AGENT_JID, AGENT_PASSWORD)
    
    try:
        # Start agent
        await agent.start(auto_register=True)
        print(" Agent started successfully!")
        
        # Create default users from scenarios
        await create_default_users(agent)
        
        # === SYSTEM CHECK ===
        print("\nSYSTEM CHECK:")
        print(f"   Job database type: {type(agent.job_database)}")
        print(f"   Job database length: {len(agent.job_database)}")
        if agent.job_database:
            print(f"   First job: {agent.job_database[0].get('title')}")
        print(f"   User profiles: {len(agent.user_profiles)}")
        print("="*50)
        # ====================
        
        # Run simulations and command handler concurrently
        sim_task = asyncio.create_task(simulate_user_interactions(agent))
        cmd_task = asyncio.create_task(console_command_handler(agent))
        
        # Wait for either task to complete (command handler will exit on 'quit')
        await cmd_task
        
        # Cancel simulation if still running
        sim_task.cancel()
        
    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal...")
    finally:
        print("\nStopping agent...")
        await agent.stop()
        print("Agent stopped. Goodbye!")
        print("="*70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")