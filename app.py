import streamlit as st
import requests
import re
import json
from urllib.parse import urlparse
import base64

# Page configuration
st.set_page_config(
    page_title="GitHub Repo Setup Guide",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .tech-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        background: #667eea;
        color: white;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    .command-box {
        background: #2d3748;
        color: #e2e8f0;
        padding: 1rem;
        border-radius: 5px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def extract_repo_info(github_url):
    """Extract owner and repo name from GitHub URL"""
    pattern = r'github\.com/([^/]+)/([^/]+)'
    match = re.search(pattern, github_url)
    if match:
        return match.group(1), match.group(2).replace('.git', '')
    return None, None

def get_repo_data(owner, repo):
    """Fetch repository data from GitHub API"""
    try:
        # Repository basic info
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        repo_response = requests.get(repo_url, timeout=10)
        
        if repo_response.status_code != 200:
            return None, "Repository not found or is private"
        
        repo_data = repo_response.json()
        
        # Repository contents
        contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        contents_response = requests.get(contents_url, timeout=10)
        contents_data = contents_response.json() if contents_response.status_code == 200 else []
        
        return {
            'repo_data': repo_data,
            'contents': contents_data
        }, None
        
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching repository data: {str(e)}"

def detect_technologies(contents, repo_data):
    """Detect technologies used in the repository"""
    tech_stack = set()
    files = [item['name'].lower() for item in contents if item['type'] == 'file']
    
    # Language detection from GitHub API
    if repo_data.get('language'):
        tech_stack.add(repo_data['language'])
    
    # File-based detection
    tech_patterns = {
        'Python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'pipfile', 'conda.yml', 'environment.yml'],
        'Node.js': ['package.json', 'package-lock.json', 'yarn.lock'],
        'React': ['package.json'],  # Will be refined later
        'Django': ['manage.py', 'django'],
        'Flask': ['app.py', 'flask'],
        'FastAPI': ['fastapi', 'uvicorn'],
        'Streamlit': ['streamlit', '.streamlit'],
        'Docker': ['dockerfile', 'docker-compose.yml', 'docker-compose.yaml'],
        'Java': ['pom.xml', 'build.gradle', 'gradle.properties'],
        'Go': ['go.mod', 'go.sum'],
        'Rust': ['cargo.toml', 'cargo.lock'],
        'Ruby': ['gemfile', 'gemfile.lock'],
        'PHP': ['composer.json', 'composer.lock'],
        'C++': ['makefile', 'cmake', 'cmakelists.txt'],
        'HTML/CSS/JS': ['index.html', 'style.css', 'script.js'],
        'Vue.js': ['vue.config.js', 'nuxt.config.js'],
        'Angular': ['angular.json', 'ng'],
        'Next.js': ['next.config.js']
    }
    
    for tech, patterns in tech_patterns.items():
        if any(pattern in ' '.join(files) for pattern in patterns):
            tech_stack.add(tech)
    
    return list(tech_stack)

def get_file_content(owner, repo, filename):
    """Get content of a specific file from the repository"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.json()
            if content.get('encoding') == 'base64':
                return base64.b64decode(content['content']).decode('utf-8', errors='ignore')
        return None
    except:
        return None

def generate_setup_steps(owner, repo, tech_stack, repo_data, contents):
    """Generate step-by-step setup instructions"""
    steps = []
    
    # Step 1: Clone Repository
    steps.append({
        'title': '📥 Clone the Repository',
        'description': 'Download the repository to your local machine',
        'commands': [
            f'git clone https://github.com/{owner}/{repo}.git',
            f'cd {repo}'
        ],
        'notes': ['Make sure you have Git installed on your system']
    })
    
    # Step 2: Technology-specific setup
    if 'Python' in tech_stack:
        python_steps = generate_python_steps(owner, repo, contents)
        steps.extend(python_steps)
    
    if 'Node.js' in tech_stack:
        node_steps = generate_node_steps(owner, repo, contents)
        steps.extend(node_steps)
    
    if 'Docker' in tech_stack:
        docker_steps = generate_docker_steps()
        steps.extend(docker_steps)
    
    if 'Java' in tech_stack:
        java_steps = generate_java_steps(contents)
        steps.extend(java_steps)
    
    # Step 3: Running the application
    run_steps = generate_run_steps(tech_stack, contents, owner, repo)
    steps.extend(run_steps)
    
    return steps

def generate_python_steps(owner, repo, contents):
    """Generate Python-specific setup steps"""
    steps = []
    files = [item['name'].lower() for item in contents if item['type'] == 'file']
    
    # Virtual environment setup
    steps.append({
        'title': '🐍 Set up Python Environment',
        'description': 'Create and activate a virtual environment',
        'commands': [
            'python -m venv venv',
            '# On Windows:',
            'venv\\Scripts\\activate',
            '# On macOS/Linux:',
            'source venv/bin/activate'
        ],
        'notes': ['Python 3.7+ recommended', 'Virtual environment helps avoid dependency conflicts']
    })
    
    # Install dependencies
    install_commands = []
    if 'requirements.txt' in files:
        install_commands.append('pip install -r requirements.txt')
    elif 'setup.py' in files:
        install_commands.append('pip install -e .')
    elif 'pyproject.toml' in files:
        install_commands.append('pip install -e .')
    elif 'pipfile' in files:
        install_commands.extend(['pip install pipenv', 'pipenv install'])
    else:
        install_commands.append('# Check for any Python dependencies and install manually')
    
    steps.append({
        'title': '📦 Install Dependencies',
        'description': 'Install required Python packages',
        'commands': install_commands,
        'notes': ['Dependencies are listed in requirements.txt or similar files']
    })
    
    return steps

def generate_node_steps(owner, repo, contents):
    """Generate Node.js-specific setup steps"""
    steps = []
    files = [item['name'].lower() for item in contents if item['type'] == 'file']
    
    # Check for package managers
    if 'yarn.lock' in files:
        package_manager = 'yarn'
        install_cmd = 'yarn install'
    elif 'package-lock.json' in files:
        package_manager = 'npm'
        install_cmd = 'npm install'
    else:
        package_manager = 'npm'
        install_cmd = 'npm install'
    
    steps.append({
        'title': '📦 Install Node.js Dependencies',
        'description': f'Install packages using {package_manager}',
        'commands': [install_cmd],
        'notes': [
            'Make sure you have Node.js installed (version 14+ recommended)',
            f'This project uses {package_manager} as package manager'
        ]
    })
    
    return steps

def generate_docker_steps():
    """Generate Docker-specific setup steps"""
    return [{
        'title': '🐳 Docker Setup (Alternative)',
        'description': 'Run the application using Docker',
        'commands': [
            'docker build -t repo-app .',
            'docker run -p 8080:8080 repo-app'
        ],
        'notes': [
            'Make sure Docker is installed and running',
            'Check Dockerfile for specific port configurations'
        ]
    }]

def generate_java_steps(contents):
    """Generate Java-specific setup steps"""
    files = [item['name'].lower() for item in contents if item['type'] == 'file']
    
    if 'pom.xml' in files:
        return [{
            'title': '☕ Java Maven Setup',
            'description': 'Build and run Java application with Maven',
            'commands': [
                'mvn clean install',
                'mvn spring-boot:run'
            ],
            'notes': ['Make sure Java 8+ and Maven are installed']
        }]
    elif any('gradle' in f for f in files):
        return [{
            'title': '☕ Java Gradle Setup',
            'description': 'Build and run Java application with Gradle',
            'commands': [
                './gradlew build',
                './gradlew run'
            ],
            'notes': ['Make sure Java 8+ is installed', 'Gradle wrapper is included']
        }]
    
    return []

def generate_run_steps(tech_stack, contents, owner, repo):
    """Generate application running steps"""
    files = [item['name'].lower() for item in contents if item['type'] == 'file']
    steps = []
    
    # Try to detect main entry point
    run_commands = []
    
    if 'Streamlit' in tech_stack:
        if 'app.py' in files:
            run_commands.append('streamlit run app.py')
        elif 'main.py' in files:
            run_commands.append('streamlit run main.py')
        else:
            run_commands.append('streamlit run <main_file>.py')
    
    elif 'Flask' in tech_stack:
        if 'app.py' in files:
            run_commands.extend(['export FLASK_APP=app.py', 'flask run'])
        elif 'main.py' in files:
            run_commands.extend(['export FLASK_APP=main.py', 'flask run'])
        else:
            run_commands.extend(['python app.py'])
    
    elif 'Django' in tech_stack:
        run_commands.extend([
            'python manage.py migrate',
            'python manage.py runserver'
        ])
    
    elif 'FastAPI' in tech_stack:
        if 'main.py' in files:
            run_commands.append('uvicorn main:app --reload')
        else:
            run_commands.append('uvicorn app:app --reload')
    
    elif 'Node.js' in tech_stack:
        run_commands.append('npm start')
        if 'React' in tech_stack:
            run_commands.append('# Or: npm run dev')
    
    elif 'Python' in tech_stack:
        if 'main.py' in files:
            run_commands.append('python main.py')
        elif 'app.py' in files:
            run_commands.append('python app.py')
        else:
            run_commands.append('python <main_file>.py')
    
    if run_commands:
        steps.append({
            'title': '🚀 Run the Application',
            'description': 'Start the application',
            'commands': run_commands,
            'notes': [
                'Check the README file for specific run instructions',
                'Application will typically run on localhost with a specific port'
            ]
        })
    
    # Environment setup if needed
    env_files = [f for f in files if '.env' in f or 'config' in f]
    if env_files:
        steps.append({
            'title': '⚙️ Environment Configuration',
            'description': 'Set up environment variables',
            'commands': [
                '# Copy example environment file (if exists)',
                'cp .env.example .env',
                '# Edit .env file with your configurations'
            ],
            'notes': [
                'Check for .env.example or similar configuration files',
                'Add necessary API keys, database URLs, etc.'
            ]
        })
    
    return steps

# Main Streamlit App
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 GitHub Repository Setup Guide</h1>
        <p>Get step-by-step instructions to set up and run any GitHub repository</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ How to Use")
        st.markdown("""
        1. **Paste GitHub URL**: Enter any public GitHub repository URL
        2. **Analyze**: Click analyze to scan the repository
        3. **Follow Steps**: Get detailed setup instructions
        4. **Run Code**: Execute the provided commands
        """)
        
        st.header("✨ Features")
        st.markdown("""
        - 🔍 **Auto-detection** of technologies
        - 📋 **Step-by-step** setup guide
        - 💻 **Copy-paste** commands
        - 🆓 **Completely free** to use
        - 🌐 **No API keys** required
        """)
    
    # Main content
    st.subheader("📎 Enter GitHub Repository URL")
    
    github_url = st.text_input(
        "",
        placeholder="https://github.com/username/repository",
        help="Paste any public GitHub repository URL",
        label_visibility="collapsed"
    )
    
    # Center the button below input
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 Analyze Repository", type="primary", use_container_width=True)
    
    if analyze_button and github_url:
        # Validate URL
        if 'github.com' not in github_url:
            st.error("Please enter a valid GitHub repository URL")
            return
        
        # Extract repository information
        owner, repo = extract_repo_info(github_url)
        if not owner or not repo:
            st.error("Could not parse repository URL. Please check the format.")
            return
        
        # Show loading
        with st.spinner(f"Analyzing {owner}/{repo}..."):
            # Fetch repository data
            data, error = get_repo_data(owner, repo)
            
            if error:
                st.error(error)
                return
            
            repo_data = data['repo_data']
            contents = data['contents']
        
        # Display repository info
        st.success(f"✅ Successfully analyzed **{owner}/{repo}**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⭐ Stars", repo_data.get('stargazers_count', 0))
        with col2:
            st.metric("🍴 Forks", repo_data.get('forks_count', 0))
        with col3:
            st.metric("📁 Size", f"{repo_data.get('size', 0)} KB")
        
        # Repository description
        if repo_data.get('description'):
            st.info(f"**Description:** {repo_data['description']}")
        
        # Detect technologies
        tech_stack = detect_technologies(contents, repo_data)
        
        if tech_stack:
            st.subheader("🔧 Detected Technologies")
            tech_html = "".join([f'<span class="tech-badge">{tech}</span>' for tech in tech_stack])
            st.markdown(tech_html, unsafe_allow_html=True)
        
        # Generate setup steps
        st.subheader("📋 Setup Instructions")
        steps = generate_setup_steps(owner, repo, tech_stack, repo_data, contents)
        
        for i, step in enumerate(steps, 1):
            with st.expander(f"**Step {i}: {step['title']}**", expanded=True):
                st.markdown(f"*{step['description']}*")
                
                if step['commands']:
                    st.markdown("**Commands to run:**")
                    command_text = '\n'.join(step['commands'])
                    st.code(command_text, language='bash')
                
                if step.get('notes'):
                    st.markdown("**📝 Notes:**")
                    for note in step['notes']:
                        st.markdown(f"- {note}")
        
        # Additional resources
        st.subheader("📚 Additional Resources")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📖 View README"):
                readme_content = get_file_content(owner, repo, 'README.md')
                if readme_content:
                    st.markdown("### README.md")
                    st.markdown(readme_content[:2000] + ("..." if len(readme_content) > 2000 else ""))
                else:
                    st.info("No README.md found")
        
        with col2:
            st.markdown(f"**🔗 [View on GitHub]({github_url})**")
        
        with col3:
            if repo_data.get('homepage'):
                st.markdown(f"**🌐 [Live Demo]({repo_data['homepage']})**")
    
    elif analyze_button:
        st.warning("Please enter a GitHub repository URL first")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Made with ❤️ using Streamlit | 100% Free & Open Source</p>
        <p><small>This tool uses GitHub's public API and doesn't require authentication for public repositories</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()