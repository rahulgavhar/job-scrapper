# Sample job database for testing
# Each job has: id, title, company, location, description, skills required

JOBS_DB = [
    {
        "id": 1,
        "title": "Software Engineer",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "description": "Develop and maintain web applications using Python and Django.",
        "salary_range": "$120,000 - $150,000",
        "skills": ["Python", "Django", "REST", "SQL", "Git"]
    },
    {
        "id": 2,
        "title": "Frontend Developer",
        "company": "Webify",
        "location": "New York, NY",
        "description": "Build responsive UI with React and modern JavaScript.",
        "salary_range": "$100,000 - $130,000",
        "skills": ["JavaScript", "React", "HTML", "CSS", "Git"]
    },
    {
        "id": 3,
        "title": "Data Scientist",
        "company": "DataWorks",
        "location": "Remote",
        "description": "Analyze datasets and build ML models using Python.",
        "salary_range": "$130,000 - $160,000",
        "skills": ["Python", "Pandas", "Scikit-learn", "SQL", "Machine Learning"]
    },
    {
        "id": 4,
        "title": "DevOps Engineer",
        "company": "CloudOps",
        "location": "Austin, TX",
        "description": "Manage CI/CD pipelines and cloud infrastructure.",
        "salary_range": "$110,000 - $140,000",
        "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Python"]
    },
    {
        "id": 5,
        "title": "Backend Developer",
        "company": "API Solutions",
        "location": "Seattle, WA",
        "description": "Design and maintain backend services and APIs.",
        "salary_range": "$115,000 - $145,000",
        "skills": ["Node.js", "Express", "MongoDB", "REST", "Git"]
    },
    {
        "id": 6,
        "title": "Full Stack Developer",
        "company": "WebDynamics",
        "location": "Boston, MA",
        "description": "Build end-to-end web applications with Python and React.",
        "salary_range": "$125,000 - $155,000",
        "skills": ["Python", "React", "PostgreSQL", "REST", "Git", "JavaScript"]
    },
    {
        "id": 7,
        "title": "ML Engineer",
        "company": "AI Innovations",
        "location": "Remote",
        "description": "Develop machine learning models and deploy them to production.",
        "salary_range": "$140,000 - $170,000",
        "skills": ["Python", "TensorFlow", "Scikit-learn", "SQL", "Machine Learning"]
    },
    {
        "id": 8,
        "title": "Cloud Architect",
        "company": "CloudScale",
        "location": "San Jose, CA",
        "description": "Design and implement cloud infrastructure solutions.",
        "salary_range": "$150,000 - $180,000",
        "skills": ["AWS", "Docker", "Kubernetes", "CI/CD", "Python"]
    }
]

def get_all_jobs() -> list[dict]:
    """
    Return all jobs in the fake database.
    """
    return JOBS_DB

