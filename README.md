# Code Review AI

An automated code review tool that analyzes GitHub repositories using AI to provide detailed code assessments.

## Features

- Automated code review using OpenAI's GPT-4 Turbo
- GitHub repository analysis
- Support for different developer levels (Junior, Middle, Senior)
- Redis caching for improved performance
- Asynchronous processing
- Comprehensive test coverage

## Tech Stack

- Python 3.10+
- FastAPI
- OpenAI API
- GitHub API
- Poetry for dependency management
- Docker & Docker Compose
- pytest for testing

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/code-review-ai.git
cd code-review-ai
```

2. Install dependencies using Poetry:

```bash
poetry install
```

3. Set up environment variables:

```bash
cp .env.example .env
```

Edit `.env` file with your credentials:

```
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_api_key
```

## Running the Application

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

### Manual Setup

1. Run the FastAPI application:

```bash
poetry run start
```

The API will be available at `http://localhost:8000`

## API Documentation

### POST /review

Analyzes a GitHub repository and provides a detailed code review.

**Request Body:**

```json
{
  "assignment_description": "string",
  "github_repo_url": "string",
  "candidate_level": "string" // Junior, Middle, or Senior
}
```

**Response Format:**

```json
{
  "status": "success" | "error",
  "found_files": ["list of analyzed files"],
  "comments": ["list of comments and suggestions"],
  "rating": "overall rating",
  "conclusion": "detailed conclusion"
}
```

## Testing

Run tests using pytest:

```bash
poetry run pytest
```

For coverage report:

```bash
poetry run pytest --cov=app --cov-report=term-missing
```

## Scaling Solution

### Handling High Traffic (100+ requests/minute)

To handle high traffic and large repositories, the following architecture improvements would be implemented:

1. **Queue-based Processing**

   - Implement message queues (e.g., RabbitMQ, AWS SQS) for asynchronous processing
   - Use worker processes to handle review requests in parallel
   - Implement webhook notifications for completed reviews

2. **Distributed Caching**

   - Scale Redis to a cluster configuration
   - Implement cache sharding for better performance
   - Cache frequently accessed repository data

3. **API Management**

   - Implement token bucket rate limiting
   - Use circuit breakers for external API calls
   - Batch API requests to optimize GitHub API usage

4. **Infrastructure**

   - Deploy using Kubernetes for automatic scaling
   - Use CDN for static content
   - Implement load balancing across multiple regions

5. **Database Solutions**

   - Use MongoDB/PostgreSQL for storing review results
   - Implement database sharding for horizontal scaling
   - Regular archiving of old review data

6. **Cost Management**
   - Implement smart batching of OpenAI API calls
   - Cache common review patterns
   - Use cheaper AI models for initial analysis

This architecture ensures high availability, fault tolerance, and efficient resource utilization while managing API rate limits and costs effectively.

### Handling Large Repositories (100+ files)

To efficiently process large repositories with hundreds of files, the following strategies would be implemented:

1. **Chunked Processing**

   - Split repository analysis into smaller chunks of files
   - Process files in parallel using worker pools
   - Implement smart file prioritization based on importance (e.g., source files over configuration files)

2. **Smart File Selection**

   - Analyze only modified files in recent commits
   - Focus on core application code files
   - Skip binary files, generated code, and vendor directories
   - Use .gitignore patterns to identify relevant files

3. **Hierarchical Analysis**

   - First analyze project structure and architecture
   - Then process individual components and modules
   - Finally, deep dive into specific files
   - Aggregate results using hierarchical summarization

4. **Resource Optimization**

   - Implement streaming file processing
   - Use memory-efficient file parsing
   - Employ lazy loading for file contents
   - Cache intermediate analysis results

5. **Token Management**

   - Calculate token usage before processing
   - Split large files into semantic chunks
   - Use compression for code representation
   - Implement token-aware batching strategies

6. **Incremental Processing**
   - Store previous analysis results
   - Process only changed files in subsequent reviews
   - Maintain analysis history for repositories
   - Enable delta reviews for efficiency

These strategies ensure efficient processing of large repositories while maintaining analysis quality and managing API limitations effectively.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
