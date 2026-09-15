"""Curated demo dataset (safer than live scraping, per master plan §7).

Every posting models a realistic type. #2 is the adversarial "different wording,
same skill" job: nothing in it literally says "Docker/JS", so a naive keyword
matcher scores it low while this matcher (which resolves synonyms/implied skills)
ranks it correctly high.
"""
SAMPLE_JOBS = [
    {
        "id": "sr-python-backend",
        "title": "Senior Python Backend Engineer",
        "text": (
            "We are hiring a Senior Python Backend Engineer.\n\n"
            "Responsibilities:\n"
            "- Design and build REST APIs for our core platform\n"
            "- Work with relational databases at scale\n"
            "- Own deployments in a containerised microservices environment\n\n"
            "Qualifications (must-have):\n"
            "- 5+ years of Python development experience\n"
            "- Strong SQL and database design\n"
            "- Experience with Docker and container orchestration\n"
            "- Working knowledge of DevOps pipelines (CI/CD)\n\n"
            "Nice to have:\n"
            "- Experience with Kubernetes\n"
            "- Familiarity with Node.js services\n"
            "- Knowledge of distributed systems\n"
            "- Agile team experience\n"
        ),
    },
    {
        "id": "cloud-js-engineer",
        "title": "Cloud Platform Engineer (JS-focused)",
        "text": (
            "We are building scalable web services and need someone fluent in modern\n"
            "scripting and cloud platform engineering.\n\n"
            "What you need:\n"
            "- 4+ years of experience with modern scripting languages\n"
            "- Strong background shipping containerised applications\n"
            "- Experience orchestrating services across cloud infrastructure\n"
            "- Solid understanding of event-driven architecture and microservices\n\n"
            "Preferred:\n"
            "- Comfortable with server-side JavaScript\n"
            "- Exposure to CI/CD and infrastructure as code\n"
            "- Familiarity with relational and NoSQL data stores\n"
        ),
    },
    {
        "id": "ml-data-scientist",
        "title": "Machine Learning Engineer",
        "text": (
            "We are looking for an ML Engineer to own our recommendation models.\n\n"
            "Day to day:\n"
            "- Build and train ML models with modern frameworks\n"
            "- Productionise models on cloud infrastructure\n"
            "- Build data pipelines for training data\n"
            "- Evaluate model performance with rigorous experimentation\n\n"
            "Requirements:\n"
            "- 3+ years of machine learning experience\n"
            "- Strong Python programming skills\n"
            "- Hands-on experience with PyTorch or TensorFlow\n"
            "- Experience with data pipelines (Spark, Airflow, Kafka)\n\n"
            "Nice to have:\n"
            "- A/B testing experience\n"
            "- Cloud certification (AWS/GCP)\n"
        ),
    },
    {
        "id": "fullstack-react",
        "title": "Full-Stack Developer (React + Node)",
        "text": (
            "We are building a modern e-commerce experience and need a full-stack engineer.\n\n"
            "Must-haves:\n"
            "- 3+ years building React applications\n"
            "- Strong JavaScript including TypeScript\n"
            "- Experience building REST APIs on Node.js\n"
            "- Working knowledge of SQL\n\n"
            "Must have extras:\n"
            "- Testing experience (Jest or equivalent)\n"
            "- Git and code review workflows\n\n"
            "Nice to have:\n"
            "- GraphQL experience\n"
            "- E-commerce domain knowledge\n"
            "- Familiarity with Redis or similar caching\n"
        ),
    },
    {
        "id": "product-manager-growth",
        "title": "Product Manager — Growth",
        "text": (
            "We are hiring a Product Manager focused on growth for our SaaS product.\n\n"
            "What we expect:\n"
            "- 4+ years of product or project management experience\n"
            "- Track record leading cross-functional teams\n"
            "- Strong stakeholder communication and reporting skills\n"
            "- Data-driven decision making using analytics\n\n"
            "Preferred:\n"
            "- Experience with A/B testing and experimentation\n"
            "- Familiarity with SQL for self-serve analytics\n"
            "- Background in fintech or SaaS\n"
        ),
    },
    {
        "id": "payments-backend",
        "title": "Senior Backend Engineer — Payments Platform",
        "text": (
            "We are a fintech company building a high-scale payments platform and are\n"
            "looking for a senior engineer to own core services end to end.\n\n"
            "Must-haves:\n"
            "- Minimum 5 years of relevant industry experience\n"
            "- 5+ years of Python development with Django\n"
            "- Strong REST API design and implementation experience\n"
            "- Excellent SQL and PostgreSQL at scale\n"
            "- AWS experience on EC2 and Lambda\n"
            "- Docker containerisation and Kubernetes orchestration\n"
            "- Event-driven microservices with Kafka and message queues\n"
            "- CI/CD pipelines and automated deployments\n"
            "- Automated testing with pytest\n"
            "- Git and code review workflows\n\n"
            "Nice to have:\n"
            "- Fintech and payments domain knowledge\n"
            "- Experience leading or mentoring engineers\n"
            "- Strong communication for presenting technical decisions\n"
            "- Familiarity with data warehouses such as Redshift or BigQuery\n"
        ),
    },
]