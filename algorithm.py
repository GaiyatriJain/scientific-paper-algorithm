import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

PAPER_DB_FILE = "papers_db.json"

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for",
    "if", "in", "into", "is", "it", "no", "not", "of", "on", "or",
    "such", "that", "the", "their", "then", "there", "these", "they",
    "this", "to", "was", "will", "with", "from", "we", "can", "also",
    "which", "using", "used", "use", "via", "new", "may", "based"
}
TOKEN_RE = re.compile(r"[a-zA-Z]{3,}")
STATE_FILE = "recommender_state.json"


@dataclass
class Paper:
    paper_id: str
    title: str
    summary: str
    authors: List[str]
    categories: List[str]
    updated: str
    url: str
    text: str = field(init=False)

    def __post_init__(self):
        self.text = f"{self.title} {self.summary}"


def tokenize(text: str) -> List[str]:
    tokens = TOKEN_RE.findall(text.lower())
    return [token for token in tokens if token not in STOP_WORDS]


def load_paper_database() -> List[Paper]:
    if os.path.exists(PAPER_DB_FILE):
        try:
            with open(PAPER_DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Paper(**item) for item in data]
        except Exception:
            pass
    return [
        Paper(
            "arXiv:1706.03762",
            "Attention Is All You Need",
            "The Transformer model uses self-attention mechanisms to replace recurrent layers for sequence modeling tasks.",
            ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
            ["cs.CL", "cs.LG"],
            "2017-06-12T00:00:00Z",
            "https://arxiv.org/abs/1706.03762",
        ),
        Paper(
            "arXiv:1810.04805",
            "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
            "BERT introduces bidirectional training of Transformer encoders to achieve state-of-the-art results on many NLP tasks.",
            ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
            ["cs.CL", "cs.LG"],
            "2018-10-11T00:00:00Z",
            "https://arxiv.org/abs/1810.04805",
        ),
        Paper(
            "arXiv:2005.14165",
            "Language Models are Few-Shot Learners",
            "GPT-3 scales generative language models to 175 billion parameters and demonstrates strong few-shot performance.",
            ["Tom B. Brown", "Benjamin Mann", "Nick Ryder"],
            ["cs.CL", "cs.LG"],
            "2020-05-28T00:00:00Z",
            "https://arxiv.org/abs/2005.14165",
        ),
        Paper(
            "arXiv:1409.3215",
            "Sequence to Sequence Learning with Neural Networks",
            "This paper demonstrates an end-to-end approach using encoder-decoder LSTM networks for sequence prediction tasks.",
            ["Ilya Sutskever", "Oriol Vinyals", "Quoc V. Le"],
            ["cs.LG"],
            "2014-09-10T00:00:00Z",
            "https://arxiv.org/abs/1409.3215",
        ),
        Paper(
            "arXiv:1404.7828",
            "Generative Adversarial Networks",
            "GANs train two neural networks in opposition, allowing one to generate realistic samples and the other to discriminate them.",
            ["Ian Goodfellow", "Jean Pouget-Abadie", "Mehdi Mirza"],
            ["cs.LG"],
            "2014-06-10T00:00:00Z",
            "https://arxiv.org/abs/1404.7828",
        ),
        Paper(
            "arXiv:1505.04597",
            "U-Net: Convolutional Networks for Biomedical Image Segmentation",
            "U-Net is an architecture for fast and precise segmentation of medical images using only a few training examples.",
            ["Olaf Ronneberger", "Philipp Fischer", "Thomas Brox"],
            ["cs.CV"],
            "2015-05-18T00:00:00Z",
            "https://arxiv.org/abs/1505.04597",
        ),
        Paper(
            "arXiv:1710.10903",
            "Graph Attention Networks",
            "Graph Attention Networks combine graph structure with attention mechanisms to improve node classification.",
            ["Petar Veličković", "Guillem Cucurull", "Arantxa Casanova"],
            ["cs.LG", "cs.AI"],
            "2017-10-04T00:00:00Z",
            "https://arxiv.org/abs/1710.10903",
        ),
        Paper(
            "arXiv:1905.11946",
            "EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks",
            "EfficientNet uses a compound scaling method to improve accuracy and efficiency across model sizes.",
            ["Mingxing Tan", "Quoc V. Le"],
            ["cs.CV"],
            "2019-05-29T00:00:00Z",
            "https://arxiv.org/abs/1905.11946",
        ),
        Paper(
            "arXiv:1910.01108",
            "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter",
            "DistilBERT compresses BERT while retaining most of its language understanding capabilities.",
            ["Victor Sanh", "Lysandre Debut", "Julien Chaumond"],
            ["cs.CL", "cs.LG"],
            "2019-10-02T00:00:00Z",
            "https://arxiv.org/abs/1910.01108",
        ),
        Paper(
            "arXiv:1703.10593",
            "Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial Networks",
            "CycleGAN learns to translate images between domains without paired examples.",
            ["Jun-Yan Zhu", "Taesung Park", "Phillip Isola"],
            ["cs.CV"],
            "2017-03-10T00:00:00Z",
            "https://arxiv.org/abs/1703.10593",
        ),
        Paper(
            "arXiv:1812.04948",
            "A Simple Framework for Contrastive Learning of Visual Representations",
            "SimCLR shows how contrastive learning can produce strong visual features without labels.",
            ["Ting Chen", "Simon Kornblith", "Mohammad Norouzi"],
            ["cs.CV"],
            "2019-06-16T00:00:00Z",
            "https://arxiv.org/abs/2002.05709",
        ),
        Paper(
            "arXiv:2103.00020",
            "Learning Transferable Visual Models From Natural Language Supervision",
            "CLIP learns image-text embeddings from web-scale data to enable zero-shot object recognition.",
            ["Alec Radford", "Jong Wook Kim", "Chris Hallacy"],
            ["cs.CV", "cs.CL"],
            "2021-01-05T00:00:00Z",
            "https://arxiv.org/abs/2103.00020",
        ),
    ]


def strip_html_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")


def fetch_live_papers(query: str, max_results: int = 20) -> List[Paper]:
    query_text = urllib.parse.quote_plus(query)
    url = f"https://api.crossref.org/works?query={query_text}&rows={max_results}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read()

    data = json.loads(raw.decode("utf-8", errors="ignore"))
    items = data.get("message", {}).get("items", [])
    papers = []
    for item in items:
        paper_id = item.get("DOI", item.get("URL", ""))
        title_parts = item.get("title", [])
        title = " ".join(title_parts).strip() if title_parts else item.get(
            "container-title", ["Untitled"]
        )[0]
        summary = strip_html_tags(item.get("abstract", ""))
        if not summary:
            summary = item.get("subtitle", [""])[0] if item.get("subtitle") else ""
        authors = []
        for author in item.get("author", []):
            name_parts = []
            if author.get("given"):
                name_parts.append(author["given"])
            if author.get("family"):
                name_parts.append(author["family"])
            if name_parts:
                authors.append(" ".join(name_parts))
        if not authors and item.get("author"):
            authors = [str(author) for author in item.get("author")]
        categories = item.get("subject", []) or item.get("container-title", [])
        published = (
            item.get("created", {}).get("date-time")
            or item.get("issued", {}).get("date-time")
            or ""
        )
        url = item.get("URL") or ("https://doi.org/" + item.get("DOI", ""))
        papers.append(
            Paper(paper_id, title, summary, authors, categories, published, url)
        )
    if not papers:
        raise RuntimeError("No live papers were returned from the Crossref API.")
    return papers


def search_local_papers(query: str, max_results: int = 20) -> List[Paper]:
    papers = load_paper_database()
    q_terms = tokenize(query)
    results = []
    for paper in papers:
        text = f"{paper.title} {paper.summary} {' '.join(paper.categories)}"
        score = sum(1 for term in q_terms if term in text.lower())
        if score > 0:
            results.append((score, paper))
    if not results:
        return papers[:max_results]
    results.sort(key=lambda item: item[0], reverse=True)
    return [paper for _, paper in results][:max_results]


def cosine_similarity(
    vec1: Dict[str, float], vec2: Dict[str, float]
) -> float:
    if not vec1 or not vec2:
        return 0.0
    dot = sum(vec1.get(k, 0.0) * vec2.get(k, 0.0) for k in vec1)
    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


class Policy:
    ACCEPT_WEIGHT = 1.0
    LATER_WEIGHT = 0.5
    REJECT_WEIGHT = -0.3


class PaperRecommender:
    def __init__(self):
        self.papers: List[Paper] = []
        self.vectors: Dict[str, Dict[str, float]] = {}
        self.feedback: Dict[str, str] = {}
        self.reading_list: List[str] = []
        self.profile: Dict[str, float] = {}
        self.query_text: str = ""
        self.query_vector: Dict[str, float] = {}
        self.load_state()

    def load_state(self):
        if not os.path.exists(STATE_FILE):
            return
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            self.feedback = state.get("feedback", {})
            self.reading_list = state.get("reading_list", [])
            self.profile = {
                k: float(v) for k, v in state.get("profile", {}).items()
            }
        except Exception:
            pass

    def save_state(self):
        state = {
            "feedback": self.feedback,
            "reading_list": self.reading_list,
            "profile": self.profile,
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def set_query(self, query: str):
        self.query_text = query
        token_counts = Counter(tokenize(query))
        if not token_counts:
            self.query_vector = {}
            return
        norm = math.sqrt(sum(v * v for v in token_counts.values()))
        self.query_vector = {
            term: count / norm for term, count in token_counts.items()
        }

    def ingest(self, papers: List[Paper]):
        added_ids = {paper.paper_id for paper in self.papers}
        for paper in papers:
            if paper.paper_id not in added_ids:
                self.papers.append(paper)
        self.build_vectors()

    def build_vectors(self):
        self.vectors = {}
        for paper in self.papers:
            token_counts = Counter(tokenize(paper.text))
            if not token_counts:
                continue
            norm = math.sqrt(sum(v * v for v in token_counts.values()))
            self.vectors[paper.paper_id] = {
                term: count / norm for term, count in token_counts.items()
            }

    def update_profile(self, paper_id: str, action: str):
        paper = next(
            (p for p in self.papers if p.paper_id == paper_id), None
        )
        if paper is None or paper_id not in self.vectors:
            return
        self.feedback[paper_id] = action
        if action == "accepted":
            weight = Policy.ACCEPT_WEIGHT
        elif action == "later":
            weight = Policy.LATER_WEIGHT
        elif action == "rejected":
            weight = Policy.REJECT_WEIGHT
        else:
            return
        for term, value in self.vectors[paper_id].items():
            self.profile[term] = (
                self.profile.get(term, 0.0) + weight * value
            )
        if action == "later" and paper_id not in self.reading_list:
            self.reading_list.append(paper_id)
        self.save_state()

    def recommend(
        self, top_n: int = 10
    ) -> List[Tuple[Paper, float]]:
        candidates = []
        for paper in self.papers:
            if paper.paper_id in self.feedback:
                continue
            if paper.paper_id in self.reading_list:
                continue
            vector = self.vectors.get(paper.paper_id)
            if not vector:
                continue
            profile_score = cosine_similarity(self.profile, vector)
            query_score = cosine_similarity(self.query_vector, vector)
            recency = self._recency_boost(paper)
            if self.profile:
                score = (
                    profile_score * 0.6
                    + query_score * 0.3
                    + recency * 0.1
                )
            else:
                score = query_score * 0.7 + recency * 0.3
            candidates.append((paper, score))
        candidates.sort(key=lambda item: item[1], reverse=True)
        return candidates[:top_n]

    def _recency_boost(self, paper: Paper) -> float:
        try:
            dt = datetime.fromisoformat(
                paper.updated.replace("Z", "+00:00")
            )
        except ValueError:
            return 0.0
        now = datetime.now(timezone.utc)
        age = max((now - dt).days, 0)
        return 1.0 / (1.0 + age / 30.0)

    def get_paper_by_id(
        self, paper_id: str
    ) -> Optional[Paper]:
        return next(
            (p for p in self.papers if p.paper_id == paper_id),
            None,
        )

    def show_reading_list(self):
        if not self.reading_list:
            print("Your reading list is empty.")
            return
        print("Reading list:")
        for idx, paper_id in enumerate(self.reading_list, start=1):
            paper = self.get_paper_by_id(paper_id)
            title = paper.title if paper else paper_id
            print(f"{idx}. {title}")

    def show_feedback_summary(self):
        counts = Counter(self.feedback.values())
        print("Feedback summary:")
        print(f"  accepted: {counts['accepted']}")
        print(f"  later:    {counts['later']}")
        print(f"  rejected: {counts['rejected']}")


def display_paper(paper: Paper):
    print("\n=== Suggested paper ===")
    print(f"Title: {paper.title}")
    print(f"Authors: {', '.join(paper.authors)}")
    print(f"Categories: {', '.join(paper.categories)}")
    print(f"Updated: {paper.updated}")
    print(f"URL: {paper.url}")
    print("\nAbstract:")
    print(paper.summary)
    print("\nCommands: [y]es [n]o [s]ave for later [l]ist [p]rofile [q]uit")


def print_intro():
    print("===============================================")
    print("  PAPER RECOMMENDER v1.0")
    print("  A lightweight terminal tool for arXiv papers")
    print("===============================================")
    print("Enter a short search query, then respond to each suggestion.")
    print(
        "If you run this from an editor without arguments, you can type your query now."
    )
    print(
        "\nExample: machine learning, quantum computing, graph neural networks"
    )
    print("-----------------------------------------------")


def run_web_query(query: str):
    recommender = PaperRecommender()
    papers = load_paper_database()
    recommender.ingest(papers)
    recommender.set_query(query)

    results = recommender.recommend(top_n=3)
    for paper, score in results:
        print("=" * 40)
        print(paper.title)
        print(", ".join(paper.authors))
        print(paper.url)
        print(f"score: {score:.3f}")


def main():
    print_intro()
    args = sys.argv[1:]
    use_local = False
    if "--local" in args:
        use_local = True
        args = [arg for arg in args if arg != "--local"]

    if not args:
        search_query = input("Search query: ").strip()
        if not search_query:
            print("No query entered. Exiting.")
            return
    else:
        search_query = " ".join(args)

    print("Using live Crossref data by default.")
    recommender = PaperRecommender()
    if use_local:
        print("Local mode enabled: loading local paper database.")
        papers = load_paper_database()
        print(f"Loaded {len(papers)} papers from local database.")
    else:
        print("Fetching live papers from Crossref...")
        try:
            papers = fetch_live_papers(search_query, max_results=30)
            print(f"Loaded {len(papers)} papers from Crossref.")
        except Exception as exc:
            print(f"Failed to fetch live papers: {exc}")
            print("Falling back to local paper database.")
            papers = load_paper_database()
            print(f"Loaded {len(papers)} papers from local database.")
    recommender.ingest(papers)
    recommender.set_query(search_query)
    print(f"Prepared recommender for query: {search_query}")

    while True:
        suggestions = recommender.recommend(top_n=1)
        if not suggestions:
            print("No more suggestions available.")
            break
        paper, score = suggestions[0]
        display_paper(paper)
        answer = input("Your choice: ").strip().lower()
        if answer in {"y", "yes"}:
            recommender.update_profile(paper.paper_id, "accepted")
            print("Marked accepted.")
        elif answer in {"n", "no"}:
            recommender.update_profile(paper.paper_id, "rejected")
            print("Marked rejected.")
        elif answer in {"s", "save", "later"}:
            recommender.update_profile(paper.paper_id, "later")
            print("Saved for later.")
        elif answer in {"l", "list"}:
            recommender.show_reading_list()
            continue
        elif answer in {"p", "profile"}:
            recommender.show_feedback_summary()
            continue
        elif answer in {"q", "quit", "exit"}:
            print("Goodbye.")
            break
        else:
            print("Unknown command. Use y/n/s/l/p/q.")
            continue

    print("Session finished.")


if __name__ == "__main__":
    main()
