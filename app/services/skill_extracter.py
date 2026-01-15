import re
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Common technical skills database
TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'cpp', 'c++', 'csharp', 'c#',
    'ruby', 'php', 'swift', 'kotlin', 'go', 'rust', 'scala', 'r', 'matlab',
    'groovy', 'perl', 'powershell', 'bash', 'shell',

    # Web Frameworks
    'django', 'flask', 'fastapi', 'spring', 'spring boot', 'react', 'angular',
    'vue', 'express', 'node.js', 'nodejs', 'asp.net', 'rails', 'laravel',
    'symfony', 'gin', 'echo', 'actix', 'rocket',

    # Databases
    'sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'cassandra', 'redis',
    'elasticsearch', 'firebase', 'dynamodb', 'mariadb', 'sqlite', 'neo4j',
    'couchdb', 'influxdb', 'postgres', 'sqlserver', 'mssql',

    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
    'jenkins', 'gitlab', 'github actions', 'terraform', 'ansible', 'helm',
    'ci/cd', 'devops', 'microservices', 'serverless', 'lambda', 'cloud',

    # Data & Analytics
    'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow',
    'keras', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'spark', 'hadoop',
    'hive', 'pig', 'kafka', 'airflow', 'tableau', 'power bi', 'looker',
    'data science', 'analytics', 'big data', 'etl', 'data pipeline',

    # API & Messaging
    'rest api', 'graphql', 'soap', 'websocket', 'grpc', 'amqp', 'mqtt',
    'rabbitmq', 'activemq', 'zeromq', 'api gateway', 'microservices',

    # Version Control
    'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial', 'perforce',

    # Testing & QA
    'junit', 'pytest', 'selenium', 'testng', 'mocha', 'jest', 'cypress',
    'postman', 'jira', 'qa', 'automation testing', 'unit testing',
    'integration testing', 'e2e testing',

    # Other Technologies
    'rest', 'xml', 'json', 'yaml', 'html', 'css', 'sass', 'less',
    'webpack', 'gulp', 'gradle', 'maven', 'npm', 'pip', 'docker',
    'linux', 'windows', 'macos', 'unix', 'aws', 'gcp', 'azure',
    'agile', 'scrum', 'kanban', 'jira', 'confluence', 'slack',
}

def extract_skills(text: str, top_n: int = 10) -> list[str]:
    """
    Extract skills from resume text using keyword matching.

    This is a simplified approach that doesn't rely on external ML models,
    making it compatible with all PyTorch versions.

    Args:
        text (str): The raw text from resume
        top_n (int): Maximum number of skills to return

    Returns:
        List of skill strings
    """
    if not text:
        return []

    # Convert text to lowercase for matching
    text_lower = text.lower()

    # Find all matched skills
    matched_skills = []
    for skill in TECHNICAL_SKILLS:
        # Use word boundary matching to avoid partial matches
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            matched_skills.append(skill.title())

    # Remove duplicates while preserving order
    unique_skills = list(dict.fromkeys(matched_skills))

    # Return top_n skills, sorted by frequency
    return unique_skills[:top_n]
