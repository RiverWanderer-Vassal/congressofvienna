#!/usr/bin/env python3
"""Fixes applied to dist/buildFile.xml for 2.0.0a60. Run from the repository root:
    python3 tools/build/a60_fixes.py
Each fix edits the raw XML text in place and is safe to run once on the a59 buildFile."""
import re, sys

BF = 'dist/buildFile.xml'


def attr(expr: str) -> str:
    return expr.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def report_issue_link(raw: str) -> str:
    """#1 Help > Report an Issue opened a plain issue on vassalengine/modules with an assignee and the
    label ABR. It now opens this repository's bug form with the environment and game state filled in."""
    E = 'java.net.URLEncoder.encode'
    def q(name, expr): return '"&' + name + '=" + ' + E + '(' + expr + ', "UTF-8")'
    env = ('"Module " + ModuleVersion + "\\n" + "VASSAL " + VassalVersionRunning + "\\n" + '
           '"Java " + java.lang.System.getProperty("java.version") + " (" + java.lang.System.getProperty("java.vendor") + ")\\n" + '
           '"OS " + java.lang.System.getProperty("os.name") + " " + java.lang.System.getProperty("os.version") + " " + java.lang.System.getProperty("os.arch") + "\\n" + '
           '"Max heap " + (java.lang.Runtime.getRuntime().maxMemory() / 1048576) + " MB"')
    scen = ('Scenario + "\\n" + "Variant: " + Variant + "\\n" + "Players: " + PlayersOption + "\\n" + '
            '"Edition: " + Edition + "\\n" + "French bot: " + isFRbot + "; open hands: " + OpenHandsOption + "\\n" + '
            '"Initial Situation cards: " + ISCmode + "; Handicap cards: " + HCmode')
    phase = ('(Phase == Setup ? "Setup" : Phase == Start ? "Start" : Phase == Initial ? "Initial" : '
             'Phase == InitialSC ? "Initial Situation card" : (Phase >= EnvPhase1 && Phase <= EnvPhase3) ? "Environment" : '
             'Phase == InitialHC ? "Initial Handicap cards" : Phase == HC09 ? "Handicap card HC-9" : Phase == Deal ? "Deal" : '
             'Phase == Wager ? "Wager" : Phase == WagerIssue ? "Wager winner places issue" : Phase == PlaceIssues ? "Place issues" : '
             '(Phase >= Conference && Phase < War) ? "Conference" : Phase >= War ? "War" : "other") + " (" + Phase + ")"')
    state = ('"Game started: " + GameStarted + "\\n" + "Turn: " + Turn + " of " + MaxTurn + "\\n" + "Phase: " + ' + phase + ' + "\\n" + '
             '"Conference round: " + Round + "\\n" + "Step: " + sopStep + "\\n" + "Side on turn: " + OnTurn + "\\n" + '
             '"Card draw power: " + DrawPower + "\\n" + "Active front: " + ActiveFront + "\\n" + '
             '"War state: " + WarState + " (0 limited, 1 armistice, 2 total war)\\n" + '
             '"Napoleon active: " + NapoleonActive + "; Grande Armée in Paris: " + GA_InParis + "\\n" + '
             '"Player side: " + PlayerSide')
    label = '(ModuleVersion =~ ".*[bB]eta.*" ? "bug,beta" : ModuleVersion =~ ".*[0-9-]a[0-9].*" ? "bug,alpha" : "bug")'
    expr = ('{"https://github.com/RiverWanderer-Vassal/congressofvienna/issues/new?template=bug_report.yml" + '
            + q('labels', label) + ' + ' + q('title', '"[" + ModuleVersion + "] "') + ' + '
            + q('version', env) + ' + ' + q('scenario', scen) + ' + ' + q('state', state) + '}')
    m = re.search(r'<VASSAL\.build\.module\.documentation\.BrowserHelpFile startingPage="([^"]*)" title="Report an Issue[^"]*"/>', raw)
    assert m, 'Report an Issue link not found'
    return raw[:m.start(1)] + attr(expr) + raw[m.end(1):]


FIXES = [report_issue_link]

if __name__ == '__main__':
    raw = open(BF, encoding='utf-8').read()
    for f in FIXES:
        raw = f(raw)
        print('applied', f.__name__)
    open(BF, 'w', encoding='utf-8').write(raw)
