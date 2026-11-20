"""RAG helpers: split documents into chunks and find the best chunks for a question.

Hybrid retrieval:
  1. Embeddings from a FREE OpenRouter embedding model (understands meaning:
     "money back" ~ "refund"). Uses the same OPENROUTER_API_KEY as the chat model.
  2. BM25 keyword ranking (exact words: product names, error codes).
The two rankings are merged with Reciprocal Rank Fusion (RRF).

Pure Python: no numpy, torch or other compiled packages are needed.
If the embedding API fails (rate limit, network), the bot falls back to keyword search only.
"""
import math
import os
import re
from collections import Counter
from functools import lru_cache

CHUNK_SIZE = 900      # target characters per chunk
CHUNK_OVERLAP = 150   # characters shared between neighbouring pieces of a very long paragraph

# Free OpenRouter embedding models, tried in this order. Free model lists change over time:
# check https://openrouter.ai/models?output_modalities=embeddings if one stops working.
EMBED_MODELS = [
    "nvidia/nemotron-3.5-embed-1b:free",
    "liquid/lfm-2.5-embedding-350m:free",
]
EMBED_BATCH = 16       # chunks sent per API request
MIN_SIMILARITY = 0.30  # chunks below this cosine similarity (and with no keyword match) are ignored
RRF_K = 60             # standard RRF constant
DEBUG = False          # True = print retrieval scores in the terminal (helps tune MIN_SIMILARITY)

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "am", "do", "does", "did",
    "i", "me", "my", "we", "our", "you", "your", "it", "its", "of", "to", "in", "on", "at",
    "for", "with", "and", "or", "but", "if", "so", "as", "by", "from", "this", "that", "these",
    "those", "can", "could", "will", "would", "should", "how", "what", "when", "where", "which",
    "who", "why", "there", "have", "has", "had", "about", "any", "please", "tell",
}


# ---------- Text helpers ----------
def tokenize(text):
    """Lowercase words, drop filler words, and trim a plural 's' so 'plans' matches 'plan'."""
    tokens = []
    for word in re.findall(r"\w+", text.lower()):
        if word in STOPWORDS:
            continue
        if len(word) > 3 and word.endswith("s"):
            word = word[:-1]
        tokens.append(word)
    return tokens


def split_long(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Cut a very long paragraph into overlapping pieces, preferring to break at sentence ends."""
    pieces = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            cut = max(text.rfind(". ", start, end), text.rfind("\n", start, end))
            if cut > start + size // 2:
                end = cut + 1
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return pieces


def make_chunks(source, text):
    """Split one document into chunks. Each chunk remembers its file name and nearest heading."""
    chunks = []
    state = {"heading": "", "buf": ""}

    def flush():
        if state["buf"].strip():
            chunks.append({"source": source, "heading": state["heading"], "text": state["buf"].strip()})
        state["buf"] = ""

    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        if para.startswith("#"):          # a markdown heading starts a new chunk
            flush()
            state["heading"] = para.split("\n")[0].lstrip("#").strip()
        if len(para) > CHUNK_SIZE:
            flush()
            for piece in split_long(para):
                chunks.append({"source": source, "heading": state["heading"], "text": piece})
            continue
        if state["buf"] and len(state["buf"]) + len(para) + 2 > CHUNK_SIZE:
            flush()
        state["buf"] = (state["buf"] + "\n\n" + para) if state["buf"] else para
    flush()
    return chunks


# ---------- Keyword ranking (BM25) ----------
class BM25:
    """Ranks chunks by how well their words match the question (standard BM25 formula)."""

    def __init__(self, token_lists, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.n = len(token_lists)
        self.lengths = [len(t) for t in token_lists]
        self.avg_len = (sum(self.lengths) / self.n) if self.n else 0.0
        self.term_freqs = [Counter(t) for t in token_lists]
        doc_freq = Counter()
        for tokens in token_lists:
            doc_freq.update(set(tokens))
        self.idf = {
            term: math.log(1 + (self.n - df + 0.5) / (df + 0.5)) for term, df in doc_freq.items()
        }

    def scores(self, query_tokens):
        result = [0.0] * self.n
        if not self.avg_len:
            return result
        for i, (tf, length) in enumerate(zip(self.term_freqs, self.lengths)):
            total = 0.0
            for term in query_tokens:
                freq = tf.get(term)
                if freq:
                    norm = freq + self.k1 * (1 - self.b + self.b * length / self.avg_len)
                    total += self.idf[term] * freq * (self.k1 + 1) / norm
            result[i] = total
        return result


# ---------- Embeddings (free OpenRouter models) ----------
@lru_cache(maxsize=1)
def get_client():
    from openai import OpenAI

    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        try:
            import streamlit as st
            key = st.secrets["OPENROUTER_API_KEY"]
        except Exception:
            key = None
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)


def normalize(vector):
    norm = math.sqrt(sum(x * x for x in vector)) or 1.0
    return [x / norm for x in vector]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def embed_texts(texts, model):
    """Return one normalized vector per text (so dot product = cosine similarity)."""
    client = get_client()
    vectors = []
    for start in range(0, len(texts), EMBED_BATCH):
        batch = texts[start:start + EMBED_BATCH]
        response = client.embeddings.create(model=model, input=batch)
        data = sorted(response.data, key=lambda d: d.index)
        vectors.extend(normalize(d.embedding) for d in data)
    if len(vectors) != len(texts):
        raise RuntimeError("Embedding API returned the wrong number of vectors")
    return vectors


class HybridIndex:
    """Holds the BM25 index plus the embedding vectors (None if embeddings were unavailable)."""

    def __init__(self, bm25, vectors, model):
        self.bm25 = bm25
        self.vectors = vectors
        self.model = model  # the model that made the vectors; queries must use the same one


def build_index(documents):
    """documents: list of (file_name, text). Returns (chunks, hybrid_index)."""
    chunks = []
    for name, text in documents:
        chunks.extend(make_chunks(name, text))
    if not chunks:
        return chunks, HybridIndex(BM25([]), None, None)

    token_lists = [tokenize(c["heading"] + " " + c["text"]) for c in chunks]
    texts = [(c["heading"] + ". " if c["heading"] else "") + c["text"] for c in chunks]

    vectors, model_used = None, None
    for model in EMBED_MODELS:
        try:
            vectors = embed_texts(texts, model)
            model_used = model
            print(f"[rag] Embeddings ready with {model}")
            break
        except Exception as e:
            print(f"[rag] Embedding model {model} failed: {e}")
    if vectors is None:
        print("[rag] Embeddings unavailable - using keyword search only.")

    return chunks, HybridIndex(BM25(token_lists), vectors, model_used)


def rank_positions(scores):
    """Map chunk index -> rank (0 = best)."""
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return {i: rank for rank, i in enumerate(order)}


def retrieve(query, chunks, index, top_k=4):
    """Return up to top_k (chunk, score) pairs that match the query. Empty if nothing matches."""
    if not query.strip() or not chunks:
        return []

    # Semantic scores (cosine similarity), if embeddings are available
    similarities = [0.0] * len(chunks)
    semantic_ok = False
    if index.vectors:
        try:
            query_vector = embed_texts([query], index.model)[0]
            similarities = [dot(query_vector, v) for v in index.vectors]
            semantic_ok = True
        except Exception as e:
            print(f"[rag] Query embedding failed, using keywords only: {e}")

    # Keyword scores
    query_tokens = tokenize(query)
    keyword_scores = index.bm25.scores(query_tokens) if query_tokens else [0.0] * len(chunks)

    if DEBUG:
        print(f"[rag] query={query!r} best_similarity={max(similarities):.3f} "
              f"best_keyword={max(keyword_scores):.3f} semantic={semantic_ok}")

    # Only consider chunks that are semantically close OR share a keyword with the question
    candidates = [
        i for i in range(len(chunks))
        if (semantic_ok and similarities[i] >= MIN_SIMILARITY) or keyword_scores[i] > 0
    ]
    if not candidates:
        return []

    # Reciprocal Rank Fusion: combine both rankings
    keyword_rank = rank_positions(keyword_scores)
    semantic_rank = rank_positions(similarities) if semantic_ok else None
    fused = {}
    for i in candidates:
        score = 1.0 / (RRF_K + keyword_rank[i])
        if semantic_rank is not None:
            score += 1.0 / (RRF_K + semantic_rank[i])
        fused[i] = score
    best = sorted(candidates, key=lambda i: fused[i], reverse=True)[:top_k]
    return [(chunks[i], fused[i]) for i in best]