import re
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Common technical skills database
TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'cpp', 'c++', 'csharp', 'c#',
    'ruby', 'php', 'swift', 'kotlin', 'go', 'golang', 'rust', 'scala', 'r', 'matlab',
    'groovy', 'perl', 'powershell', 'bash', 'shell', 'dart', 'julia', 'haskell',
    'c', 'objective-c', 'assembly', 'cobol', 'fortran', 'lua', 'elixir',

    # Web Frameworks & Libraries
    'django', 'flask', 'fastapi', 'spring', 'spring boot', 'react', 'angular',
    'vue', 'vue.js', 'express', 'express.js', 'node.js', 'nodejs', 'asp.net', 'rails',
    'laravel', 'symfony', 'gin', 'echo', 'actix', 'rocket', 'next.js', 'nuxt.js',
    'svelte', 'backbone', 'ember', 'meteor', 'gatsby', 'redux', 'mobx', 'rxjs',
    'jquery', 'bootstrap', 'tailwind', 'material-ui', 'chakra', 'ant design',

    # Databases & Storage
    'sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'cassandra', 'redis',
    'elasticsearch', 'firebase', 'dynamodb', 'mariadb', 'sqlite', 'neo4j',
    'couchdb', 'influxdb', 'postgres', 'sqlserver', 'mssql', 'db2', 'sybase',
    'memcached', 'aerospike', 'cockroachdb', 'timescaledb', 'clickhouse',
    'supabase', 'planetscale', 'airtable', 'fauna', 'dgraph',

    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
    'jenkins', 'gitlab', 'github actions', 'terraform', 'ansible', 'helm',
    'ci/cd', 'devops', 'microservices', 'serverless', 'lambda', 'cloud',
    'cloudformation', 'pulumi', 'vagrant', 'packer', 'consul', 'vault',
    'prometheus', 'grafana', 'datadog', 'new relic', 'splunk', 'elk stack',
    'circleci', 'travis ci', 'bamboo', 'teamcity', 'octopus', 'spinnaker',

    # Data & Analytics & ML
    'machine learning', 'ml', 'deep learning', 'nlp', 'computer vision', 'cv',
    'tensorflow', 'keras', 'pytorch', 'scikit-learn', 'sklearn', 'pandas',
    'numpy', 'spark', 'pyspark', 'hadoop', 'hive', 'pig', 'kafka', 'airflow',
    'tableau', 'power bi', 'looker', 'data science', 'analytics', 'big data',
    'etl', 'data pipeline', 'data engineering', 'feature engineering',
    'neural networks', 'cnn', 'rnn', 'lstm', 'gru', 'transformers', 'bert',
    'gpt', 'yolo', 'opencv', 'hugging face', 'xgboost', 'lightgbm', 'catboost',
    'matplotlib', 'seaborn', 'plotly', 'dask', 'ray', 'mlflow', 'kubeflow',

    # API & Messaging
    'rest api', 'rest', 'restful', 'graphql', 'soap', 'websocket', 'grpc',
    'amqp', 'mqtt', 'rabbitmq', 'activemq', 'zeromq', 'api gateway',
    'api', 'webhook', 'http', 'https', 'tcp/ip', 'udp',

    # Version Control
    'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial', 'perforce',
    'version control', 'source control',

    # Testing & QA
    'junit', 'pytest', 'unittest', 'selenium', 'testng', 'mocha', 'jest',
    'cypress', 'postman', 'jira', 'qa', 'quality assurance', 'testing',
    'automation testing', 'unit testing', 'integration testing', 'e2e testing',
    'test automation', 'cucumber', 'behave', 'robot framework', 'jmeter',
    'loadrunner', 'gatling', 'locust', 'performance testing', 'load testing',

    # Mobile Development
    'ios', 'android', 'react native', 'flutter', 'xamarin', 'cordova',
    'ionic', 'phonegap', 'native script', 'swift ui', 'jetpack compose',
    'kotlin multiplatform', 'mobile development', 'mobile app',

    # Frontend Technologies
    'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less', 'stylus',
    'webpack', 'gulp', 'grunt', 'parcel', 'rollup', 'vite', 'babel',
    'typescript', 'javascript', 'es6', 'es7', 'es8', 'dom', 'ajax',

    # Backend & Architecture
    'microservices', 'monolith', 'soa', 'event-driven', 'cqrs', 'saga',
    'api design', 'system design', 'distributed systems', 'scalability',
    'load balancing', 'caching', 'message queue', 'pub/sub',

    # Security
    'oauth', 'jwt', 'saml', 'ssl', 'tls', 'encryption', 'authentication',
    'authorization', 'security', 'penetration testing', 'owasp', 'xss',
    'csrf', 'sql injection', 'cryptography', 'zero trust', 'iam',

    # Methodologies
    'agile', 'scrum', 'kanban', 'waterfall', 'lean', 'devops', 'sre',
    'pair programming', 'tdd', 'bdd', 'ddd', 'ci/cd', 'continuous integration',
    'continuous delivery', 'continuous deployment',

    # Tools & Platforms
    'jira', 'confluence', 'slack', 'teams', 'zoom', 'notion', 'trello',
    'asana', 'monday', 'linear', 'figma', 'sketch', 'adobe xd', 'invision',
    'zeplin', 'miro', 'lucidchart', 'draw.io',

    # Build & Package Management
    'npm', 'yarn', 'pip', 'maven', 'gradle', 'ant', 'make', 'cmake',
    'bazel', 'buck', 'pants', 'sbt', 'cargo', 'composer', 'nuget',
    'cocoapods', 'carthage', 'swift package manager',

    # Operating Systems
    'linux', 'unix', 'windows', 'macos', 'ubuntu', 'centos', 'debian',
    'rhel', 'fedora', 'arch', 'alpine', 'freebsd', 'solaris',

    # Containers & Orchestration
    'docker', 'docker compose', 'podman', 'kubernetes', 'k8s', 'openshift',
    'rancher', 'nomad', 'mesos', 'swarm', 'ecs', 'eks', 'aks', 'gke',

    # Networking
    'tcp/ip', 'dns', 'dhcp', 'vpn', 'load balancer', 'cdn', 'nginx',
    'apache', 'haproxy', 'traefik', 'envoy', 'istio', 'linkerd', 'consul',

    # Blockchain & Web3
    'blockchain', 'ethereum', 'solidity', 'web3', 'smart contracts',
    'defi', 'nft', 'cryptocurrency', 'bitcoin', 'hyperledger',
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
        print("⚠️ Empty text provided to extract_skills")
        return []

    # Convert text to lowercase for matching
    text_lower = text.lower()

    # Normalize text: remove extra whitespace and special characters for better matching
    text_normalized = re.sub(r'[^\w\s.#+]', ' ', text_lower)

    print(f"🔍 Searching for skills in text ({len(text)} chars)...")

    # Find all matched skills
    matched_skills = []
    skill_count = {}

    for skill in TECHNICAL_SKILLS:
        # Use word boundary matching to avoid partial matches
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'

        # Count occurrences
        matches = re.findall(pattern, text_normalized)
        if matches:
            count = len(matches)
            # Capitalize skill name properly
            skill_formatted = skill.upper() if len(skill) <= 3 else skill.title()

            if skill_formatted not in matched_skills:
                matched_skills.append(skill_formatted)
                skill_count[skill_formatted] = count
                print(f"  ✓ Found: {skill_formatted} ({count}x)")

    if not matched_skills:
        print("❌ No skills matched from the skill database")
        print(f"📝 Text sample (first 500 chars): {text[:500]}")
        return []

    # Sort by frequency, then alphabetically
    matched_skills.sort(key=lambda x: (-skill_count.get(x, 0), x))

    print(f"✓ Extracted {len(matched_skills)} unique skills")

    # Return top_n skills
    return matched_skills[:top_n]

