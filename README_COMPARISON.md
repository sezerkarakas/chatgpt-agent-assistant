# Monster Notebook Assistant - RAG vs Vector Store Comparison

## 🎯 Project Overview
This project compares two AI technologies for the Monster Notebook technical support assistant:
1. **Vector Store** (OpenAI Assistant API with vector search)
2. **RAG** (Retrieval-Augmented Generation with local embeddings)

## 📋 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Prepare Documents
Ensure your documents are in the `documents/` folder:
- Technical Service Information.txt
- Monster Model List.txt
- Problems and Solutions.txt
- Technical Service Office.txt

## 🚀 Usage

### Testing Individual Systems

#### Vector Store Version (Original)
```bash
python chat-assistant.py
```
- Uses OpenAI Assistant API
- Pre-configured vector store
- Type 'stats' for performance metrics
- Type 'exit' to quit and see final stats

#### RAG Version
```bash
python chat-assistant-rag.py
```
- Uses local embeddings + Chat Completions API
- Real-time document search
- Detailed performance tracking
- Token usage monitoring

#### Automated Comparison
```bash
python comparison_tool.py
```
- Runs both systems with identical test questions
- Generates detailed performance report
- Saves results to JSON file
- Provides winner analysis

## 📊 Comparison Metrics

### Speed (Response Time)
- **Vector Store**: Assistant API processing time
- **RAG**: Embedding search + generation time
- Measured in seconds per query

### Cost Analysis
- **Vector Store**: Fixed Assistant API costs
- **RAG**: Token-based pricing (embeddings + completions)
- Cost per query and total cost estimates

### Quality Factors
- Response accuracy
- Context relevance
- Citation handling
- Turkish language quality

## 🏆 Expected Results

### Speed Winner: Usually RAG
- RAG typically faster due to direct API calls
- Vector Store has Assistant API overhead
- Both systems are optimized for real-time use

### Cost Winner: Depends on Volume
- **Low Volume** (< 1000 queries/month): RAG cheaper
- **High Volume** (> 10000 queries/month): Vector Store cheaper
- Vector Store has predictable costs

### Quality: Generally Comparable
- Both use same knowledge base
- Vector Store may have better semantic search
- RAG offers more control over retrieval

## 📁 File Structure

```
├── chat-assistant.py          # Vector Store implementation (modified)
├── chat-assistant-rag.py      # RAG implementation
├── comparison_tool.py         # Automated comparison tool
├── requirements.txt           # Python dependencies
├── documents/                 # Knowledge base documents
├── static/                    # Web interface files
└── README_COMPARISON.md       # This file
```

## 🛠 Customization Options

### Adjusting RAG Parameters
Edit `chat-assistant-rag.py`:
- `chunk_size`: Document chunking size (default: 1000)
- `top_k`: Number of retrieved documents (default: 3)
- `similarity_threshold`: Minimum similarity score (default: 0.3)

### Modifying Test Questions
Edit `comparison_tool.py`:
- Update `TEST_QUESTIONS` list with your own queries
- Add domain-specific questions
- Include edge cases

### Performance Tuning
- Use different embedding models (text-embedding-3-small vs large)
- Adjust Chat Completions model (gpt-4o-mini vs gpt-4o)
- Optimize chunk sizes and overlap

## 📈 Interpreting Results

### Response Time Analysis
- Look for consistent performance
- Check for outliers or timeouts
- Consider user experience impact

### Cost Efficiency
- Calculate cost per successful resolution
- Factor in development and maintenance costs
- Consider scaling implications

### Quality Assessment
- Manual evaluation of responses
- Check for hallucinations
- Verify Turkish language accuracy

## 🚨 Troubleshooting

### Common Issues
1. **Missing Dependencies**: Run `pip install -r requirements.txt`
2. **API Key Errors**: Check `.env` file and OpenAI API key
3. **Document Loading**: Verify file paths and encoding (UTF-8)
4. **Memory Issues**: Reduce chunk size or document count

### Performance Issues
- Slow responses: Check internet connection and API limits
- High costs: Monitor token usage and optimize prompts
- Quality issues: Review document quality and chunk strategy

## 📝 Notes for Your Assignment

### Technology Comparison Points
1. **Architecture Differences**
   - Vector Store: Managed service approach
   - RAG: Self-managed retrieval system

2. **Scalability Considerations**
   - Vector Store: Auto-scaling, managed infrastructure
   - RAG: Manual scaling, more control

3. **Development Complexity**
   - Vector Store: Simpler setup, less control
   - RAG: More complex, full control over pipeline

4. **Maintenance Requirements**
   - Vector Store: Minimal maintenance
   - RAG: Regular optimization needed

Use these insights to write a comprehensive comparison report for your assignment!
