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
# Paired fronts [13.6.1], as printed on the map. Front C waits on Front D, whose battle comes later in the turn,
# so a British Front C attack whose prerequisite is not already met is refused at placement. Front B waits on
# Front A, whose battle comes first, so a Russian Front B placement is allowed with a warning and the Front B
# battle start reports when Saxony is still not occupied.
PAIRED_CD = ('(FrontTrack == "C" && sideCode == "BR" && FrontDBR != "" && '
             '((FrontCBR == "Castile" && FrontDBR !~ "Valencia|Catalonia|Pyrenees") || '
             '(FrontCBR == "Gascony" && FrontDBR !~ "Catalonia|Pyrenees")))')
NO_SAXONY = '(FrontARU !~ "Saxony|Bavaria|Alsace|Paris" && FrontAAU !~ "Saxony|Bavaria|Alsace|Paris")'

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
    '"A Military Operation in Denmark/Norway needs units of both sides there." : '
    + PAIRED_CD + ' ? (FrontCBR == "Castile" ? '
    '"The Coalition must occupy Valencia (Front D) before Britain can attack Gascony [13.6.1.2]." : '
    '"The Coalition must occupy Catalonia (Front D) before Britain can attack Toulouse [13.6.1.2].") : ""}')


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


def paired_fronts(raw):
    """Paired fronts [13.6.1], printed on the map: Hanover needs Saxony occupied (Front A), Gascony needs
    Valencia and Toulouse needs Catalonia (Front D). Front C is refused at placement through moBlock (see
    PAIRED_CD); this adds the same Disable on the British Front C right-click command, a warning when a
    Russian Military Operation is placed on Front B to attack Hanover without Saxony, and, when Front B is chosen
    in the battle menu without Saxony occupied, the Russian marker goes home and Front B is cancelled unless
    France also has a marker there [13.6.1.4]."""
    if 'Paired front B warning (a61)' in raw:
        return None
    # BR right-click Front C
    m, pid, t, s = prototype(raw, 'BR Military Operation')
    j = index_of(t, 'hideCmd;Only 1;Disable;MilOpCBR > 0;')
    cond = PAIRED_CD.replace('FrontTrack == "C" && sideCode == "BR" && ', '')
    t.insert(j + 1, 'hideCmd;Paired fronts C/D [13.6.1.2];Disable;{' + cond + '};57870\\,0\\,goC')
    s.insert(j + 1, '')
    raw = put_prototype(raw, m, pid, t, s)
    # Russian Front B placement warning (fires on a valid registration)
    m, pid, t, s = prototype(raw, 'Military Operation Placement')
    j = index_of(t, 'PROP;moBlockMsg;')
    warn = '{Alert("Allowed, but the Russian attack on Hanover can only be carried out if the Coalition occupies Saxony when Front B is fought (Front A is fought first) [13.6.1.1].")}'
    t.insert(j + 1, seq_encode(['PROP', 'moWarnB', 'false,0,100,false',
        seq_encode([seq_encode(['', '59122,0,warnMOpairedB', seq_encode(['P', warn], ',')], ':')], ','),
        'a61: paired front warning'], ';'))
    s.insert(j + 1, '')
    j = index_of(t, 'macro;Rule restriction (a61);')
    t.insert(j + 1, 'macro;Paired front B warning (a61);;57859,0,register;{FrontTrack == "B" && sideCode == "RU" && '
             'FrontBRU == "Pomerania" && ' + NO_SAXONY + '};;59122\\,0\\,warnMOpairedB;false;;;counted;;;;false;;1;1')
    s.insert(j + 1, '')
    raw = put_prototype(raw, m, pid, t, s)
    # Front B in the battle menu: the menu item becomes a check. If the Coalition does not occupy Saxony, the
    # Russian Military Operation on the Northern Army goes back to the Diplomacy Display (its deregister re-locks
    # Front B when no other marker is there, as after a battle), the chat says why, and the battle only runs if
    # another Military Operation (France) still holds Front B. The original button keeps all its actions and
    # is now fired by key only.
    bad = 'FrontBRU == "Pomerania" && ' + NO_SAXONY
    old = re.search(r'<VASSAL\.build\.module\.DoActionButton canDisable="true" disabledIcon="toolbarSpace-w02\.png"[^>]*'
                    r'name="Front B" postLoopKey="58506,0,CHECKLASTBATTLE" preLoopKey="57370,0,setFrontB" propertyGate="LockB"[^>]*/>', raw)
    assert old and raw.count(old.group(0)) == 1
    e = old.group(0)
    assert e.count('hotkey=""') == 1 and e.count('text="B: Northern Europe"') == 1
    hidden = (e.replace('canDisable="true" disabledIcon="toolbarSpace-w02.png"', 'canDisable="false" disabledIcon=""')
               .replace('hotkey=""', 'hotkey="59134,0,doFrontB"').replace('propertyGate="LockB"', 'propertyGate=""')
               .replace('text="B: Northern Europe"', 'text=""'))
    rpt = ('{MilOpBRU > 0 && ' + bad + ' ? "<font color=red><b>Front B: the Coalition does not occupy Saxony, so the '
           'Russian attack on Hanover is cancelled and its Military Operation returns to the Diplomacy Display '
           '[13.6.1.1, 13.6.1.4].</b></font>" + (MilOpBFR > 0 ? "" : " No Front B battle this turn.") : ""}')
    menu = ('<VASSAL.build.module.DoActionButton canDisable="true" disabledIcon="toolbarSpace-w02.png" doHotkey="true" '
            'doLoop="false" doReport="true" doSound="false" hideWhenDisabled="false" hotkey="" '
            'hotkeys="59132\\,0\\,cancelRUfrontB,59133\\,0\\,chkFrontB" icon="" index="false" indexProperty="" '
            'indexStart="1" indexStep="1" loopCount="1" loopType="counted" '
            'name="a61: Front B - paired front check (Hanover needs Saxony) [13.6.1.1]" postLoopKey="" preLoopKey="" '
            'propertyGate="LockB" reportFormat="' + attr(rpt) + '" soundClip="" text="B: Northern Europe" tooltip="" '
            'untilExpression="" whileExpression=""/>')
    gkc = ('<VASSAL.build.module.GlobalKeyCommand buttonHotkey="59132,0,cancelRUfrontB" buttonText="" canDisable="false" '
           'deckCount="0" disabledIcon="" filter="' + attr('{' + bad + '}') + '" hideWhenDisabled="false" '
           'hotkey="57354,0,gohome" icon="" name="a61: Russian Front B Military Operation home when Saxony is not occupied" '
           'propertyGate="" reportFormat="" reportSingle="true" singleMap="true" suppressSounds="true" '
           'target="MODULE|true|ZONE|$map$||Northern Army||0|0||true|sideCode|RU|EQUALS||" tooltip=""/>')
    chk = ('<VASSAL.build.module.DoActionButton canDisable="false" disabledIcon="" doHotkey="true" doLoop="true" '
           'doReport="false" doSound="false" hideWhenDisabled="false" hotkey="59133,0,chkFrontB" '
           'hotkeys="59134\\,0\\,doFrontB" icon="" index="false" indexProperty="" indexStart="1" indexStep="1" '
           'loopCount="' + attr('{LockB ? 0 : 1}') + '" loopType="counted" name="a61: Front B battle if still open" '
           'postLoopKey="" preLoopKey="" propertyGate="" reportFormat="" soundClip="" text="" tooltip="" '
           'untilExpression="" whileExpression=""/>')
    ind = '\n            '
    return raw.replace(e, menu + ind + gkc + ind + chk + ind + hidden)

def mountain_hold(raw):
    """Battle menu: "France holds the mountains" / "Coalition holds the mountains" [13.4.5 Canceling a Retreat].
    Locked during the battle. "End of battle: read the battle track" opens the item only when the losing Army
    defends in a mountain space (the attacker's mountain malus, MountainCO / MountainFR, is -3), nobody withdrew,
    the losses differ by exactly one and at least one of the loser's units would remain after the extra loss.
    Pressing it logs the extra loss and the cancelled retreat and locks both items until the next battle."""
    if 'name="LockFRhold"' in raw:
        return None
    def gp(name, side_mtn, side, other):
        ok = ('{!(EobWithdrew == "" && ActiveFront =~ "A|C|D|F" && %s == -3 && EobHits%s - EobHits%s == 1 '
              '&& EobUnits%s - EobHits%s > 1)}') % (side_mtn, other, side, side, other)
        def cpb(desc, key, val):
            return ('                <VASSAL.build.module.properties.ChangePropertyButton canDisable="false" desc="%s" '
                    'disabledIcon="" hideWhenDisabled="false" hotkey="%s" icon="" propChanger="P,%s" propertyGate="" '
                    'reportFormat="" text="" tooltip=""/>\n') % (desc, key, attr(val))
        return ('<VASSAL.build.module.properties.GlobalProperty description="a61: mountain hold button control" '
                'initialValue="true" isNumeric="false" max="null" min="null" name="%s" wrap="false">\n' % name
                + cpb('battle start: locked until the end of the battle', '57482,0,initDRM', 'true')
                + cpb('end of battle: open if this side may hold the mountains', '59143,0,eobCalc', ok)
                + cpb('no hold after a withdrawal', '57514,0,withdrawDRM', 'true')
                + cpb('locked after use', '59136,0,usedMountainHold', 'true')
                + cpb('locked when the markers go back', '59153,0,eobReturned', 'true')
                + '            </VASSAL.build.module.properties.GlobalProperty>\n            ')
    anchor = '<VASSAL.build.module.properties.GlobalProperty description="button control" initialValue="true" isNumeric="false" max="null" min="null" name="LockCOwithdraw"'
    raw = replace_once(raw, anchor, gp('LockFRhold', 'MountainCO', 'FR', 'CO') + gp('LockCOhold', 'MountainFR', 'CO', 'FR') + anchor)
    tail = (' loses one more unit to hold the mountains: the retreat is cancelled and the attacking Army stays in its '
            'space [13.4.5].</b>')
    def btn(text, gate, rpt):
        return ('<VASSAL.build.module.DoActionButton canDisable="true" disabledIcon="toolbarSpace-w02.png" doHotkey="true" '
                'doLoop="false" doReport="true" doSound="false" hideWhenDisabled="false" hotkey="" '
                'hotkeys="59136\\,0\\,usedMountainHold" icon="" index="false" indexProperty="" indexStart="1" indexStep="1" '
                'loopCount="1" loopType="counted" name="a61: %s" postLoopKey="" preLoopKey="" propertyGate="%s" '
                'reportFormat="%s" soundClip="" text="%s" tooltip="" untilExpression="" whileExpression=""/>') % (
                text, gate, attr(rpt), text)
    fr = btn('France holds the mountains', 'LockFRhold',
             '{"<b><i>" + mFR + "</i> (" + GetProperty("Front" + ActiveFront + "FR") + ")' + tail + '"}')
    co = btn('Coalition holds the mountains', 'LockCOhold',
             '{"<b><i>" + mCO + "</i> (" + GetProperty("Front" + ActiveFront + (ActiveFront == "A" ? "RU" : '
             'ActiveFront == "F" ? "AU" : "BR")) + ")' + tail + '"}')
    w = re.search(r'<VASSAL\.build\.module\.DoActionButton [^>]*name="Withdraw \(Coalition\)"[^>]*/>', raw)
    assert w and raw.count(w.group(0)) == 1
    raw = raw.replace(w.group(0), w.group(0) + '\n            ' + fr + '\n            ' + co)
    return replace_once(raw, 'Coalition Withdraws!,', 'Coalition Withdraws!,France holds the mountains,Coalition holds the mountains,')


FRONTS = ['A', 'B', 'DN', 'C', 'D', 'E', 'F', 'G']
CO_MO = {'A': ['ARU', 'AAU'], 'B': ['BRU', 'BBR'], 'DN': ['DNRU'], 'C': ['CBR'], 'D': ['DBR'], 'E': ['EBR'],
         'F': ['FAU'], 'G': ['GBR']}
ARMY_ZONES = {'A': 'Army of Silesia|Army of Bohemia|Grande Armée', 'B': 'Northern Army|Army of Elbe|Army of Scheldt',
              'DN': 'Denmark/Norway', 'C': 'Army of Portugal|Army of Spain', 'D': 'Eastern Army|Army of Mediterranean',
              'E': 'Army of Sicily|Army of Naples', 'F': 'Army of Tyrol|Army of Italy', 'G': 'War of 1812'}


def by_front(vals, default):
    """Nested ternary on ActiveFront."""
    e = default
    for f in reversed(FRONTS):
        if f in vals:
            e = 'ActiveFront == "%s" ? %s : %s' % (f, vals[f], e)
    return '(' + e + ')'


def end_of_battle(raw):
    """End of battle [13.4.4-13.4.6], at Mark's request (26 Nov 2026): the battle track is still played by hand;
    "End of battle: read the battle track" in the battle menu then works through the post-battle steps in order.
    1. Reads the losses each side inflicts from the DRM Track zone (result 0-5) under each battle pawn, names the
       winner (more losses inflicted, nobody withdrew), or a draw, and the losses each side removes.
    2. Major Battle [13.4.6]: both sides started with 4 or more units (the Coalition count on Front A already
       combines the Armies of Silesia and Bohemia), nobody withdrew, not the War of 1812 Box. The winner gains
       1 VP and the loser loses 1 VP, 2 when the Napoleon card was played in this battle (Napoleon was active at
       the start of the battle and is not any more). On Front A Russia, and Austria when at war, both score; the
       VP markers move through their usual addVP routine.
    3. Mountain hold [13.4.5]: the hold item opens only when it is allowed (see mountain_hold).
    4. Advance/retreat guidance [13.4.2, 13.4.5]; the players move the blocks and adjust space VPs [13.5].
    5. "Return markers: battle over" sends this Front's Military Operations to the Diplomacy Display and its
       Military Support markers to the Force Pools [13.4.6], through the markers' own commands, so the Front
       locks again as when they are moved by hand."""
    if 'name="EobHitsFR"' in raw:
        return None

    def pc(expr):  # a ChangePropertyButton value: commas are SequenceEncoder separators
        return attr(expr.replace(',', '\\,'))

    def cpb(desc, key, val):
        return ('                <VASSAL.build.module.properties.ChangePropertyButton canDisable="false" desc="%s" '
                'disabledIcon="" hideWhenDisabled="false" hotkey="%s" icon="" propChanger="P,%s" propertyGate="" '
                'reportFormat="" text="" tooltip=""/>\n') % (desc, key, pc(val))

    def gp(name, init, buttons, desc='a61: end of battle'):
        return ('<VASSAL.build.module.properties.GlobalProperty description="%s" initialValue="%s" isNumeric="false" '
                'max="null" min="null" name="%s" wrap="false">\n' % (desc, init, name)
                + ''.join(cpb(*b) for b in buttons)
                + '            </VASSAL.build.module.properties.GlobalProperty>\n            ')

    INIT, CALC, READ = '57482,0,initDRM', '59143,0,eobCalc', '59140,0,eobRead'
    hits = {s: ' + '.join('%d * CountZone("DRM Track %d", map, "{BasicName == \\"%s Battle DRM Pawn\\"}")' % (n, n, p)
                          for n in range(1, 6))
            for s, p in (('FR', 'French'), ('CO', 'Coalition'))}
    fr_atk = by_front({f: 'MilOp%sFR > 0' % f for f in FRONTS}, 'false')
    co_atk = by_front({f: ' || '.join('MilOp%s > 0' % m for m in CO_MO[f]) for f in FRONTS}, 'false')

    # start-of-battle unit counts: the same pick-ups the battle strength uses (MilStrFR / MilStrCO)
    def unit_buttons(src):
        m = re.search(r'<VASSAL\.build\.module\.properties\.GlobalProperty [^>]*name="%s"[^>]*>(.*?)'
                      r'</VASSAL\.build\.module\.properties\.GlobalProperty>' % src, raw, re.S)
        out = []
        for b in re.findall(r'<VASSAL\.build\.module\.properties\.ChangePropertyButton [^>]*/>', m.group(1)):
            v = re.search(r'propChanger="([^"]*)"', b).group(1)
            if v.startswith('P,{'):
                out.append('                ' + b.replace('desc="', 'desc="a61 units: ') + '\n')
        assert len(out) == 8, (src, len(out))
        return out
    units = {s: ('<VASSAL.build.module.properties.GlobalProperty description="a61: units at the start of the battle" '
                 'initialValue="0" isNumeric="false" max="null" min="null" name="EobUnits%s" wrap="false">\n' % s
                 + ''.join(unit_buttons('MilStr' + s))
                 + '            </VASSAL.build.module.properties.GlobalProperty>\n            ') for s in ('FR', 'CO')}

    gps = (gp('EobLock', 'true', [('battle start: open', INIT, 'false'), ('used', '59150,0,eobDone', 'true')])
           + gp('EobReturnLock', 'true', [('battle start: locked', INIT, 'true'), ('open after the end of battle', '59150,0,eobDone', 'false'),
                                          ('used', '59153,0,eobReturned', 'true')])
           + gp('EobWithdrew', '', [('battle start', INIT, ''), ('France withdrew', '59141,0,eobFRwd', 'FR'),
                                    ('Coalition withdrew', '59142,0,eobCOwd', 'CO')])
           + gp('EobNapStart', 'true', [('Napoleon active at the start of the battle', INIT, '{NapoleonActive}')])
           + units['FR'] + units['CO']
           + gp('EobHitsFR', '0', [('losses inflicted by France', READ, '{' + hits['FR'] + '}')])
           + gp('EobHitsCO', '0', [('losses inflicted by the Coalition', READ, '{' + hits['CO'] + '}')])
           + gp('EobFRatk', 'false', [('France has a Military Operation on this Front', READ, '{' + fr_atk + '}')])
           + gp('EobCOatk', 'false', [('the Coalition has a Military Operation on this Front', READ, '{' + co_atk + '}')])
           + gp('EobWinner', '', [('FR, CO, draw, or empty after a withdrawal', CALC,
                                   '{EobWithdrew != "" ? "" : EobHitsFR > EobHitsCO ? "FR" : EobHitsCO > EobHitsFR ? "CO" : "draw"}')])
           + gp('EobMajor', 'false', [('Major Battle [13.4.6]', CALC,
                                       '{EobWithdrew == "" && EobHitsFR != EobHitsCO && ActiveFront != "G" && EobUnitsFR >= 4 && EobUnitsCO >= 4}')])
           + gp('EobVP', '1', [('2 with the Napoleon card', CALC, '{EobNapStart && !NapoleonActive ? 2 : 1}')])
           + gp('EobCOsides', 'RU', [('Coalition powers scoring this Front', CALC,
                                      '{ActiveFront == "A" ? (WarState == 2 ? "RU|AU" : "RU") : ActiveFront =~ "B|DN" ? "RU" : ActiveFront == "F" ? "AU" : "BR"}')])
           + gp('EobZones', '', [("this Front's Army boxes", CALC, by_front({f: '"%s"' % z for f, z in ARMY_ZONES.items()}, '""'))])
           + gp('mMajorBattle', 'Major Battle', [], 'a61: VP report prefix'))
    gps = gps.replace('propChanger="P,(ActiveFront', 'propChanger="P,{(ActiveFront').replace(' : &quot;&quot;)" propertyGate', ' : &quot;&quot;)}" propertyGate')
    anchor = '<VASSAL.build.module.properties.GlobalProperty description="button control" initialValue="true" isNumeric="false" max="null" min="null" name="LockCOwithdraw"'
    raw = replace_once(raw, anchor, gps + anchor)

    # Withdraw buttons record who withdrew
    for side, key in (('France', '59141\\,0\\,eobFRwd'), ('Coalition', '59142\\,0\\,eobCOwd')):
        w = re.search(r'<VASSAL\.build\.module\.DoActionButton [^>]*name="Withdraw \(%s\)"[^>]*/>' % side, raw).group(0)
        raw = replace_once(raw, w, w.replace('hotkeys="57514\\,0\\,withdrawDRM"', 'hotkeys="57514\\,0\\,withdrawDRM,' + key + '"'))

    FR, CO = 'mFR', 'mCO'
    win = '(EobWinner == "FR" ? mFR : mCO)'
    lose = '(EobWinner == "FR" ? mCO : mFR)'
    wd = '(EobWithdrew == "FR" ? mFR : mCO)'
    nwd = '(EobWithdrew == "FR" ? mCO : mFR)'
    loss = lambda n: '%s + (%s == 1 ? " loss" : " losses")' % (n, n)
    r1 = ('{"<b>End of battle, Front " + ActiveFront + ":</b> " + mFR + " inflicts " + ' + loss('EobHitsFR') + ' + ", " + mCO + '
          '" inflicts " + ' + loss('EobHitsCO') + ' + " (battle track) [13.4.4]. " + (EobWithdrew != "" ? "<b>" + ' + wd +
          ' + " withdrew.</b>" : EobWinner == "draw" ? "<b>Draw.</b>" : "<b>" + ' + win + ' + " wins.</b>") + '
          '" Remove units: " + mFR + " " + EobHitsCO + ", " + mCO + " " + EobHitsFR + "."}')
    starts = '" + mFR + " " + EobUnitsFR + " units, " + mCO + " " + EobUnitsCO + " at the start'
    r2 = ('{EobMajor ? "<b>Major Battle</b> (' + starts + '" + (EobVP == 2 ? ", Napoleon card played" : "") + "): " + ' + win +
          ' + " +" + EobVP + " VP, " + ' + lose + ' + " -" + EobVP + " VP, applied below [13.4.6]." : '
          'ActiveFront == "G" ? "War of 1812 Box: never a Major Battle, no VP [13.4.6]." : '
          'EobWithdrew != "" ? "No Major Battle VP after a withdrawal [13.4.6]. If the Napoleon, Kutuzov or Blücher card was '
          'played against the withdrawing Army, its owner gains 1 VP (by hand) [13.4.2]." : '
          'EobWinner == "draw" ? "Draw: no Major Battle VP [13.4.6]." : '
          '"Minor battle (' + starts + '; 4 each needed): no VP [13.4.6]."}')
    hold = ' lost by exactly one while defending in the mountains: it may hold them (Battle menu) before any Army moves [13.4.5]."'
    r3 = '{!LockFRhold ? "<b>" + mFR + "</b>' + hold + ' : !LockCOhold ? "<b>" + mCO + "</b>' + hold + ' : ""}'
    r4 = ('{EobWithdrew != "" ? ' + wd + ' + " withdrew: it retreats one space if it was defending or both sides had Military '
          'Operations, otherwise it stays in its space. " + ' + nwd + ' + " advances into a vacated space if it has a Military '
          'Operation [13.4.2]." : EobWinner == "draw" ? "Draw: the defending Army stays in place, no Army moves [13.4.5]." : '
          '(EobWinner == "FR" ? EobFRatk : EobCOatk) ? ' + lose + ' + " retreats one space to its rear and " + ' + win +
          ' + " advances into it, unless the mountains are held. Allied Armies in their Front Start Space and the Grande Armée '
          'in Paris do not retreat; the War of 1812 Box has no advance [13.4.5]." : ' + win +
          ' + " beat off the attack: no Army moves [13.4.5]."}')
    r5 = ('{"Move the Army blocks and adjust space VPs for any change of control by hand [13.5]. Then Battle menu &gt; '
          '<i>Return markers: battle over</i> [13.4.6]."}')

    def keybtn(name, key, rpt, hotkeys=''):
        return ('<VASSAL.build.module.DoActionButton canDisable="false" disabledIcon="" doHotkey="%s" doLoop="false" '
                'doReport="true" doSound="false" hideWhenDisabled="false" hotkey="%s" hotkeys="%s" icon="" index="false" '
                'indexProperty="" indexStart="1" indexStep="1" loopCount="1" loopType="counted" name="a61: %s" '
                'postLoopKey="" preLoopKey="" propertyGate="" reportFormat="%s" soundClip="" text="" tooltip="" '
                'untilExpression="" whileExpression=""/>') % ('true' if hotkeys else 'false', key, hotkeys, name, attr(rpt))

    def menubtn(text, gate, hotkeys, rpt=''):
        return ('<VASSAL.build.module.DoActionButton canDisable="true" disabledIcon="toolbarSpace-w02.png" doHotkey="true" '
                'doLoop="false" doReport="%s" doSound="false" hideWhenDisabled="false" hotkey="" hotkeys="%s" icon="" '
                'index="false" indexProperty="" indexStart="1" indexStep="1" loopCount="1" loopType="counted" name="a61: %s" '
                'postLoopKey="" preLoopKey="" propertyGate="%s" reportFormat="%s" soundClip="" text="%s" tooltip="" '
                'untilExpression="" whileExpression=""/>') % ('true' if rpt else 'false', hotkeys, text, gate, attr(rpt), text)

    def gkc(name, key, hotkey, target, flt, params=''):
        return ('<VASSAL.build.module.GlobalKeyCommand buttonHotkey="%s" buttonText="" canDisable="false" deckCount="0" '
                'disabledIcon="" filter="%s" hideWhenDisabled="false" hotkey="%s" icon="" name="a61: %s" parameters="%s" '
                'propertyGate="" reportFormat="" reportSingle="false" singleMap="true" suppressSounds="true" target="%s" '
                'tooltip=""/>') % (key, attr(flt), hotkey, name, attr(params), target)

    seq = ','.join(k.replace(',', '\\,') for k in (
        READ, CALC, '59144,0,eobR1', '59145,0,eobR2', '59146,0,eobR3', '59147,0,eobR4', '59148,0,eobR5',
        '59149,0,eobVP', '59150,0,eobDone'))
    vp_target = 'MODULE|true|MAP|$map$||||0|0||true|BasicName|(French\\|Austrian\\|Russian\\|British) VP|MATCH||'
    map_target = 'MODULE|true|MAP|$map$||||0|0||false|||EQUALS||'
    vp_param = 'prefixProp:mMajorBattle,incVP:{EobWinner == "%s" ? EobVP \\: 0 - EobVP}'
    ret_rpt = ('{"<b>Front " + ActiveFront + " battle over:</b> its Military Operations go back to the Diplomacy Display and '
               'its Military Support markers to the Force Pools [13.4.6]."}')
    ret = ','.join(k.replace(',', '\\,') for k in ('59151,0,eobRetMO', '59152,0,eobRetMS', '59153,0,eobReturned'))
    els = [
        menubtn('End of battle: read the battle track', 'EobLock', seq),
        keybtn('End of battle - result and losses', '59144,0,eobR1', r1),
        keybtn('End of battle - Major Battle VP', '59145,0,eobR2', r2),
        keybtn('End of battle - mountain hold', '59146,0,eobR3', r3),
        keybtn('End of battle - advance and retreat', '59147,0,eobR4', r4),
        keybtn('End of battle - next step', '59148,0,eobR5', r5),
        gkc('Major Battle VP - France', '59149,0,eobVP', '57983,0,addVP', vp_target, '{EobMajor && sideCode == "FR"}', vp_param % 'FR'),
        gkc('Major Battle VP - Coalition', '59149,0,eobVP', '57983,0,addVP', vp_target,
            '{EobMajor && sideCode =~ EobCOsides}', vp_param % 'CO'),
        menubtn('Return markers: battle over', 'EobReturnLock', ret, ret_rpt),
        gkc("Return this Front's Military Operations", '59151,0,eobRetMO', '57354,0,gohome', map_target,
            '{BasicName =~ ".*Military Operation.*" && CurrentZone =~ EobZones}'),
        gkc("Return this Front's Military Support", '59152,0,eobRetMS', '57912,0,ms2pool', map_target,
            '{BasicName =~ ".*Military Support" && CurrentZone =~ EobZones}'),
    ]
    w = re.search(r'<VASSAL\.build\.module\.DoActionButton [^>]*name="Withdraw \(Coalition\)"[^>]*/>', raw).group(0)
    raw = replace_once(raw, w, w + ''.join('\n            ' + e for e in els))
    return replace_once(raw, 'Coalition Withdraws!,France holds the mountains,Coalition holds the mountains,',
                        'Coalition Withdraws!,End of battle: read the battle track,France holds the mountains,'
                        'Coalition holds the mountains,Return markers: battle over,')


def free_milop_to_paris(raw):
    """Free French Military Operation [12.4.4]: when the Conference ends with Napoleon available for the War Phase,
    one French Military Operation not won on a National Track goes from the Diplomacy Display (else the Negotiation
    Table) to Paris for free. a59 only reminded France to do it by hand. The move uses the marker's own To Paris
    command (goParis), whose Disable already allows only one free marker in Paris, so a second one never follows."""
    if 'Free French Mil Op to Paris (a61)' in raw:
        return None
    old = re.search(r'<VASSAL\.build\.module\.DoActionButton [^>]*name="a59: Free French Mil Op reminder \(12\.4\.4\)"[^>]*/>', raw).group(0)
    rpt = ('<b><font color=blue>Napoleon was not used in the Diplomacy Phase: one French Military Operation goes to '
           'Paris for free [12.4.4].</font></b>')
    new = (old.replace('doHotkey="false"', 'doHotkey="true"')
              .replace('hotkeys=""', 'hotkeys="59160\\,0\\,freeMOdip,59161\\,0\\,freeMOtable"')
              .replace('name="a59: Free French Mil Op reminder (12.4.4)"', 'name="Free French Mil Op to Paris (a61) [12.4.4]"'))
    new = re.sub(r'reportFormat="[^"]*"', 'reportFormat="' + attr(rpt) + '"', new)
    tgt = 'MODULE|true|MAP|$map$||||0|0||true|BasicName|French Military Operation|EQUALS||'
    def gkc(name, key, zone):
        return ('<VASSAL.build.module.GlobalKeyCommand buttonHotkey="%s" buttonText="" canDisable="false" deckCount="0" '
                'disabledIcon="" filter="%s" hideWhenDisabled="false" hotkey="57845,0,goParis" icon="" name="a61: %s" '
                'parameters="" propertyGate="" reportFormat="" reportSingle="true" singleMap="true" suppressSounds="false" '
                'target="%s" tooltip=""/>') % (key, attr('{FRMilOp == 1 && !isWon && CurrentZone == %s}' % zone), name, tgt)
    ind = '\n    '
    return replace_once(raw, old, new + ind + gkc('free French Mil Op from the Diplomacy Display', '59160,0,freeMOdip', 'DiplomacyZone')
                        + ind + gkc('free French Mil Op from the Negotiation Table', '59161,0,freeMOtable', 'TableZone'))


def version(raw):
    old = 'nextPieceSlotId="3804" version="2.0.0a60"'
    if old not in raw:
        return None
    return replace_once(raw, old, 'nextPieceSlotId="3804" version="2.0.0a61"')


FIXES = [env_second_die_after_draw, milop_restrictions, battle_cards_from_every_hand, paired_fronts, mountain_hold,
         end_of_battle, free_milop_to_paris, version]

if __name__ == '__main__':
    raw = open(BF, encoding='utf-8').read()
    for f in FIXES:
        new = f(raw)
        print(('applied ' if new is not None else 'already  ') + f.__name__)
        if new is not None:
            raw = new
    open(BF, 'w', encoding='utf-8').write(raw)
