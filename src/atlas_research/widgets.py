"""Atlas-Research project widgets — citations panel for the sidebar.

Differentiator: cited sources are first-class. Each claim in the report
is anchored to one or more sources; the panel surfaces those sources
with domain + title + cached snippet so the user can audit faithfulness
before publishing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from rich.panel import Panel
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import ListItem, ListView, Static


@dataclass
class Citation:
    domain: str
    title: str
    url: str = ""
    snippet: str = ""
    supports: List[str] = field(default_factory=list)  # claim ids


_DEMO_CITATIONS: List[Citation] = [
    Citation(
        domain="anthropic.com",
        title="Claude Code permission modes",
        url="https://code.claude.com/docs/en/permission-modes",
        snippet="Plan mode is read-only; Auto-Accept skips edit prompts but…",
        supports=["c1", "c4"],
    ),
    Citation(
        domain="github.com/charmbracelet",
        title="Crush — TUI architecture and AppModel",
        snippet="Single UI struct, three state buckets (app, focus, layout)…",
        supports=["c2"],
    ),
    Citation(
        domain="hermes-agent.nousresearch.com",
        title="Hermes Agent TUI · ToolTrail and StreamingMd",
        snippet="ScrollBox + useVirtualHistory virtualizes the chat viewport…",
        supports=["c3", "c5"],
    ),
    Citation(
        domain="textual.textualize.io",
        title="Textual — Posting + Elia production proofs",
        snippet="Posting (HTTP client) and Elia (multi-LLM chat) prove the pattern…",
        supports=["c1", "c5"],
    ),
]


class CitationsPanel(Vertical):
    """A scrollable list of citations with a detail card below."""

    DEFAULT_CSS = """
    CitationsPanel {
        height: 1fr;
    }
    CitationsPanel ListView {
        height: 50%;
        background: $bg;
    }
    CitationsPanel #detail {
        height: 1fr;
        padding: 1;
        background: $bg_alt;
        color: $fg_muted;
    }
    """

    def __init__(self, citations: List[Citation] | None = None) -> None:
        super().__init__()
        self.citations = list(citations) if citations is not None else list(_DEMO_CITATIONS)

    def compose(self) -> ComposeResult:
        items = []
        for i, c in enumerate(self.citations):
            line = Text()
            line.append("▸ ", style="dim")
            line.append(c.domain, style="bold cyan")
            line.append("  ")
            line.append(c.title[:30], style="bold")
            items.append(ListItem(Static(line), id=f"cit-{i}"))
        yield ListView(*items, id="cit-list")
        yield Static(self._detail(0), id="detail")

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item is None:
            return
        idx = int((event.item.id or "cit-0")[4:])
        self.query_one("#detail", Static).update(self._detail(idx))

    def _detail(self, idx: int) -> Panel:
        if not self.citations:
            return Panel(Text("(no citations yet)", style="dim"), border_style="dim")
        c = self.citations[idx]
        body = Text()
        body.append(c.title, style="bold")
        body.append("\n")
        body.append(c.domain, style="cyan")
        if c.url:
            body.append("  ")
            body.append(c.url, style="dim underline")
        body.append("\n\n")
        body.append(c.snippet, style="default")
        if c.supports:
            body.append("\n\nsupports: ", style="dim")
            body.append(", ".join(c.supports), style="bold green")
        return Panel(body, title="[bold]source[/]", title_align="left", border_style="cyan")

    def add_citation(self, citation: Citation) -> None:
        """Append a citation at runtime (e.g. from a transport event)."""
        self.citations.append(citation)
        try:
            lv: ListView = self.query_one("#cit-list", ListView)
            i = len(self.citations) - 1
            line = Text()
            line.append("▸ ", style="dim")
            line.append(citation.domain, style="bold cyan")
            line.append("  ")
            line.append(citation.title[:30], style="bold")
            lv.append(ListItem(Static(line), id=f"cit-{i}"))
        except Exception:
            pass
