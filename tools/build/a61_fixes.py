#!/usr/bin/env python3
"""Fixes applied to dist/buildFile.xml for 2.0.0a61. Run from the repository root:
    python3 tools/build/a61_fixes.py
Each fix edits the raw XML text in place and only touches the elements it names. A fix that finds its
change already present is skipped, so the script can be re-run on a partly fixed buildFile."""
import html, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vassal_traits import decode_def, encode_def, seq_encode  # noqa: E402

BF = 'dist/buildFile.xml'
PAT = re.compile(r'<(VASSAL\.[\w.]*?(PrototypeDefinition|PieceSlot|CardSlot))\b([^>]*)>(.*?)</\1>', re.S)


def attr(expr: str) -> str:
    return expr.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def text(s: str) -> str:
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def replace_once(raw, old, new):
    assert raw.count(old) == 1, (old[:100], raw.count(old))
    return raw.replace(old, new)


def prototype(raw, name):
    hits = [m for m in PAT.finditer(raw) if m.group(2) == 'PrototypeDefinition'
            and html.unescape(re.search(r'\bname="([^"]*)"', m.group(3)).group(1)) == name]
    assert len(hits) == 1, (name, len(hits))
    m = hits[0]
    pid, types, states = decode_def(html.unescape(m.group(4)))
    return m, pid, types, states


def put_prototype(raw, m, pid, types, states):
    return raw[:m.start(4)] + text(encode_def(pid, types, states)) + raw[m.end(4):]


def index_of(types, prefix):
    hits = [i for i, t in enumerate(types) if t.startswith(prefix)]
    assert len(hits) == 1, (prefix, hits)
    return hits[0]


# ---------------------------------------------------------------------------------------------
def env_second_die_after_draw(raw):
    """Environment Table: the 2nd die could be rolled as soon as the 1st roll was resolved, before the
    National card it called for was drawn. ETroll2 (which shows the 2nd die's roll command) is now set
    only when no draw is pending, and is set when the draw is done (ETDRAWDONE)."""
    if 'desc="on once the National card is drawn"' in raw:
        return None
    raw = replace_once(raw,
        'desc="on" disabledIcon="" hideWhenDisabled="false" hotkey="57449,0,ENVPHASE2" icon="" propChanger="P,true"',
        'desc="on, unless a National card draw is pending" disabledIcon="" hideWhenDisabled="false" '
        'hotkey="57449,0,ENVPHASE2" icon="" propChanger="P,' + attr('{DrawPower == ""}') + '"')
    off = ('<VASSAL.build.module.properties.ChangePropertyButton canDisable="false" desc="off after roll" '
           'disabledIcon="" hideWhenDisabled="false" hotkey="57450,0,ENVROLL2" icon="" propChanger="P,false" '
           'propertyGate="" reportFormat="" text="" tooltip=""/>')
    rpt = '{Phase == EnvPhase2 ? "<b><i>National card drawn: the 2nd Environment die can now be rolled.</i></b>" : ""}'
    new = ('<VASSAL.build.module.properties.ChangePropertyButton canDisable="false" desc="on once the National card is drawn" '
           'disabledIcon="" hideWhenDisabled="false" hotkey="57451,0,ETDRAWDONE" icon="" propChanger="P,'
           + attr('{Phase == EnvPhase2}') + '" propertyGate="" reportFormat="' + attr(rpt) + '" text="" tooltip=""/>')
    indent = '\n                '
    return replace_once(raw, off, off + indent + new)


# ---------------------------------------------------------------------------------------------
MO_BLOCK = ('{CurrentZone == "Paris" || FrontTrack == "" || CapitalCode != "" ? "" : '
    '(FrontTrack =~ "A|B" && sideCode =~ "FR|RU" && WarState == 1) || (FrontTrack == "DN" && WarState == 1) ? '
    '"The Armistice is in effect: no Military Operation on Front A, Front B or in Denmark/Norway [13.1]." : '
    'FrontTrack == "F" && WarState < 2 ? "Austria is not at war: no Military Operation on Front F [12.4.2]." : '
    'FrontTrack == "A" && sideCode == "AU" && WarState < 2 ? "Austria is not at war: no Austrian Military Operation on Front A [12.4.2]." : '
    'FrontTrack == "E" && sideCode == "FR" ? "France can never place a Military Operation to attack Sicily from Naples [13.1]." : '
    'FrontTrack == "E" && sideCode == "BR" && (CountZone("Sicily", map, "fleet") == 0 || CountZone(ZoneCOE, map, "COdrm") == 0) ? '
    '"A British Military Operation in Sicily needs at least one British unit and one fleet there [13.1, 13.6.3]." : '
    'FrontTrack == "B" && sideCode == "BR" && CountZone("Scheldt", map, "fleet") == 0 ? '
    '"A British Military Operation on Front B needs a British fleet in the Scheldt." : '
    'FrontTrack == "G" && war1812status.startsWith("3") ? "The War of 1812 has ended: no more Military Operations there." : '
    'FrontTrack == "G" && sideCode =~ "FR|BR" && CountZone(ZoneG, map, sideCode == "FR" ? "FRdrm" : "COdrm") == 0 ? '
    '"A Military Operation in the War of 1812 Box needs at least one of your units or fleets there [13.1]." : '
    'FrontTrack == "DN" && (CountZone(ZoneDN, map, "COdrm") == 0 || CountZone(ZoneDN, map, "FRdrm") == 0) ? '
    '"A Military Operation in Denmark/Norway needs units of both sides there." : ""}')


def milop_restrictions(raw):
    """Military Operations dragged onto the battle board were only checked for the marker's side and for
    one marker per Army/Box, and a marker dragged straight from a National Track was not checked at all.
    The same rule restrictions the right-click commands apply (Armistice, Austria at war, Sicily, Scheldt,
    War of 1812, Denmark/Norway) now also stop a dragged marker: it goes back and an alert says why."""
    m, pid, t, s = prototype(raw, 'Military Operation Placement')
    if any(x.startswith('calcProp;moBlock;') for x in t):
        return None
    # moveCase: new error code 7 (odd = rejected) when a rule restriction applies; alert command
    i = index_of(t, 'PROP;moveCase;')
    old = 'sideCode !~ SidesHere ? 1 \\: '
    assert t[i].count(old) == 1
    t[i] = t[i].replace(old, old + 'moBlock != "" ? 7 \\: ')
    old = ',:57855\\,0\\,alertMODN:P\\,{Alert(mMODN)}'
    assert t[i].count(old) == 1
    t[i] = t[i].replace(old, old + ',:59121\\,0\\,alertMOblock:P\\,{Alert(moBlockMsg)}')
    old = '5: special (1812 & Denmark/Norway - 1 only total)\\;'
    assert t[i].count(old) == 1
    t[i] = t[i].replace(old, '5: special (1812 & Denmark/Norway - 1 only total), 7: rule restriction (see moBlock)\\;')
    # the message, stored at the drop position (the alert runs after the marker has gone back)
    msg = seq_encode(['PROP', 'moBlockMsg', 'false,0,100,false',
                      seq_encode([seq_encode(['', '57850,0,chkMove', seq_encode(['P', '{moBlock}'], ',')], ':')], ','),
                      'a61: rule restriction message for the last rejected placement'], ';')
    calc = seq_encode(['calcProp', 'moBlock', MO_BLOCK,
                       'a61: "" when the rules allow a Military Operation here, otherwise why not '
                       '(mirrors the Disable conditions of the right-click Front commands)'], ';')
    t[i + 1:i + 1] = [msg, calc]
    s[i + 1:i + 1] = ['', '']
    # alert macro, beside the other doAlert macros
    j = index_of(t, 'macro;Not allowed;')
    t.insert(j + 1, 'macro;Rule restriction (a61);;57865,0,doAlert;{moveCase % 8 == 7};;59121\\,0\\,alertMOblock;'
                    'false;;;counted;;;;false;;1;1')
    s.insert(j + 1, '')
    # a rejected (odd) move no longer runs the valid-move register/deregister/redirect steps
    j = index_of(t, 'macro;Valid (odd bit clear);')
    old = '{moveCase % 1 == 0}'
    assert t[j].count(old) == 1
    t[j] = t[j].replace(old, '{moveCase % 2 == 0}')
    # check moves from a National Track onto a front (capitals and Paris stay free, as before)
    j = index_of(t, 'macro;Front Track checks start once MO is moved')
    old = '{GameStarted && !OldZone.contains("Track")}'
    assert t[j].count(old) == 1
    t[j] = t[j].replace(old, '{GameStarted && (!OldZone.contains("Track") || (FrontTrack != "" && CapitalCode == ""))}')
    return put_prototype(raw, m, pid, t, s)


# ---------------------------------------------------------------------------------------------
HANDS = [('French Hand', 'France'), ('Russian Hand', 'Russia'), ('Austrian Hand', 'Austria'),
         ('Austro-Russian Hand', 'Austria-Russia'), ('British Hand', 'Britain'), ('Coalition Hand', 'Coalition')]
SEND_KEYS = ['58478\\,0\\,SendFRBattleCards', '58481\\,0\\,SendRUBattleCards', '58480\\,0\\,SendAUBattleCards',
             '58495\\,0\\,SendAURUBattleCards', '58496\\,0\\,SendBRBattleCards', '58497\\,0\\,SendCOBattleCards']
OLD_SEND = {
    'chkInitBattleCardsFromAU': '58478\\,0\\,SendFRBattleCards,58479\\,0\\,chkSendRUBattleCards,58480\\,0\\,SendAUBattleCards',
    'chkInitBattleCardsFromFR': '58478\\,0\\,SendFRBattleCards,58494\\,0\\,chkSendBattleCardsFromFR',
    'chkInitBattleCardsFromRU': '58478\\,0\\,SendFRBattleCards,58481\\,0\\,SendRUBattleCards,58516\\,0\\,chkSendAUBattleCards',
    'chkInitBattleCardsFromAURU': '58478\\,0\\,SendFRBattleCards,58495\\,0\\,SendAURUBattleCards',
    'chkInitBattleCardsFromCO': '58478\\,0\\,SendFRBattleCards,58497\\,0\\,SendCOBattleCards',
    'chkInitBattleCardsFromBR': '58478\\,0\\,SendFRBattleCards,58496\\,0\\,SendBRBattleCards',
}
READY = {'LockBattleFR': 'France', 'LockBattleRU': 'Russia', 'LockBattleAU': 'Austria',
         'LockBattleAURU': 'Austria-Russia', 'LockBattleCO': 'The Coalition', 'LockBattleBR': 'Britain'}


def battle_cards_from_every_hand(raw):
    """Battle: when the last side pressed its ready button, only some hands were sent to the battle window,
    chosen by which hand pressed last, the front and the player count; the Russian and British sends were
    also switched off by the player-count flags. Selected cards could stay behind (reported on Front B:
    France's cards arrived, Russia's did not). Now the last ready press sends the selected cards of every
    hand, France first as before, the ready press is reported, and the send reports what each side sent."""
    if '59130,0,SendAllBattleCards' in raw:
        return None
    # one module-level button sends every hand's selected cards (France first: the row switch follows it)
    counts = ' + '.join('(CountMap("%s", "{selectedForBattle}") > 0 ? " %s " + CountMap("%s", "{selectedForBattle}") : "")'
                        % (h, side, h) for h, side in HANDS)
    total = ' + '.join('CountMap("%s", "{selectedForBattle}")' % h for h, _ in HANDS)
    rpt = '{"<i>Battle cards to the battle window:" + (' + total + ' == 0 ? " none" : ' + counts + ') + "</i>"}'
    btn = ('<VASSAL.build.module.DoActionButton canDisable="false" disabledIcon="" doHotkey="true" doLoop="false" '
           'doReport="true" doSound="false" hideWhenDisabled="false" hotkey="59130,0,SendAllBattleCards" hotkeys="'
           + ','.join(SEND_KEYS) + '" icon="" index="false" indexProperty="" indexStart="1" indexStep="1" loopCount="1" '
           'loopType="counted" name="a61: Send the selected battle cards of every hand to the Battle mat (France first)" '
           'postLoopKey="" preLoopKey="" propertyGate="" reportFormat="' + attr(rpt) + '" soundClip="" text="" tooltip="" '
           'untilExpression="" whileExpression=""/>')
    anchor = '<VASSAL.build.module.ToolbarMenu canDisable="false" description="Battle Fronts &amp; utilities"'
    raw = replace_once(raw, anchor, btn + '\n            ' + anchor)
    # every hand's "send all queued cards" step now fires that one button
    for key, old in OLD_SEND.items():
        pat = 'hotkey="%s" hotkeys="%s"' % (OLD_SEND_CODES[key], old)
        raw = replace_once(raw, pat, 'hotkey="%s" hotkeys="59130\\,0\\,SendAllBattleCards"' % OLD_SEND_CODES[key])
    # the Russian and British "Send selected cards" commands no longer depend on the player-count flags
    for k, gate in (('58481,0,SendRUBattleCards', 'RUdisabled'), ('58496,0,SendBRBattleCards', 'BRdisabled')):
        old = re.search(r'<VASSAL\.build\.module\.map\.MassKeyCommand buttonHotkey="%s"[^>]*/>' % re.escape(k), raw)
        assert old and raw.count(old.group(0)) == 1, k
        new = old.group(0).replace('canDisable="true"', 'canDisable="false"').replace(
            'propertyGate="%s"' % gate, 'propertyGate=""')
        raw = raw.replace(old.group(0), new)
    # report each ready press
    for key, side in READY.items():
        old = re.search(r'<VASSAL\.build\.module\.DoActionButton [^>]*hotkeys="57\d\d\d\\,0\\,%s,[^>]*/>' % key, raw)
        assert old and raw.count(old.group(0)) == 1, key
        e = old.group(0)
        assert 'doReport="false"' in e and 'reportFormat=""' in e, key
        e = e.replace('doReport="false"', 'doReport="true"').replace(
            'reportFormat=""', 'reportFormat="' + attr('<i><b>%s</b> is ready for this battle.</i>' % side) + '"')
        raw = raw.replace(old.group(0), e)
    return raw


OLD_SEND_CODES = {
    'chkInitBattleCardsFromAU': '58476,0,chkInitBattleCardsFromAU',
    'chkInitBattleCardsFromFR': '58493,0,chkInitBattleCardsFromFR',
    'chkInitBattleCardsFromRU': '58515,0,chkInitBattleCardsFromRU',
    'chkInitBattleCardsFromAURU': '58524,0,chkInitBattleCardsFromAURU',
    'chkInitBattleCardsFromCO': '58535,0,chkInitBattleCardsFromCO',
    'chkInitBattleCardsFromBR': '58547,0,chkInitBattleCardsFromBR',
}


FIXES = [env_second_die_after_draw, milop_restrictions, battle_cards_from_every_hand]

if __name__ == '__main__':
    raw = open(BF, encoding='utf-8').read()
    for f in FIXES:
        new = f(raw)
        print(('applied ' if new is not None else 'already  ') + f.__name__)
        if new is not None:
            raw = new
    open(BF, 'w', encoding='utf-8').write(raw)
