import hashlib

def compute_post_hash(post_date: str, content: str) -> str:
  return hashlib.sha256(f"{post_date}{content}".encode('utf-8')).hexdigest()
