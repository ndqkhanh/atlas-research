"""Atlas-Research brand — Map-blue + parchment, compass-rose logo."""
from __future__ import annotations

from harness_tui.theme import Theme
from harness_tui.themes import catppuccin_mocha

ATLAS_LOGO = r"""
                    [bold #1B4965]N[/]
                    [bold #1B4965]│[/]
       [dim]NW[/]      [bold #1B4965]│[/]      [dim]NE[/]
            [bold #1B4965]╲[/]   [bold #1B4965]│[/]   [bold #1B4965]╱[/]
              [bold #1B4965]╲[/] [bold #FAF3DD]│[/] [bold #1B4965]╱[/]
   [bold #FAF3DD]W[/] ──────[bold #1B4965]✦[/]──────  [bold #FAF3DD]E[/]
              [bold #1B4965]╱[/] [bold #FAF3DD]│[/] [bold #1B4965]╲[/]
            [bold #1B4965]╱[/]   [bold #1B4965]│[/]   [bold #1B4965]╲[/]
       [dim]SW[/]      [bold #1B4965]│[/]      [dim]SE[/]
                    [bold #1B4965]│[/]
                    [bold #1B4965]S[/]

   [bold]ATLAS-RESEARCH[/]  [dim]· long-horizon research[/]
""".strip("\n")


def atlas_theme() -> Theme:
    return catppuccin_mocha().with_brand(
        name="atlas-research",
        primary="#5B8FB9",
        primary_alt="#1B4965",
        accent="#FAF3DD",
        ascii_logo=ATLAS_LOGO,
        spinner_frames=("◐", "◓", "◑", "◒"),
    )
