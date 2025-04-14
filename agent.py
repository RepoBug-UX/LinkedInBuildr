from nearai.agents.environment import Environment
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

STUDENT_ACTIVITY_TYPES = [
    "hackathon",
    "personal_project",
    "internship",
    "conference",
    "workshop",
    "course_completion",
    "competition"
]

REQUIRED_INFO = {
    "hackathon": {
        "essential": ["project_name", "tech_stack", "team_size", "achievement"],
        "optional": ["duration", "demo_link", "github_link", "problem_solved"]
    },
    "personal_project": {
        "essential": ["project_name", "tech_stack", "problem_statement"],
        "optional": ["github_link", "demo_link", "duration"]
    },
    "internship": {
        "essential": ["company", "role", "technologies", "duration"],
        "optional": ["team", "projects", "key_learnings"]
    },
    "conference": {
        "essential": ["conference_name", "date_or_duration", "key_learnings"],
        "optional": ["key_sessions", "networking_highlights"]
    },
    "workshop": {
        "essential": ["workshop_name", "skills_acquired"],
        "optional": ["practical_applications", "duration"]
    },
    "competition": {
        "essential": ["competition_name", "challenge_description", "tech_stack", "result"],
        "optional": ["team_size", "duration", "github_link"]
    }
}

TONE_STYLES = {
    "formal": {
        "technical_depth": "high",
        "format": "structured",
        "enthusiasm": "moderate"
    },
    "balanced": {
        "technical_depth": "moderate",
        "format": "conversational",
        "enthusiasm": "moderate"
    },
    "narrative": {
        "technical_depth": "moderate",
        "format": "story",
        "enthusiasm": "high"
    }
}

TECH_KEYWORDS = {
    "languages": ["Python", "JavaScript", "TypeScript", "Java", "C++", "Rust", "Go", "Ruby", "Swift"],
    "frameworks": ["React", "Angular", "Vue", "Django", "Flask", "Spring", "Express", "Next.js", "FastAPI"],
    "cloud": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Serverless"],
    "ai_ml": ["TensorFlow", "PyTorch", "OpenAI", "Machine Learning", "Deep Learning", "NLP", "Computer Vision"],
    "databases": ["PostgreSQL", "MongoDB", "MySQL", "Redis", "Elasticsearch"],
    "tools": ["Git", "GitHub", "GitLab", "CI/CD", "Jenkins", "Docker"]
}

def extract_technologies(text: str) -> List[str]:
    """Extract mentioned technologies from text"""
    found_tech = set()
    text_lower = text.lower()
    
    for category, terms in TECH_KEYWORDS.items():
        for term in terms:
            if term.lower() in text_lower:
                found_tech.add(term)
    
    return list(found_tech)

def generate_smart_hashtags(text: str, activity_type: str) -> List[str]:
    """Generate relevant hashtags based on content and activity type"""
    hashtags = set()
    
    # Add activity-specific hashtags
    activity_tags = {
        "hackathon": ["hackathon", "coding", "hackerlife"],
        "personal_project": ["sideproject", "coding", "buildingInPublic"],
        "internship": ["internship", "careerstart", "techcareer"],
        "conference": ["techconference", "learning", "networking"],
        "workshop": ["workshop", "skillbuilding", "learning"],
        "course_completion": ["learning", "upskilling", "education"],
        "competition": ["coding", "competition", "challenge"]
    }
    
    # Add 2 activity-specific hashtags
    if activity_type in activity_tags:
        hashtags.update(activity_tags[activity_type][:2])
    
    # Add technology hashtags
    tech_mentions = extract_technologies(text)
    for tech in tech_mentions[:3]:  # Limit to 3 tech hashtags
        clean_tech = tech.replace(" ", "").replace(".", "").replace("-", "")
        hashtags.add(clean_tech)
    
    # Add general CS student hashtags
    general_tags = ["computerscience", "tech", "coding"]
    hashtags.add(general_tags[0])
    
    return list(hashtags)[:5]  # Limit to 5 total hashtags

def detect_activity_type(text: str) -> str:
    """Automatically detect activity type from user input"""
    text_lower = text.lower()
    
    keywords = {
        "hackathon": ["hackathon", "hack", "hacka"],
        "personal_project": ["project", "built", "created", "developed", "launched"],
        "internship": ["intern", "internship", "company"],
        "conference": ["conference", "event", "convention", "attended"],
        "workshop": ["workshop", "session", "training"],
        "course_completion": ["course", "certification", "completed", "learned"],
        "competition": ["competition", "contest", "challenge", "competed"]
    }
    
    for activity_type, words in keywords.items():
        if any(word in text_lower for word in words):
            return activity_type
    
    return "personal_project"  # default if no clear match

def create_activity_template(activity_type: str) -> Dict[str, any]:
    """Create template based on activity type"""
    base_template = {
        "title": "",
        "date_or_duration": "",
        "organization": "",
        "role_or_participation": "",
        "technical_details": [],
        "achievements": [],
        "key_learnings": [],
        "acknowledgments": "",
        "next_steps": "",
        "hashtags": []
    }
    
    specific_templates = {
        "hackathon": {
            **base_template,
            "project_name": "",
            "team_size": "",
            "problem_solved": "",
            "tech_stack": [],
            "demo_link": ""
        },
        "personal_project": {
            **base_template,
            "project_name": "",
            "problem_statement": "",
            "tech_stack": [],
            "github_link": "",
            "demo_link": ""
        },
        "internship": {
            **base_template,
            "company": "",
            "team": "",
            "projects": [],
            "technologies": []
        },
        "conference": {
            **base_template,
            "conference_name": "",
            "key_sessions": [],
            "networking_highlights": []
        },
        "workshop": {
            **base_template,
            "workshop_name": "",
            "skills_acquired": [],
            "practical_applications": []
        },
        "course_completion": {
            **base_template,
            "course_name": "",
            "provider": "",
            "skills_acquired": [],
            "projects_completed": []
        },
        "competition": {
            **base_template,
            "competition_name": "",
            "challenge_description": "",
            "solution_approach": "",
            "result": ""
        }
    }
    
    return specific_templates.get(activity_type, base_template)

def check_missing_info(activity_type: str, post_data: Dict[str, any]) -> Dict[str, List[str]]:
    """Check what essential and optional information is missing"""
    if activity_type not in REQUIRED_INFO:
        return {"essential": [], "optional": []}
        
    requirements = REQUIRED_INFO[activity_type]
    missing = {
        "essential": [field for field in requirements["essential"] if not post_data.get(field)],
        "optional": [field for field in requirements["optional"] if not post_data.get(field)]
    }
    return missing

def generate_info_request(missing_info: Dict[str, List[str]], activity_type: str) -> str:
    """Generate a natural request for missing information"""
    requests = []
    
    if missing_info["essential"]:
        requests.append("To create a comprehensive post, I'll need a few key details:")
        for field in missing_info["essential"]:
            if field == "tech_stack":
                requests.append("- What technologies did you use?")
            elif field == "team_size":
                requests.append("- How many people were on your team?")
            elif field == "achievement":
                requests.append("- Did you achieve any notable results or wins?")
            elif field == "project_name":
                requests.append("- What did you name your project?")
            elif field == "problem_statement":
                requests.append("- What problem were you trying to solve?")
            elif field == "company":
                requests.append("- Which company did you intern with?")
            elif field == "role":
                requests.append("- What was your role or main responsibilities?")
            elif field == "duration":
                requests.append("- How long was the " + activity_type + "?")
            else:
                requests.append(f"- Could you share details about the {field.replace('_', ' ')}?")
    
    if missing_info["optional"]:
        optional_requests = []
        for field in missing_info["optional"]:
            if field == "github_link":
                optional_requests.append("- Do you have a GitHub repository to share?")
            elif field == "demo_link":
                optional_requests.append("- Is there a demo available?")
            elif field == "key_learnings":
                optional_requests.append("- What were your main takeaways?")
            else:
                optional_requests.append(f"- Any details about {field.replace('_', ' ')}?")
        
        if optional_requests:
            requests.append("\nAdditional helpful information (optional):")
            requests.extend(optional_requests)
    
    return "\n".join(requests)

def format_post(post_data: Dict[str, any], activity_type: str, tone_style: str = "balanced") -> str:
    """Format the post with specified tone and style"""
    # First check if we have all essential information
    missing = check_missing_info(activity_type, post_data)
    if missing["essential"]:
        return generate_info_request(missing, activity_type)
    
    style = TONE_STYLES[tone_style]
    formatted_sections = []
    
    # Opening hook based on activity type and tone
    if activity_type == "hackathon":
        if post_data.get("achievements"):
            formatted_sections.append(f"{post_data.get('achievements')[0]}")
        else:
            formatted_sections.append(f"Just completed an intensive hackathon experience at {post_data.get('organization')}.")
    
    elif activity_type == "personal_project":
        formatted_sections.append(f"Excited to share my latest project: {post_data.get('project_name')}")
    
    elif activity_type == "internship":
        if "title" in post_data and post_data["title"]:
            formatted_sections.append(f"{post_data['title']}")
    
    elif activity_type in ["conference", "workshop"]:
        formatted_sections.append(f"Recently participated in {post_data.get('title')} at {post_data.get('organization')}")

    # Main content with technical depth based on tone
    main_content = []
    
    if style["technical_depth"] == "high":
        if post_data.get("technical_details"):
            main_content.append("\nTechnical Implementation:")
            main_content.extend([f"- {detail}" for detail in post_data["technical_details"]])
    else:
        if post_data.get("technical_details"):
            main_content.append("\nKey Technical Highlights:")
            main_content.extend([f"- {detail}" for detail in post_data["technical_details"][:3]])
    
    if post_data.get("key_learnings"):
        main_content.append("\nKey Takeaways:")
        main_content.extend([f"- {learning}" for learning in post_data["key_learnings"]])
    
    if post_data.get("achievements") and len(post_data["achievements"]) > 1:
        main_content.append("\nAchievements:")
        main_content.extend([f"- {achievement}" for achievement in post_data["achievements"][1:]])
    
    formatted_sections.extend(main_content)
    
    # Add acknowledgments based on tone
    if post_data.get("acknowledgments"):
        formatted_sections.append(f"\n{post_data['acknowledgments']}")
    
    # Add next steps or future outlook
    if post_data.get("next_steps"):
        formatted_sections.append(f"\n{post_data['next_steps']}")
    
    # Add relevant links
    links = []
    if post_data.get("github_link"):
        links.append(f"GitHub: {post_data['github_link']}")
    if post_data.get("demo_link"):
        links.append(f"Demo: {post_data['demo_link']}")
    
    if links:
        formatted_sections.append("\nLinks: " + " | ".join(links))
    
    # Add hashtags
    if post_data.get("hashtags"):
        formatted_sections.append("\n" + " ".join([f"#{tag}" for tag in post_data["hashtags"]]))
    
    return "\n\n".join([s for s in formatted_sections if s])

def apply_quick_edit(post: str, edit_type: str) -> str:
    """Apply quick edits to the post"""
    if edit_type == "shorter":
        # Remove some detail sections while keeping core message
        lines = post.split("\n")
        if len(lines) > 10:
            # Keep first 2 paragraphs, achievements if any, and links/hashtags
            important_parts = []
            in_achievements = False
            for line in lines:
                if line.startswith("🔗") or line.startswith("#"):
                    important_parts.append(line)
                elif "Achievement" in line:
                    in_achievements = True
                    important_parts.append(line)
                elif in_achievements and line.startswith("•"):
                    important_parts.append(line)
                elif len(important_parts) < 5:
                    important_parts.append(line)
            return "\n".join(important_parts)
    
    elif edit_type == "longer":
        # Add more context and detail markers
        if "Key Takeaways:" not in post:
            post += "\n\nKey Takeaways:\n• [Add your key learning point]\n• [Add another learning point]"
    
    elif edit_type == "more_technical":
        # Add technical detail markers
        if "Technical Implementation:" not in post:
            post = post.replace("Key Technical Highlights:", "Technical Implementation:")
            post += "\n\nTechnical Details:\n• [Add specific technical implementation detail]\n• [Add architecture decision]"
    
    elif edit_type == "less_technical":
        # Simplify technical language
        post = post.replace("Technical Implementation:", "Key Highlights:")
        post = re.sub(r'(?<=•)[^•]+?(?=(\n|$))', lambda m: simplify_technical_text(m.group()), post)
    
    return post

def simplify_technical_text(text: str) -> str:
    """Simplify technical language in the text"""
    # Add logic to simplify technical terms
    return text

def run(env: Environment):
    system_prompt = """You are a LinkedIn post creator specialized in helping a computer science student showcase their 
    technical activities and achievements. You excel at:
    1. Asking clear, focused questions to gather key information
    2. Understanding technical context to guide the conversation
    3. Maintaining a clean, professional tone
    4. Crafting compelling posts that highlight technical achievements
    5. Keeping the focus on career-relevant details
    
    When gathering information:
    - Start with specific, targeted questions about key details
    - Focus on information relevant for a LinkedIn audience
    - Ask at most 2-3 questions at a time
    - Keep technical questions high-level unless specifically relevant
    
    Essential information to gather:
    - Project/Activity name (ask directly)
    - Core technical details (high-level stack and features)
    - Main purpose/problem solved (ask specifically)
    
    Follow-up information (ask after essentials):
    - Project status (deployed/in development)
    - Key achievements or metrics (if any)
    - Links to showcase work (GitHub, demo, etc.)
    
    DO NOT:
    - Ask for overly technical implementation details
    - Request multiple categories of information at once
    - Focus on future plans unless specifically relevant
    - Ask about authentication or security details unless crucial
    
    Information gathering process:
    1. Get essential details first (name, purpose, tech stack)
    2. Ask for 1-2 showcase elements (deployment, links, achievements)
    3. Confirm readiness for post generation
    4. Draft post and allow for refinements
    
    Guide users efficiently through the post creation process, maintaining a professional tone while gathering career-relevant information.
    """
    
    prompt = {"role": "system", "content": system_prompt}
    
    # Initial message to help user get started
    if not env.list_messages():
        welcome_message = """Welcome! I'll help you create a professional LinkedIn post about your CS journey and activities.

What would you like to post about? Once you share your activity, I'll ask specific questions to help craft a compelling post."""
        
        env.add_reply(welcome_message)
        env.request_user_input()
        return

    # Process user input and generate response
    result = env.completion([prompt] + env.list_messages())
    env.add_reply(result)
    env.request_user_input()

run(env)

