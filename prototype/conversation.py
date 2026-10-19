"""Independent, provider-free conversation lifecycle contract.

This is a local deterministic test fixture, NOT a live speech/video/AI provider.
It never calls third-party services, sends messages, stores audio or executes tools.
All media channels are metadata-only until explicitly integrated and verified.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from uuid import uuid4

CHANNELS = frozenset({"chat", "voice", "video"})
STATES = frozenset({"CREATED", "ACTIVE", "INTERRUPTED", "CLOSED"})
MAX_SOURCE_BYTES = 100_000
MAX_QUESTION_CHARS = 4_000


class ConversationError(ValueError):
    """Invalid transition or rejected input."""


@dataclass(frozen=True)
class TurnResult:
    request_id: str
    answer: str
    source_ids: tuple[str, ...]
    abstained: bool
    channel: str
    language: str


def _tokens(value: str) -> set[str]:
    """Unicode-aware lexical matching; not a translation or semantic model."""
    return {term for term in re.findall(r"\w+", value.casefold()) if len(term) >= 3}


class ConversationSession:
    """Single-tenant, consent-gated, source-bounded mock conversation session."""

    def __init__(
        self, workspace_id: str, agent_id: str, channel: str = "chat",
        language: str = "en", *, keep_transcript: bool = False,
        max_turns: int = 25,
    ):
        if not workspace_id or not agent_id:
            raise ConversationError("workspace and agent are required")
        if channel not in CHANNELS:
            raise ConversationError("unsupported channel")
        if not isinstance(max_turns, int) or not 1 <= max_turns <= 100:
            raise ConversationError("max_turns must be between 1 and 100")
        self.id = "conv_" + uuid4().hex
        self.workspace_id = workspace_id
        self.agent_id = agent_id
        self.channel = channel
        self.language = language
        self.max_turns = max_turns
        self.keep_transcript = keep_transcript
        self.state = "CREATED"
        self._consented = False
        self._sources: dict[str, str] = {}
        self._turns: dict[str, TurnResult] = {}
        self._request_hashes: dict[str, str] = {}
        self._transcript: list[dict[str, str]] = []
        self.events: list[dict[str, str]] = []

    def _authorize(self, workspace_id: str) -> None:
        if workspace_id != self.workspace_id:
            raise PermissionError("cross-workspace session access denied")

    def start(self, *, workspace_id: str, consent: bool, transcript_consent: bool = False) -> None:
        self._authorize(workspace_id)
        if self.state != "CREATED":
            raise ConversationError("session already started")
        if consent is not True:
            raise PermissionError("explicit conversation consent required")
        if self.keep_transcript and transcript_consent is not True:
            raise PermissionError("separate transcript retention consent required")
        self._consented = True
        self.state = "ACTIVE"
        self.events.append({"type": "session.started", "channel": self.channel})

    def attach_sources(self, *, workspace_id: str, sources: dict[str, str]) -> None:
        self._authorize(workspace_id)
        if self.state != "ACTIVE":
            raise ConversationError("cannot attach sources in this state")
        if not isinstance(sources, dict) or not sources:
            raise ConversationError("nonempty source mapping required")
        for key, value in sources.items():
            if not isinstance(key, str) or not key.strip() or not isinstance(value, str):
                raise ConversationError("invalid source")
            if len(value.encode("utf-8")) > MAX_SOURCE_BYTES:
                raise ConversationError("source exceeds test-harness bound")
        self._sources.update(sources)
        self.events.append({"type": "knowledge.attached", "count": str(len(sources))})

    def ask(self, *, workspace_id: str, request_id: str, question: str) -> TurnResult:
        self._authorize(workspace_id)
        if self.state != "ACTIVE":
            raise ConversationError("session is not active")
        if not isinstance(request_id, str) or not request_id.strip():
            raise ConversationError("request_id required")
        if not isinstance(question, str) or not 0 < len(question.strip()) <= MAX_QUESTION_CHARS:
            raise ConversationError("invalid question")
        qhash = hashlib.sha256(question.encode("utf-8")).hexdigest()
        if request_id in self._turns:
            if self._request_hashes[request_id] != qhash:
                raise ConversationError("idempotency key reused with different content")
            return self._turns[request_id]  # retry is free and exactly-once in memory
        if len(self._turns) >= self.max_turns:
            raise ConversationError("session turn limit reached")
        q_tokens = _tokens(question)
        matches = []
        for source_id, source_text in self._sources.items():
            overlap = len(q_tokens & _tokens(source_text))
            if overlap:
                matches.append((overlap, source_id, source_text))
        matches.sort(key=lambda item: (-item[0], item[1]))
        if matches:
            _, source_id, excerpt = matches[0]
            # EXTRACTIVE ONLY: source content is untrusted text, never an instruction.
            answer = "Source [" + source_id + "]: " + excerpt[:240]
            ids = (source_id,)
            abstained = False
        else:
            answer = "I do not have a supporting source for that question."
            ids = ()
            abstained = True
        result = TurnResult(request_id, answer, ids, abstained, self.channel, self.language)
        self._turns[request_id] = result
        self._request_hashes[request_id] = qhash
        self.events.append({"type": "turn.completed", "abstained": str(abstained).lower()})
        if self.keep_transcript:
            self._transcript.append({"question": question, "answer": answer})
        return result

    def interrupt(self, *, workspace_id: str) -> None:
        self._authorize(workspace_id)
        if self.state != "ACTIVE":
            raise ConversationError("can interrupt only active sessions")
        self.state = "INTERRUPTED"
        self.events.append({"type": "session.interrupted"})

    def resume(self, *, workspace_id: str) -> None:
        self._authorize(workspace_id)
        if self.state != "INTERRUPTED":
            raise ConversationError("can resume only interrupted sessions")
        self.state = "ACTIVE"
        self.events.append({"type": "session.resumed"})

    def propose_action(self, *, workspace_id: str, intent: str) -> dict[str, str]:
        self._authorize(workspace_id)
        if self.state != "ACTIVE":
            raise ConversationError("session is not active")
        if not isinstance(intent, str) or not intent.strip():
            raise ConversationError("intent required")
        # Deliberately does NOT execute side effects or auto-approve them.
        self.events.append({"type": "action.approval_required"})
        return {"status": "APPROVAL_REQUIRED", "intent": intent}

    def transcript(self, *, workspace_id: str) -> tuple[dict[str, str], ...]:
        self._authorize(workspace_id)
        if not self.keep_transcript:
            raise PermissionError("transcription persistence was not consented to")
        return tuple(dict(item) for item in self._transcript)

    def close(self, *, workspace_id: str) -> None:
        self._authorize(workspace_id)
        if self.state not in {"ACTIVE", "INTERRUPTED"}:
            raise ConversationError("session cannot close in current state")
        self.state = "CLOSED"
        self.events.append({"type": "session.closed"})
