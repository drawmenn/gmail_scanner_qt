from __future__ import annotations

from dataclasses import dataclass
import itertools
import re
import unicodedata


FALLBACK_CHAR_POOL = "aeiourstlnmcd"
COMMON_FILLERS = (
    "x",
    "y",
    "z",
    "r",
    "n",
    "s",
    "o",
    "a",
    "io",
    "ly",
    "go",
    "on",
    "er",
    "it",
    "me",
    "up",
    "ai",
    "ox",
    "lab",
    "hub",
    "box",
    "cat",
    "fox",
    "zen",
    "jet",
    "max",
    "pro",
    "sky",
    "bit",
    "nova",
    "byte",
    "zone",
    "nest",
    "link",
    "wave",
    "mint",
    "grid",
    "flow",
    "base",
    "spark",
    "shift",
    "scope",
    "prime",
)
DIGIT_FILLERS = (
    "1",
    "7",
    "8",
    "9",
    "01",
    "07",
    "08",
    "11",
    "21",
    "88",
    "99",
    "007",
    "101",
    "365",
    "777",
    "888",
)


@dataclass(frozen=True)
class GeneratorOptions:
    source_text: str
    target_length: int = 6
    allow_digits: bool = False
    max_results: int = 80


def generate_candidates(options: GeneratorOptions) -> list[str]:
    target_length = max(6, min(30, int(options.target_length)))
    max_results = max(10, min(500, int(options.max_results)))

    source_terms = _extract_terms(options.source_text)
    if not source_terms:
        return []

    base_fragments = _build_base_fragments(source_terms, target_length)
    char_pool = _build_char_pool(source_terms, options.allow_digits)
    fill_cache: dict[tuple[int, bool], list[str]] = {}
    candidates: dict[str, int] = {}

    def remember(raw: str, bonus: int = 0) -> None:
        candidate = _normalize_candidate(raw)
        if len(candidate) != target_length:
            return
        score = _score_candidate(candidate, source_terms) + bonus
        existing = candidates.get(candidate)
        if existing is None or score > existing:
            candidates[candidate] = score

    for fragment in base_fragments:
        if len(fragment) >= target_length:
            remember(fragment[:target_length], 26)
            remember(fragment[-target_length:], 18)
            continue

        remainder = target_length - len(fragment)
        fillers = _get_fillers(remainder, char_pool, options.allow_digits, fill_cache)
        for suffix in fillers:
            remember(fragment + suffix, 20)
        for prefix in fillers:
            remember(prefix + fragment, 12)

        if remainder >= 2:
            left_size = min(2, remainder - 1)
            left_fillers = _get_fillers(left_size, char_pool, options.allow_digits, fill_cache)
            right_fillers = _get_fillers(remainder - left_size, char_pool, options.allow_digits, fill_cache)
            for left in left_fillers[:12]:
                for right in right_fillers[:12]:
                    remember(left + fragment + right, 10)

    if len(source_terms) >= 2:
        combined = "".join(source_terms)
        remember(combined[:target_length], 30)
        initials = "".join(term[0] for term in source_terms if term)
        if initials:
            remainder = target_length - len(initials)
            for filler in _get_fillers(remainder, char_pool, options.allow_digits, fill_cache):
                remember(initials + filler, 24)
                remember(filler + initials, 14)

    ordered = sorted(candidates.items(), key=lambda item: (-item[1], item[0]))
    return [name for name, _score in ordered[:max_results]]


def _extract_terms(source_text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", source_text or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    tokens = re.findall(r"[a-z0-9]+", ascii_text)

    deduped: list[str] = []
    for token in tokens:
        if token and token not in deduped:
            deduped.append(token)
    return deduped


def _build_base_fragments(source_terms: list[str], target_length: int) -> list[str]:
    fragments: list[str] = []

    def push(value: str) -> None:
        cleaned = _normalize_candidate(value)
        if len(cleaned) >= 2 and cleaned not in fragments:
            fragments.append(cleaned)

    combined = "".join(source_terms)
    if combined:
        push(combined[:target_length])

    for term in source_terms:
        push(term)
        push(term[: min(len(term), target_length)])
        if len(term) >= 3:
            push(term[:3])
            push(term[-3:])
        if len(term) >= 4:
            push(term[:4])
            push(term[-4:])

        compact = term[0] + "".join(ch for ch in term[1:] if ch not in "aeiou")
        if len(compact) >= 3:
            push(compact)

    if len(source_terms) >= 2:
        first, second = source_terms[0], source_terms[1]
        push(first + second)
        push(first[:3] + second[:3])
        push(first[0] + second)
        push(first + second[0])
        push("".join(term[0] for term in source_terms if term))

    return fragments


def _build_char_pool(source_terms: list[str], allow_digits: bool) -> list[str]:
    pool: list[str] = []
    for char in "".join(source_terms) + FALLBACK_CHAR_POOL:
        if char.isdigit() and not allow_digits:
            continue
        if char not in pool:
            pool.append(char)
    return pool or list(FALLBACK_CHAR_POOL)


def _get_fillers(
    length: int,
    char_pool: list[str],
    allow_digits: bool,
    cache: dict[tuple[int, bool], list[str]],
) -> list[str]:
    cache_key = (length, allow_digits)
    if cache_key in cache:
        return cache[cache_key]

    if length <= 0:
        cache[cache_key] = [""]
        return cache[cache_key]

    tokens = list(COMMON_FILLERS)
    if allow_digits:
        tokens.extend(DIGIT_FILLERS)

    for char in char_pool[:8]:
        if char not in tokens:
            tokens.append(char)

    for left in char_pool[:5]:
        for right in char_pool[:5]:
            token = f"{left}{right}"
            if token not in tokens:
                tokens.append(token)

    results: list[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        if value not in seen and len(value) == length:
            seen.add(value)
            results.append(value)

    for token in tokens:
        add(token)

    if length <= 3:
        letters = char_pool[:6]
        for combo in itertools.product(letters, repeat=length):
            add("".join(combo))
            if len(results) >= 80:
                break

    if length > 1 and len(results) < 120:
        for split in range(1, length):
            left_items = _get_fillers(split, char_pool, allow_digits, cache)
            right_items = _get_fillers(length - split, char_pool, allow_digits, cache)
            for left in left_items[:12]:
                for right in right_items[:12]:
                    add(left + right)
                    if len(results) >= 120:
                        break
                if len(results) >= 120:
                    break
            if len(results) >= 120:
                break

    cache[cache_key] = results or [("x" * length)[:length]]
    return cache[cache_key]


def _normalize_candidate(value: str) -> str:
    return "".join(ch for ch in (value or "").lower() if ch.isalnum())


def _score_candidate(candidate: str, source_terms: list[str]) -> int:
    score = 100

    digit_count = sum(ch.isdigit() for ch in candidate)
    score -= digit_count * 7

    for term in source_terms:
        if term in candidate:
            score += min(20, len(term) * 3)
        elif candidate.startswith(term[: min(3, len(term))]):
            score += 9

    if candidate[0].isdigit():
        score -= 20
    if re.search(r"(.)\1\1", candidate):
        score -= 16
    if re.search(r"[0-9]{3,}$", candidate):
        score -= 8

    vowel_count = sum(ch in "aeiou" for ch in candidate)
    consonant_count = len(candidate) - digit_count - vowel_count
    if vowel_count == 0 or consonant_count == 0:
        score -= 10
    elif abs(vowel_count - consonant_count) <= 2:
        score += 8

    if candidate == "".join(sorted(candidate)):
        score -= 4

    return score
