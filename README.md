# Congress of Vienna – VASSAL module

VASSAL module for *Congress of Vienna* (GMT Games), v2 development series.

* `dist/` – the unpacked module (buildFile.xml, moduledata, images, sounds, help files).
* `pom.xml` – Maven build; `./mvnw package` (or `mvnw.cmd package` on Windows) zips `dist/` into `target/CongressOfVienna-<version>.vmod`.
* Edit the module in the VASSAL editor, then unzip the saved `.vmod` over `dist/` and commit.

## History

Earlier builds were recovered from the maintainers' archives and committed in order, with their original save dates.

| Version | Line | VASSAL | Saved | Notes |
|---|---|---|---|---|
| Playtest v51.3 | V1 | 3.6.9 | 2023-02-26 | Original playtest module (Toppen & Esparrago) |
| 1.0 ("V61 6") | V1 | 3.7.16 | 2025-05-13 | Enhanced by Mark Benson; released on the library as 1.0.6 |
| 1.0.0 | V1 | 3.7.16 | 2025-05-18 | Further V1 enhancements |
| 0.3.5-MB | V2 | 3.7.16 | 2025-05-21 | Start of the V2 rewrite |
| 0.3.48 | V2 | 3.7.16 | 2025-07-24 | |
| 2.0.0a32 | V2 | 3.7.18 | 2025-10-10 | |
| 2.0.0a57 | V2 | 3.7.22 | 2026-05-14 | |
| 2.0.0a58 | V2 | 3.7.29 | 2026-10-06 | |
| 2.0.0a59 | V2 | 3.7.29 | 2026-11-01 | |

V1 library releases 1.0.3–1.0.5 and 1.0.7–1.0.8 were made by other contributors and are available from the
[VASSAL module library](https://vassalengine.org/library/projects/Congress_of_Vienna); they are not in this history.

## Contributing

`main` is protected: it can't be deleted or force-pushed, and changes from collaborators arrive by pull request
(no approval needed, so you can merge your own). Nothing merged is ever lost, so any change can be reverted.

`buildFile.xml` is one large file that VASSAL rewrites on every save, so two people editing the module at the
same time will produce changes that can't sensibly be merged. To avoid that:

1. **Claim it.** Say on the CoV Discord that you're editing the module, and say when you're done.
2. **Start from the latest.** `git pull` on `main`, then build or open that version in the VASSAL editor.
3. **Work on a branch.** `git switch -c my-change`, make your edits, save the `.vmod`.
4. **Unpack over `dist/`.** Unzip the saved `.vmod` over `dist/` (delete `dist/` first so removed files go too;
   don't commit `__MACOSX/`).
5. **Commit and open a pull request.** Describe the change and any issue it fixes (`Fixes #12`), then merge it
   promptly so the next person starts from it.

Bump the module version in the VASSAL editor (Module properties) and in `pom.xml` when you make a release.

## Bugs and requests

Report issues in this repository's Issues tab. Older reports are on
[vassalengine/modules](https://github.com/vassalengine/modules/issues?q=label%3A%22Congress+of+Vienna%22).

## Credits

Game design by **Frank Esparrago**, system design by **Mark Herman**, graphics by **Terry Leeds**, published by **GMT Games LLC**.
Original VASSAL module by **Joel Toppen & Frank Esparrago**; V2 by **Fredrik Lindner & Mark Benson**.
See [CREDITS.md](CREDITS.md) for everyone who has worked on the module.

## Copyright, permission and licence

**Game content.** The game, its rules, map, card and box artwork and other graphics are © GMT Games LLC
and/or the original game artists. They are included in this module **by permission of GMT Games LLC**, as
stated in the module's own credits. GMT's published terms for VASSAL and other electronic modules
([GMT Games FAQ](https://www.gmtgames.com/t-faq.aspx), "What are the requirements for using/playing
electronic versions of GMT Games?") are:

> In order to legally use these files to play a game, at least one of the players must own a copy of the
> game upon which that module or files are based.

All rights, copyrights and trademarks in the game remain with GMT Games LLC and/or the original artists, and
the materials may not be used commercially without GMT's express permission. Buy the game at
[gmtgames.com](https://www.gmtgames.com/p-1167-congress-of-vienna-2nd-printing.aspx).

The original module was created with the game's designer, Frank Esparrago, who is credited as a co-author of
V1 (see [CREDITS.md](CREDITS.md)).

**Module code.** The module authors have not published a separate licence. In its absence, the module's
own work (its structure, buildFile.xml, scripting and VASSAL configuration) is offered under the same licence
as the VASSAL engine it runs on: the **GNU Lesser General Public License v2.1** (see [LICENSE](LICENSE) and
[VASSAL's licence](https://github.com/vassalengine/vassal/blob/master/LICENSE)). This does not grant any
rights in GMT Games' copyrighted content.
