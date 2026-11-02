#!/usr/bin/env python3
"""Fixes applied to dist/buildFile.xml for 2.0.0a60. Run from the repository root:
    python3 tools/build/a60_fixes.py
Each fix edits the raw XML text in place. A fix that finds its change already present is skipped, so the
script can be re-run on a partly fixed buildFile."""
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
    if 'congressofvienna/issues/new?template=bug_report.yml' in m.group(1):
        return None
    return raw[:m.start(1)] + attr(expr) + raw[m.end(1):]


def replace_once(raw, old, new, done_marker):
    """Replace exactly one occurrence of old; return None if done_marker is already present."""
    if done_marker in raw:
        return None
    assert raw.count(old) == 1, (old[:80], raw.count(old))
    return raw.replace(old, new)


def veil_1812_resolved(raw):
    """#14 Treaty of Ghent / Canada Annexed: grey the marker permanently once the War of 1812 has ended
    (it leaves the game, 12.4.1.3), not only during issue selection."""
    old = ('Draws a veil over out of play markers;1.0;;true')
    ctx = '{issueInactive &amp;&amp; Phase &gt; Initial &amp;&amp; Phase &lt; Conference ? 1 : 2};1;1;true;65,130;;;' + old
    new = ('{(issueInactive &amp;&amp; Phase &gt; Initial &amp;&amp; Phase &lt; Conference) || war1812status.startsWith(&quot;3&quot;) ? 1 : 2};1;1;true;65,130;;;'
           'Draws a veil over out of play markers (a60: always once the War of 1812 has ended);1.0;;true')
    return replace_once(raw, ctx, new, 'a60: always once the War of 1812 has ended')


def veil_austria_armistice_resolved(raw):
    """#15 Austria at War and Armistice: keep them greyed once resolved (both leave the game, 12.4.1.2, 12.4.2)."""
    r = replace_once(raw,
        '{(issueInactive || WarState == 2) &amp;&amp; Phase &gt; Initial &amp;&amp; Phase &lt; Conference ? 1 : 2}',
        '{(issueInactive &amp;&amp; Phase &gt; Initial &amp;&amp; Phase &lt; Conference) || WarState == 2 ? 1 : 2}',
        '{(issueInactive &amp;&amp; Phase &gt; Initial &amp;&amp; Phase &lt; Conference) || WarState == 2 ? 1 : 2}')
    raw = r if r is not None else raw
    r2 = replace_once(raw,
        '{issueInactive || (_Level == 2 &amp;&amp; Phase &gt; Initial &amp;&amp; Phase &lt; Conference) ? 1 : 2}',
        '{(issueInactive &amp;&amp; Phase &gt; Initial &amp;&amp; Phase &lt; Conference) || _Level == 2 ? 1 : 2}',
        '{(issueInactive &amp;&amp; Phase &gt; Initial &amp;&amp; Phase &lt; Conference) || _Level == 2 ? 1 : 2}')
    if r is None and r2 is None:
        return None
    return r2 if r2 is not None else raw


def dock_rejected_unit(raw):
    """#17 A unit moved into a full (or wrong-nationality) Army Box is sent back with goBack but left loose on
    top of its old deck. After goBack, dock it back into its own deck (dockWithStack)."""
    return replace_once(raw,
        'macro;An invalid move is returned to its origin;;57910,0,evaluateMove;{moveCase &lt; 2};;57609\\,0\\,goBack;',
        'macro;An invalid move is returned to its origin (a60: and re-docked);;57910,0,evaluateMove;{moveCase &lt; 2};;57609\\,0\\,goBack,57912\\,0\\,dockWithStack;',
        'a60: and re-docked')


def withdraw_msg_1812(raw):
    """#12 Front G (War of 1812): neither side may withdraw (13.4.2). Report that as a plain rule note instead
    of the red "Neither side may withdraw!" that read like a faulty bot check."""
    if 'name="mNoWithdrawal1812"' in raw:
        return None
    raw = replace_once(raw, '(LockFRwithdraw &amp;&amp; LockCOwithdraw ? tRedB + mNoWithdrawals :',
        '(ActiveFront == &quot;G&quot; ? mNoWithdrawal1812 : LockFRwithdraw &amp;&amp; LockCOwithdraw ? tRedB + mNoWithdrawals :', '@@never@@')
    return replace_once(raw, '<VASSAL.build.module.properties.GlobalTranslatableMessage description="" initialValue="Neither side may withdraw!" name="mNoWithdrawals"/>',
        '<VASSAL.build.module.properties.GlobalTranslatableMessage description="" initialValue="Neither side may withdraw!" name="mNoWithdrawals"/>'
        '<VASSAL.build.module.properties.GlobalTranslatableMessage description="a60 #12" initialValue="No withdrawal in the War of 1812 Box [13.4.2]" name="mNoWithdrawal1812"/>', '@@never@@')


FIXES = [report_issue_link, veil_1812_resolved, veil_austria_armistice_resolved, dock_rejected_unit, withdraw_msg_1812]

if __name__ == '__main__':
    raw = open(BF, encoding='utf-8').read()
    for f in FIXES:
        r = f(raw)
        if r is None:
            print('already applied', f.__name__)
        else:
            raw = r
            print('applied', f.__name__)
    open(BF, 'w', encoding='utf-8').write(raw)
