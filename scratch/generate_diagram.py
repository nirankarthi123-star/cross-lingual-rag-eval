from graphviz import Digraph

def create_architecture_diagram():
    dot = Digraph(comment='Architecture Diagram', format='png')
    
    dot.attr(rankdir='TB', size='8,10', fontname='Helvetica')
    dot.attr('node', shape='box', style='filled', fillcolor='#f0f0f0', fontname='Helvetica', fontsize='10')
    dot.attr('edge', fontname='Helvetica', fontsize='9')
    
    dot.node('source', 'Source Documents')
    dot.node('processing', 'Document Processing')
    dot.node('chunking', 'Text Chunking')
    dot.node('embeddings', 'Multilingual Embeddings\n(intfloat/multilingual-e5-base)')
    dot.node('faiss', 'FAISS Vector Store', shape='cylinder', fillcolor='#d9edf7')
    
    dot.node('user_query', 'User Query', shape='oval', fillcolor='#dff0d8')
    dot.node('detection', 'Code-Mix Detection')
    dot.node('normalization', 'Optional Query Normalization\n(Mitigation Enabled)')
    dot.node('retrieval', 'Top-K Retrieval')
    
    dot.node('llm', 'LLM Answer Generation\n(Groq / gpt-oss-20b)')
    dot.node('answer', 'Generated Answer', shape='oval')
    
    dot.node('judge', 'LLM-as-a-Judge\n(Faithfulness)')
    dot.node('score', 'Faithfulness Score +\nHallucination Flag')
    
    dot.node('sqlite', 'SQLite Storage', shape='cylinder', fillcolor='#fcf8e3')
    dot.node('analysis', 'Statistical Analysis\n(SciPy / Wilcoxon)')
    dot.node('results', 'Final Results', shape='oval', fillcolor='#f2dede')
    
    # Document Pipeline
    dot.edge('source', 'processing')
    dot.edge('processing', 'chunking')
    dot.edge('chunking', 'embeddings')
    dot.edge('embeddings', 'faiss')
    
    # Query Pipeline
    dot.edge('user_query', 'detection')
    dot.edge('detection', 'normalization')
    dot.edge('normalization', 'retrieval')
    dot.edge('faiss', 'retrieval', style='dashed', label='Vector Search')
    
    # Generation & Evaluation
    dot.edge('retrieval', 'llm', label='Retrieved Context')
    dot.edge('llm', 'answer')
    dot.edge('answer', 'judge')
    dot.edge('retrieval', 'judge', style='dashed', label='Context Reference')
    dot.edge('judge', 'score')
    
    # Storage and Results
    dot.edge('score', 'sqlite')
    dot.edge('sqlite', 'analysis')
    dot.edge('analysis', 'results')
    
    dot.render('architecture_diagram')

if __name__ == '__main__':
    create_architecture_diagram()
