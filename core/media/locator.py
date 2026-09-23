"""Resolve media asset identifiers to verified original or proxy paths."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from ..errors import MyProError
from ..identity import ContentHash, hash_file

class UnresolvedMedia(MyProError):
    def __init__(self, asset_id: str, attempted: list[str]) -> None:
        super().__init__(f"cannot resolve {asset_id}; attempted: {', '.join(attempted) or 'none'}")
        self.asset_id = asset_id
        self.attempted = attempted

class MediaHashMismatch(MyProError):
    def __init__(self, asset_id: str, expected: ContentHash, actual: ContentHash) -> None:
        super().__init__(f"{asset_id}: expected {expected}, got {actual}")
        self.asset_id = asset_id
        self.expected = expected
        self.actual = actual

@dataclass(frozen=True, slots=True)
class ResolvedMedia:
    asset_id: str
    path: Path
    is_proxy: bool
    hash_verified: bool

class MediaLocator:
    def __init__(self, *, proxies_dir: Path | None = None, allow_proxy_fallback: bool = True) -> None:
        self._originals: dict[str, Path] = {}
        self._proxies: dict[str, Path] = {}
        self._expected_hash: dict[str, ContentHash] = {}
        self.proxies_dir = proxies_dir
        self.allow_proxy_fallback = allow_proxy_fallback

    def register(self, asset_id: str, path: Path, *, expected_hash: ContentHash | None = None) -> None:
        self._originals[asset_id] = Path(path)
        if expected_hash is not None:
            self._expected_hash[asset_id] = expected_hash

    def register_proxy(self, asset_id: str, path: Path) -> None:
        self._proxies[asset_id] = Path(path)

    def resolve(self, asset_id: str, *, verify_hash: bool = False,
                prefer_proxy: bool = False) -> ResolvedMedia:
        attempts: list[str] = []

        def attempt(path: Path, is_proxy: bool) -> ResolvedMedia | None:
            attempts.append(str(path))
            if not path.is_file():
                return None
            if verify_hash and asset_id in self._expected_hash and not is_proxy:
                actual = hash_file(path)
                expected = self._expected_hash[asset_id]
                if actual != expected:
                    raise MediaHashMismatch(asset_id, expected, actual)
                return ResolvedMedia(asset_id, path, False, True)
            return ResolvedMedia(asset_id, path, is_proxy, verify_hash and not is_proxy)

        candidates: list[tuple[Path, bool]] = []
        if prefer_proxy and asset_id in self._proxies:
            candidates.append((self._proxies[asset_id], True))
        if asset_id in self._originals:
            candidates.append((self._originals[asset_id], False))
        if not prefer_proxy and self.allow_proxy_fallback and asset_id in self._proxies:
            candidates.append((self._proxies[asset_id], True))

        for path, is_proxy in candidates:
            resolved = attempt(path, is_proxy)
            if resolved is not None:
                return resolved
        raise UnresolvedMedia(asset_id, attempts)

    def unresolved(self) -> list[str]:
        result = []
        for asset_id in self._originals:
            try:
                self.resolve(asset_id)
            except UnresolvedMedia:
                result.append(asset_id)
        return result

    def as_dict(self) -> dict[str, object]:
        return {
            "originals": {k: str(v) for k, v in self._originals.items()},
            "proxies": {k: str(v) for k, v in self._proxies.items()},
            "expected_hash": {k: str(v) for k, v in self._expected_hash.items()},
            "allow_proxy_fallback": self.allow_proxy_fallback,
        }
