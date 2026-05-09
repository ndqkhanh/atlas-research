"""Atlas-Research TUI — long-horizon research agent."""
from __future__ import annotations

import os
from typing import Optional

import click
from harness_tui import HarnessApp, ProjectConfig
from harness_tui.commands.registry import register_command
from harness_tui.transport import HTTPTransport, MockTransport

from .tui_theme import atlas_theme
from .widgets import CitationsPanel


@register_command(name="cite", description="Show citations for the current report",
                  category="Atlas")
async def cmd_cite(app, _: str) -> None:  # type: ignore[no-untyped-def]
    app.shell.chat_log.write_system(
        "(citations panel: live citation list with source domains and cached snippets)"
    )


@register_command(name="recite", description="Force re-attribution of a claim",
                  category="Atlas")
async def cmd_recite(app, args: str) -> None:  # type: ignore[no-untyped-def]
    if not args.strip():
        app.shell.chat_log.write_system("usage: /recite <claim>")
        return
    app.shell.chat_log.write_system(f"re-attributing claim: {args.strip()!r}")


@register_command(name="queue", description="Manage the planner reading queue",
                  category="Atlas")
async def cmd_queue(app, args: str) -> None:  # type: ignore[no-untyped-def]
    if args.startswith("add "):
        url = args[4:].strip()
        app.shell.chat_log.write_system(f"queued for fetch: {url}")
    else:
        app.shell.chat_log.write_system("(reading queue is empty)")


@register_command(name="synth", description="Force synthesizer step on current notes",
                  category="Atlas")
async def cmd_synth(app, _: str) -> None:  # type: ignore[no-untyped-def]
    app.shell.chat_log.write_system("synthesizer: triggered (mock)")


@click.command()
@click.option("--url", default=None)
@click.option("--mock", is_flag=True)
@click.option("--depth", type=int, default=3, help="Research depth.")
@click.option("--theme", default=None)
@click.option("--serve", is_flag=True,
              help="Run the TUI in a browser via textual-serve.")
@click.option("--port", type=int, default=8002,
              help="Web mode port (with --serve).")
@click.option("--host", default="127.0.0.1",
              help="Web mode host (with --serve).")
def main(url: Optional[str], mock: bool, depth: int, theme: Optional[str], serve: bool, port: int, host: str) -> None:
    """Open the Atlas-Research TUI."""
    if serve:
        from harness_tui.serve import serve_app, make_module_command

        flags = []
        if mock:
            flags.append("--mock")
        if url:
            flags.append(f"--url {url}")
        serve_app(
            command=make_module_command("atlas_research.tui", " ".join(flags)),
            host=host, port=port,
            title="atlas-research",
        )
        return
    if mock:
        transport = MockTransport()
    else:
        backend = url or os.environ.get("ATLAS_BACKEND") or "http://localhost:8002"
        transport = HTTPTransport(
            backend,
            endpoints={"run": "/v1/reports", "plan": "/v1/reports"},
            payload_builder=lambda t, m: {"query": t, "depth": depth},
            text_field="report",
        )
    cfg = ProjectConfig(
        name="atlas-research",
        description="Long-horizon research agent",
        theme=atlas_theme(),
        transport=transport,
        model=os.environ.get("ATLAS_MODEL", "auto"),
        sidebar_tabs=[("Citations", CitationsPanel())],
    )
    app = HarnessApp(cfg)
    app.run()
    summary = getattr(app, "last_exit_summary", None)
    if summary:
        click.echo(summary.render())


if __name__ == "__main__":  # pragma: no cover
    main()
