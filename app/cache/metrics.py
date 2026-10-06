from prometheus_client import Counter

cache_hits = Counter(
    "cache_hits",
    "Total number of prediction cache hits",
)

cache_misses = Counter(
    "cache_misses",
    "Total number of prediction cache misses",
)

model_inferences = Counter(
    "model_inferences",
    "Total number of model inference runs",
)
