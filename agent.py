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

PROFILE_SECTIONS = {
    "headline": {
        "essential": ["role", "specialization", "key_technology"],
        "optional": ["industry", "achievement"]
    },
    "about": {
        "essential": ["professional_summary", "key_skills", "interests"],
        "optional": ["achievements", "career_goals", "values"]
    },
    "experience": {
        "essential": ["company", "role", "duration", "responsibilities"],
        "optional": ["achievements", "tech_stack", "impact_metrics"]
    },
    "education": {
        "essential": ["institution", "degree", "field", "graduation_date"],
        "optional": ["gpa", "relevant_coursework", "honors"]
    },
    "skills": {
        "categories": ["technical", "soft", "domain"],
        "max_per_category": 15,
        "endorsement_priority": 5
    }
}

HEADLINE_TEMPLATES = [
    "{role} specializing in {specialization} | {key_technology} Developer",
    "{role} with focus on {specialization} | {industry} Solutions",
    "{role} passionate about {specialization} | {achievement}",
    "Student {role} building with {key_technology} | {specialization} Enthusiast"
]

ABOUT_SECTION_STRUCTURE = {
    "opening": {
        "student": "Computer Science student at {institution} passionate about {specialization}",
        "recent_grad": "Recent Computer Science graduate from {institution} specializing in {specialization}",
        "intern": "Computer Science intern with experience in {specialization}"
    },
    "body": [
        "technical_focus",
        "achievements",
        "current_projects",
        "learning_goals"
    ],
    "closing": [
        "seeking_opportunities",
        "collaboration_interest",
        "contact_info"
    ]
}

CONVERSATION_TEMPLATES = {
    "welcome": {
        "message": """Welcome! I'm here to help you create a standout LinkedIn presence. I can assist with:

1. Creating/improving your LinkedIn profile 📝
   - Craft an attention-grabbing headline
   - Write a compelling about section
   - Showcase your technical experience
   - Highlight your education and skills

2. Writing engaging posts about your CS activities 📱
   - Hackathon achievements
   - Project showcases
   - Technical learnings
   - Professional milestones

3. Building your technical network strategically 🤝
   - Connect with professionals in your tech stack
   - Join relevant technical communities
   - Engage meaningfully in your domain
   - Grow your professional network

Which of these areas would you like to focus on? Feel free to share your goals, and I'll guide you through the process!""",
        "next_steps": {
            "profile": "profile_start",
            "post": "post_start",
            "network": "network_start"
        }
    },
    "profile_start": {
        "message": """Great! Let's create a compelling LinkedIn profile. We'll go through each section step by step:

First, let's craft your professional headline. I'll need some key information:

1. Your current role (e.g., CS Student, Software Engineering Intern)
2. Your technical specialization (e.g., Full-Stack, ML/AI, Cloud)
3. Key technologies you work with (e.g., Python, React, AWS)

Please share these details, and I'll help create a headline that catches recruiters' attention!""",
        "required_fields": ["role", "specialization", "key_technology"]
    },
    "post_start": {
        "message": """Excellent! Let's create an engaging post about your CS activities. 

What would you like to post about? Here are some popular options:
1. 🚀 Project showcase
2. 💡 Hackathon experience
3. 📚 Learning achievement
4. 💼 Internship update
5. 🏆 Competition results

Choose a topic, and I'll guide you through crafting a compelling post!"""
    },
    "section_transitions": {
        "headline_to_about": """Great! Your headline looks professional. Now, let's work on your 'About' section.

This is your chance to tell your story. Could you share:
1. Your professional journey and interests
2. Key technical skills and achievements
3. What you're currently working on or learning
4. Your career goals

Don't worry about the format - I'll help structure this information!""",
        "about_to_experience": """Perfect! Your 'About' section is looking good. Let's move on to your experience.

For each relevant experience (internships, projects, etc.), please share:
1. Role and organization
2. Duration
3. Key responsibilities
4. Technical stack used
5. Notable achievements

Start with your most recent experience."""
    },
    "improvement_suggestions": {
        "headline": {
            "too_short": "Your headline could be more descriptive. Consider adding your specialization or key technology.",
            "no_tech": "Including a key technology could make your headline more discoverable.",
            "too_generic": "Try to make your headline more specific to your technical focus."
        },
        "about": {
            "too_short": "Your about section could benefit from more detail about your technical journey.",
            "no_achievements": "Consider adding specific technical achievements or projects.",
            "no_goals": "Including your career goals could make your profile more engaging."
        },
        "experience": {
            "no_metrics": "Try adding quantifiable achievements or impact metrics.",
            "no_tech_stack": "Including the technical stack for each role would strengthen your profile.",
            "vague_responsibilities": "Be more specific about your technical contributions."
        }
    }
}

NETWORK_TARGETS = {
    "technical": {
        "roles": ["Software Engineer", "Tech Lead", "Engineering Manager", "CTO"],
        "levels": ["Senior", "Lead", "Principal", "Junior"],
        "specializations": ["Frontend", "Backend", "Full-Stack", "DevOps", "ML"]
    },
    "recruitment": {
        "roles": ["Technical Recruiter", "Talent Acquisition", "HR Tech"],
        "companies": ["FAANG", "Startups", "Tech Companies"]
    },
    "community": {
        "groups": ["Open Source", "Tech Communities", "Programming Languages", "Framework-specific"],
        "events": ["Meetups", "Conferences", "Hackathons", "Tech Talks"]
    }
}

TECHNICAL_CONTEXT = {
    "project_types": {
        "optimization": {
            "key_metrics": ["latency", "memory", "cpu_usage"],
            "impact_phrases": [
                "Reduced latency by {X}%",
                "Improved memory usage by {X}MB",
                "Decreased CPU load from {X}% to {Y}%"
            ]
        },
        "scalability": {
            "key_metrics": ["requests_per_second", "concurrent_users", "data_volume"],
            "impact_phrases": [
                "Scaled from {X} to {Y} users",
                "Handled {X} concurrent requests",
                "Processed {X}GB of data daily"
            ]
        },
        "user_experience": {
            "key_metrics": ["load_time", "interaction_time", "error_rate"],
            "impact_phrases": [
                "Decreased page load time by {X}s",
                "Reduced user interaction time by {X}%",
                "Cut error rate from {X}% to {Y}%"
            ]
        },
        "security": {
            "key_metrics": ["vulnerability_count", "response_time", "coverage"],
            "impact_phrases": [
                "Identified and fixed {X} vulnerabilities",
                "Improved security response time by {X}%",
                "Increased security coverage to {X}%"
            ]
        }
    }
}

PROJECT_IMPACT = {
    "technical": {
        "performance": {
            "metrics": ["response_time", "resource_usage", "throughput"],
            "comparisons": ["before_after", "industry_standard", "competitor_analysis"],
            "validation": ["benchmarks", "monitoring_data", "user_metrics"]
        },
        "scale": {
            "metrics": ["user_load", "data_volume", "request_rate"],
            "comparisons": ["previous_capacity", "target_goals", "industry_benchmarks"],
            "validation": ["load_tests", "production_data", "stress_tests"]
        },
        "reliability": {
            "metrics": ["uptime", "error_rate", "recovery_time"],
            "comparisons": ["sla_requirements", "previous_performance", "industry_standards"],
            "validation": ["monitoring_logs", "incident_reports", "user_feedback"]
        }
    },
    "business": {
        "efficiency": {
            "metrics": ["time_saved", "cost_reduced", "productivity_gained"],
            "comparisons": ["previous_process", "manual_method", "competitor_solution"],
            "validation": ["user_feedback", "cost_analysis", "productivity_metrics"]
        },
        "impact": {
            "metrics": ["user_adoption", "revenue_impact", "market_reach"],
            "comparisons": ["previous_quarter", "market_average", "projected_goals"],
            "validation": ["analytics_data", "financial_reports", "user_surveys"]
        }
    }
}

SKILL_PROGRESSION = {
    "levels": {
        "learning": {
            "indicators": ["completing_tutorials", "basic_projects", "understanding_concepts"],
            "evidence": ["course_completion", "simple_implementations", "documented_learning"],
            "next_steps": ["apply_in_project", "solve_problems", "build_portfolio"]
        },
        "applying": {
            "indicators": ["project_completion", "bug_fixes", "feature_implementation"],
            "evidence": ["github_repos", "deployed_projects", "code_reviews"],
            "next_steps": ["optimize_code", "improve_architecture", "tackle_complexity"]
        },
        "optimizing": {
            "indicators": ["performance_improvements", "architecture_decisions", "system_design"],
            "evidence": ["benchmarks", "technical_docs", "architecture_diagrams"],
            "next_steps": ["lead_projects", "mentor_others", "contribute_opensource"]
        },
        "leading": {
            "indicators": ["team_leadership", "architecture_ownership", "technical_direction"],
            "evidence": ["team_achievements", "system_improvements", "technical_blogs"],
            "next_steps": ["expand_impact", "drive_innovation", "build_community"]
        }
    },
    "domains": {
        "technical": ["coding", "architecture", "tools", "testing"],
        "collaboration": ["teamwork", "communication", "mentoring"],
        "problem_solving": ["analysis", "debugging", "optimization"]
    }
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

def generate_headline(profile_data: Dict[str, any]) -> str:
    """Generate a compelling LinkedIn headline"""
    if not all(field in profile_data for field in PROFILE_SECTIONS["headline"]["essential"]):
        return ""
    
    template = HEADLINE_TEMPLATES[0]  # Default to first template
    # Choose template based on whether they're a student or professional
    if "student" in profile_data.get("role", "").lower():
        template = HEADLINE_TEMPLATES[3]
    
    return template.format(
        role=profile_data["role"],
        specialization=profile_data["specialization"],
        key_technology=profile_data["key_technology"],
        industry=profile_data.get("industry", "Technology"),
        achievement=profile_data.get("achievement", "")
    )

def format_about_section(profile_data: Dict[str, any]) -> str:
    """Format the about section of the profile"""
    about_structure = ABOUT_SECTION_STRUCTURE
    sections = []
    
    # Opening
    template = about_structure["opening"]["student"]
    if "recent_grad" in profile_data.get("status", "").lower():
        template = about_structure["opening"]["recent_grad"]
    elif "intern" in profile_data.get("role", "").lower():
        template = about_structure["opening"]["intern"]
    
    sections.append(template.format(
        institution=profile_data.get("institution", ""),
        specialization=profile_data.get("specialization", "")
    ))
    
    # Body
    if profile_data.get("technical_focus"):
        sections.append(f"\n🔧 Technical Focus:\n{profile_data['technical_focus']}")
    
    if profile_data.get("achievements"):
        sections.append(f"\n🏆 Achievements:\n{profile_data['achievements']}")
    
    if profile_data.get("current_projects"):
        sections.append(f"\n🚀 Current Projects:\n{profile_data['current_projects']}")
    
    if profile_data.get("learning_goals"):
        sections.append(f"\n📚 Learning Goals:\n{profile_data['learning_goals']}")
    
    # Closing
    if profile_data.get("seeking_opportunities"):
        sections.append(f"\n🔍 {profile_data['seeking_opportunities']}")
    
    return "\n".join(sections)

def format_experience_section(experiences: List[Dict[str, any]]) -> List[str]:
    """Format experience entries"""
    formatted_experiences = []
    
    for exp in experiences:
        if not all(field in exp for field in PROFILE_SECTIONS["experience"]["essential"]):
            continue
            
        entry = [
            f"🏢 {exp['role']} at {exp['company']}",
            f"📅 {exp['duration']}",
            "\nKey Responsibilities:",
        ]
        
        for resp in exp['responsibilities']:
            entry.append(f"• {resp}")
        
        if exp.get('achievements'):
            entry.append("\nKey Achievements:")
            for achievement in exp['achievements']:
                entry.append(f"• {achievement}")
        
        if exp.get('tech_stack'):
            entry.append(f"\n🛠 Tech Stack: {', '.join(exp['tech_stack'])}")
        
        formatted_experiences.append("\n".join(entry))
    
    return formatted_experiences

def format_education_section(education: Dict[str, any]) -> str:
    """Format education section"""
    if not all(field in education for field in PROFILE_SECTIONS["education"]["essential"]):
        return ""
    
    sections = [
        f"🎓 {education['degree']} in {education['field']}",
        f"📍 {education['institution']}",
        f"📅 Graduating: {education['graduation_date']}"
    ]
    
    if education.get('gpa'):
        sections.append(f"📊 GPA: {education['gpa']}")
    
    if education.get('relevant_coursework'):
        sections.append("\nRelevant Coursework:")
        sections.append("• " + "\n• ".join(education['relevant_coursework']))
    
    if education.get('honors'):
        sections.append("\nHonors & Awards:")
        sections.append("• " + "\n• ".join(education['honors']))
    
    return "\n".join(sections)

def organize_skills(skills: Dict[str, List[str]]) -> str:
    """Organize and format skills section"""
    formatted_skills = []
    
    for category in PROFILE_SECTIONS["skills"]["categories"]:
        if category in skills and skills[category]:
            # Limit skills per category
            category_skills = skills[category][:PROFILE_SECTIONS["skills"]["max_per_category"]]
            formatted_skills.append(f"\n{category.title()} Skills:")
            formatted_skills.append("• " + "\n• ".join(category_skills))
    
    return "\n".join(formatted_skills)

def validate_profile_data(profile_data: Dict[str, any]) -> Dict[str, List[str]]:
    """Validate profile data and return missing required fields"""
    missing = {}
    
    for section, requirements in PROFILE_SECTIONS.items():
        if section == "skills":
            continue  # Skills have a different structure
            
        missing[section] = []
        if "essential" in requirements:
            for field in requirements["essential"]:
                if field not in profile_data.get(section, {}):
                    missing[section].append(field)
    
    return {k: v for k, v in missing.items() if v}

def generate_profile_sections(profile_data: Dict[str, any]) -> Dict[str, str]:
    """Generate all sections of the LinkedIn profile"""
    profile = {}
    
    # Generate headline
    profile["headline"] = generate_headline(profile_data)
    
    # Generate about section
    profile["about"] = format_about_section(profile_data)
    
    # Generate experience section
    if "experiences" in profile_data:
        profile["experience"] = format_experience_section(profile_data["experiences"])
    
    # Generate education section
    if "education" in profile_data:
        profile["education"] = format_education_section(profile_data["education"])
    
    # Generate skills section
    if "skills" in profile_data:
        profile["skills"] = organize_skills(profile_data["skills"])
    
    return profile

def suggest_profile_improvements(profile: Dict[str, str]) -> List[str]:
    """Suggest improvements for the profile"""
    suggestions = []
    
    # Headline suggestions
    if len(profile.get("headline", "")) < 50:
        suggestions.append("Consider adding more detail to your headline to improve visibility")
    
    # About section suggestions
    about = profile.get("about", "")
    if len(about) < 200:
        suggestions.append("Your about section could benefit from more content - aim for 200-2000 characters")
    if "achievements" not in about.lower():
        suggestions.append("Consider adding specific achievements to your about section")
    
    # Experience suggestions
    experiences = profile.get("experience", [])
    if experiences:
        if not any("achievement" in exp.lower() for exp in experiences):
            suggestions.append("Add quantifiable achievements to your experience entries")
        if not any("tech stack" in exp.lower() for exp in experiences):
            suggestions.append("Include technical stack details in your experience descriptions")
    
    # Skills suggestions
    skills = profile.get("skills", "")
    if len(skills.split("\n")) < 10:
        suggestions.append("Add more relevant skills to increase profile visibility")
    
    return suggestions

def get_next_prompt(current_state: str, user_input: str = None) -> str:
    """Get the next conversation prompt based on current state and user input"""
    templates = CONVERSATION_TEMPLATES
    
    if current_state in templates:
        if user_input and "next_steps" in templates[current_state]:
            next_state = templates[current_state]["next_steps"].get(user_input)
            if next_state and next_state in templates:
                return templates[next_state]["message"]
        return templates[current_state]["message"]
    
    return None

def generate_improvement_suggestions(section: str, content: str) -> List[str]:
    """Generate specific improvement suggestions for profile sections"""
    suggestions = []
    templates = CONVERSATION_TEMPLATES["improvement_suggestions"]
    
    if section in templates:
        section_templates = templates[section]
        
        if section == "headline":
            if len(content) < 50:
                suggestions.append(section_templates["too_short"])
            if not any(tech in content for tech in TECH_KEYWORDS["languages"] + TECH_KEYWORDS["frameworks"]):
                suggestions.append(section_templates["no_tech"])
                
        elif section == "about":
            if len(content) < 200:
                suggestions.append(section_templates["too_short"])
            if "achieve" not in content.lower():
                suggestions.append(section_templates["no_achievements"])
                
        elif section == "experience":
            if not any(metric in content.lower() for metric in ["%", "increased", "improved", "reduced"]):
                suggestions.append(section_templates["no_metrics"])
            if not any(tech in content for tech in TECH_KEYWORDS["languages"] + TECH_KEYWORDS["frameworks"]):
                suggestions.append(section_templates["no_tech_stack"])
    
    return suggestions

def generate_connection_message(target_info: Dict[str, str], user_context: Dict[str, str]) -> str:
    """Create personalized connection request messages"""
    if target_info.get("role", "").lower() in ["recruiter", "talent"]:
        return f"Hi {target_info.get('name', '')}, I'm a CS student focusing on {user_context.get('specialization', 'software development')}. I'm interested in {target_info.get('company', 'your company')}'s opportunities and would love to connect."
    elif any(level in target_info.get("role", "").lower() for level in ["senior", "lead", "principal"]):
        return f"Hi {target_info.get('name', '')}, I'm a CS student building projects with {user_context.get('tech_stack', ['Python', 'JavaScript'])[0]}. Your work at {target_info.get('company', 'your company')} is inspiring, and I'd appreciate connecting to learn from your journey."
    else:
        return f"Hi {target_info.get('name', '')}, I'm a CS student interested in {user_context.get('interests', ['software development'])[0]}. I noticed you work with similar technologies at {target_info.get('company', 'your company')}. Would love to connect and learn from your experience!"

def suggest_engagement_plan(technical_interests: List[str], career_goals: str) -> Dict:
    """Create weekly engagement strategy"""
    return {
        "weekly_actions": {
            "connections": "Reach out to 5-7 professionals in your target companies/roles",
            "content": "Engage with 3-5 technical posts related to your interests",
            "groups": "Participate in 2-3 technical community discussions"
        },
        "focus_areas": technical_interests[:3],
        "target_roles": ["Software Engineers", "Tech Leads", "Technical Recruiters"],
        "engagement_tips": [
            "Comment on technical solutions and approaches",
            "Share your project updates and learnings",
            "Ask thoughtful questions about industry practices",
            "Engage with posts from target companies"
        ]
    }

def validate_achievement(achievement: Dict) -> Dict:
    """Enhance achievements with specific metrics and validation"""
    validated = {
        "original": achievement.get("description", ""),
        "metrics": extract_metrics(achievement),
        "suggested_improvements": [],
        "technical_depth": calculate_technical_depth(achievement)
    }
    
    if not validated["metrics"]:
        validated["suggested_improvements"].append({
            "type": "add_metrics",
            "suggestions": suggest_relevant_metrics(achievement)
        })
    
    if validated["technical_depth"] < 0.7:  # threshold for technical detail
        validated["suggested_improvements"].append({
            "type": "increase_technical_detail",
            "suggestions": suggest_technical_details(achievement)
        })
    
    return validated

def extract_metrics(achievement: Dict) -> List[Dict]:
    """Extract quantifiable metrics from achievement description"""
    metrics = []
    description = achievement.get("description", "")
    
    # Look for numerical metrics
    for project_type in TECHNICAL_CONTEXT["project_types"]:
        for metric in TECHNICAL_CONTEXT["project_types"][project_type]["key_metrics"]:
            # Use regex to find metrics in description
            pattern = f"(?i){metric}.*?([0-9]+(?:\\.[0-9]+)?%?)"
            matches = re.findall(pattern, description)
            if matches:
                metrics.append({
                    "type": metric,
                    "value": matches[0],
                    "context": project_type
                })
    
    return metrics

def suggest_relevant_metrics(achievement: Dict) -> List[str]:
    """Suggest relevant metrics based on achievement context"""
    suggestions = []
    description = achievement.get("description", "").lower()
    
    for project_type, details in TECHNICAL_CONTEXT["project_types"].items():
        # If achievement seems related to this project type
        if any(keyword in description for keyword in project_type.split("_")):
            # Suggest using relevant metrics
            for metric in details["key_metrics"]:
                suggestions.append(f"Add {metric} metrics using format: {details['impact_phrases'][0]}")
    
    return suggestions[:3]  # Return top 3 most relevant suggestions

def calculate_technical_depth(achievement: Dict) -> float:
    """Calculate technical depth score (0-1) based on various factors"""
    score = 0.0
    description = achievement.get("description", "").lower()
    
    # Check for technical terms
    tech_term_count = sum(1 for tech in TECH_KEYWORDS["languages"] + TECH_KEYWORDS["frameworks"] 
                         if tech.lower() in description)
    
    # Check for metrics
    metrics = extract_metrics(achievement)
    
    # Check for technical context
    has_problem_statement = any(word in description for word in ["solved", "fixed", "improved", "optimized"])
    has_solution_approach = any(word in description for word in ["using", "implemented", "developed", "designed"])
    
    # Calculate final score
    score += min(tech_term_count * 0.2, 0.4)  # Up to 0.4 for technical terms
    score += min(len(metrics) * 0.2, 0.3)      # Up to 0.3 for metrics
    score += 0.15 if has_problem_statement else 0  # 0.15 for problem statement
    score += 0.15 if has_solution_approach else 0  # 0.15 for solution approach
    
    return min(score, 1.0)

def suggest_technical_details(achievement: Dict) -> List[str]:
    """Suggest ways to add technical depth to achievement"""
    suggestions = []
    description = achievement.get("description", "").lower()
    
    if not any(tech.lower() in description for tech in TECH_KEYWORDS["languages"] + TECH_KEYWORDS["frameworks"]):
        suggestions.append("Specify the technologies/frameworks used")
    
    if not extract_metrics(achievement):
        suggestions.append("Add quantifiable metrics showing impact")
    
    if not any(word in description for word in ["solved", "fixed", "improved", "optimized"]):
        suggestions.append("Describe the technical challenge addressed")
    
    if not any(word in description for word in ["using", "implemented", "developed", "designed"]):
        suggestions.append("Explain your technical approach/solution")
    
    return suggestions

def assess_skill_level(profile_data: Dict) -> Dict:
    """Assess skill levels across different domains"""
    assessment = {
        "overall_level": "",
        "domain_levels": {},
        "next_steps": [],
        "suggested_evidence": []
    }
    
    # Analyze experience and projects
    experiences = profile_data.get("experiences", [])
    projects = profile_data.get("projects", [])
    
    # Check indicators for each level
    level_scores = {
        "learning": 0,
        "applying": 0,
        "optimizing": 0,
        "leading": 0
    }
    
    for exp in experiences + projects:
        description = exp.get("description", "").lower()
        for level, details in SKILL_PROGRESSION["levels"].items():
            # Count matching indicators
            indicators = sum(1 for ind in details["indicators"] 
                          if any(keyword in description for keyword in ind.split("_")))
            level_scores[level] += indicators
    
    # Determine overall level
    max_level = max(level_scores.items(), key=lambda x: x[1])
    assessment["overall_level"] = max_level[0]
    
    # Assess domain-specific levels
    for domain in SKILL_PROGRESSION["domains"]:
        domain_score = 0
        for exp in experiences + projects:
            description = exp.get("description", "").lower()
            domain_score += sum(1 for skill in SKILL_PROGRESSION["domains"][domain]
                              if skill in description)
        assessment["domain_levels"][domain] = domain_score
    
    # Suggest next steps
    current_level = SKILL_PROGRESSION["levels"][assessment["overall_level"]]
    assessment["next_steps"] = current_level["next_steps"]
    
    # Suggest missing evidence
    missing_evidence = []
    for evidence in current_level["evidence"]:
        if not any(evidence in exp.get("description", "").lower() 
                  for exp in experiences + projects):
            missing_evidence.append(evidence)
    assessment["suggested_evidence"] = missing_evidence
    
    return assessment

def suggest_skill_improvements(assessment: Dict) -> List[str]:
    """Suggest specific improvements based on skill assessment"""
    suggestions = []
    current_level = assessment["overall_level"]
    
    # Suggest evidence improvements
    if assessment["suggested_evidence"]:
        suggestions.append({
            "type": "add_evidence",
            "suggestions": [
                f"Add evidence of {evidence.replace('_', ' ')} to strengthen your profile"
                for evidence in assessment["suggested_evidence"][:3]
            ]
        })
    
    # Suggest next level progression
    next_steps = SKILL_PROGRESSION["levels"][current_level]["next_steps"]
    suggestions.append({
        "type": "progression",
        "suggestions": [
            f"Work on {step.replace('_', ' ')} to progress to the next level"
            for step in next_steps[:3]
        ]
    })
    
    # Suggest domain improvements
    weak_domains = [
        domain for domain, score in assessment["domain_levels"].items()
        if score < 2  # threshold for domain strength
    ]
    if weak_domains:
        suggestions.append({
            "type": "domain_improvement",
            "suggestions": [
                f"Strengthen your {domain} skills through projects or experiences"
                for domain in weak_domains
            ]
        })
    
    return suggestions

def detect_initial_intent(message: str) -> str:
    """Detect if the first message indicates a specific functionality request"""
    message = message.lower()
    
    # Profile-related phrases
    if any(phrase in message for phrase in [
        "profile", "headline", "about section", "experience", "education", 
        "improve my profile", "create profile", "help with my profile",
        "make my profile", "update profile"
    ]):
        return "profile_start"
    
    # Post-related phrases
    if any(phrase in message for phrase in [
        "post", "write", "share", "create post", "make a post",
        "project post", "hackathon post", "achievement post",
        "help me write", "post about"
    ]):
        return "post_start"
    
    # Network-related phrases
    if any(phrase in message for phrase in [
        "network", "connect", "connection", "networking",
        "build network", "grow network", "find connections",
        "meet people", "expand network", "professional network"
    ]):
        return "network_start"
    
    return None

def run(env: Environment):
    system_prompt = """You are a LinkedIn profile strategist who specializes in helping computer science students transition into software engineering roles. You understand both the technical and career aspects of software development, and know how to present technical achievements to catch recruiters' attention.

KEY OBJECTIVES:
- Guide natural networking progression for CS students
- Focus on individual's technical strengths and interests
- Build meaningful professional relationships in their chosen domain
- Maintain relevance to their specific tech stack and goals

NETWORKING GUIDANCE:
Guide users through networking phases naturally, focusing on one clear action at a time:

Phase 1 - Foundation
- Understand student's specific technical focus (languages, frameworks, domains)
- Use NETWORK_TARGETS to suggest relevant communities based on their interests
- Craft personalized connections using generate_connection_message() with their tech context
- Build on their unique technical experience and projects

Phase 2 - Engagement
- Use suggest_engagement_plan() for focused growth in their domain
- Keep technical context specific to their stack (e.g., backend scaling, ML models, frontend frameworks)
- Build on their demonstrated interests and strengths
- Guide meaningful interactions in their chosen field

Phase 3 - Growth
- Focus on value-add opportunities in their technical domain
- Guide collaborative engagement based on their expertise
- Expand network naturally through shared technical interests
- Maintain relevance to their career goals

RESPONSE PRINCIPLES:
1. Focus
- ONE clear next step based on their technical context
- Build on their specific experiences and interests
- Keep aligned with their tech stack
- Show natural progression in their domain

2. Value
- Technical relevance to their chosen field
- Clear benefits for their career path
- Immediate actionability in their context
- Professional growth in their area

3. Guidance
- Natural conversation about their interests
- Specific suggestions for their domain
- Clear direction based on their goals
- Simple choices aligned with their path

4. Data Usage
- Use NETWORK_TARGETS for suggestions matching their interests
- Generate personalized messages referencing their specific tech experience
- Create structured plans relevant to their domain
- Keep technical focus aligned with their goals

TECHNICAL DOMAINS:
Consider various paths including:
- Backend Development (distributed systems, APIs, databases)
- Frontend Development (web frameworks, UX, performance)
- Full Stack Development
- Machine Learning/AI
- Mobile Development
- DevOps/Infrastructure
- Security Engineering
- Game Development
- Embedded Systems

AVOID:
- Multiple actions at once
- Generic networking advice
- Losing sight of their specific technical context
- Overwhelming options
- Assuming one technology stack fits all

Remember: Guide each student through natural networking progression while maintaining focus on their specific technical interests and career goals. Use data structures to provide relevant suggestions while keeping conversation natural and focused on their chosen path."""

    prompt = {"role": "system", "content": system_prompt}
    
    # Get all messages
    messages = env.list_messages()
    
    # If this is the first user message
    if not messages or len(messages) <= 1:
        if messages and len(messages) == 1:
            # Check if the first message indicates a specific intent
            initial_intent = detect_initial_intent(messages[0].get("content", ""))
            if initial_intent:
                # Go directly to the requested functionality
                response = CONVERSATION_TEMPLATES[initial_intent]["message"]
                env.add_reply(response)
                env.request_user_input()
                return
        
        # If no specific intent detected, show welcome message
        welcome_message = CONVERSATION_TEMPLATES["welcome"]["message"]
        env.add_reply(welcome_message)
        env.request_user_input()
        return

    # Process user input and generate response
    result = env.completion([prompt] + messages)
    env.add_reply(result)
    env.request_user_input()

run(env)

