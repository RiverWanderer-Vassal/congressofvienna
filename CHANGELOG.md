# Changelog

## 2.0.0a61 (in preparation)

Builds on 2.0.0a60 (not yet released). **Load your game, then run Tools > Refresh Counters** (defaults) so existing pieces pick up the Military Operation checks.

- **Environment Table, 2nd die**: the 2nd die could be rolled right after the 1st roll, before the National card it called for had been drawn. It now unlocks only once that card is drawn (the chat says so), or straight away when no draw is due.
- **Military Operations dragged to a front** now meet the same rule restrictions as the right-click Front commands. A marker dropped where the rules forbid it goes back and an alert gives the reason: the Armistice (no Military Operation on Fronts A and B or in Denmark/Norway [13.1]), Austria not at war (Front F, and Austria on Front A [12.4.2]), France never attacking Sicily from Naples [13.1], Britain in Sicily without a British unit and a fleet [13.6.3], Britain on Front B without a fleet in the Scheldt, the War of 1812 Box (ended, or none of your units there) and Denmark/Norway without both sides present. A marker dragged straight from a National Track onto a front is now checked too (it used to skip every check, including side and one per Army/Box). A rejected move no longer registers the marker on the front it was dropped on.
- **Paired fronts** [13.6.1], as printed on the map: Britain cannot place a Military Operation to attack Gascony until the Coalition occupies Valencia, or Toulouse until it occupies Catalonia (Front D). This applies to both dragging and the right-click Front C command, because Front D is fought after Front C. A Russian Military Operation to attack Hanover is still allowed without Saxony, because Front A is fought first and may take it. It now brings a warning, and when Front B's battle starts with Saxony still not occupied, the chat says in red that the attack cannot be carried out [13.6.1.4].
- **Battle cards**: when the last side pressed its ready button, only some hands were sent to the battle window (chosen by which hand pressed last, the front and the player count), and the Russian and British hands could be switched off by the player-count setting. Selected cards could stay behind (reported on Front B: France's cards arrived, Russia's did not). The last ready press now sends the selected cards of every hand, France first as before. Each ready press is reported in the chat, and so is what each side sent.

## 2.0.0a60 (in preparation)

**Load your game, then run Tools > Refresh Counters** (defaults) so existing pieces pick up the fixes below.

- **Report an Issue** (#1): Help > Report an Issue opens this repository's bug form with the module, VASSAL and Java versions, scenario and options, and the current game state filled in.
- **Armistice** (#10): the War Status marker can no longer be set to *Armistice* by hand (that blocked France on Fronts A/B without an Armistice). An Armistice won on a National Track now offers *Resolve: Armistice does not occur*, which explains the rule [12.4.1.2]. If the War Status ever shows Armistice without the Armistice in effect, a red warning appears at the end of the Diplomacy Phase and *Correct to Limited War* is offered on the War Status marker.
- **War of 1812 withdrawal** (#12): Front G now reports "No withdrawal in the War of 1812 Box [13.4.2]" instead of a red "Neither side may withdraw!".
- **Resolved issues stay greyed** (#14, #15): Treaty of Ghent / Canada Annexed, Austria at War and Armistice are greyed in every phase once resolved.
- **Army Box over-capacity** (#17): a unit refused by a full Army Box returns into its own deck instead of lying loose on top of it.
- **Gold pawn** : "Proceed to Wager Phase" (the F12 deal-glitch workaround) is offered only in the Deal phase. Before, choosing it during the Initial Environment Table skipped the rest of the table and the deal.
- **Faster card deal** (#25): the per-card "draws a card" report no longer runs while dealing (it printed nothing during the deal but cost about 0.2 s per card). Roughly 15% faster on stock VASSAL, about 3x faster again on a VASSAL build with the keystroke fix (vassalengine/vassal#15257).
- **Situation Cards**: removed two leftover debug lines from the chat log (e.g. "SCRUunitB2 2" on card A-6).
- **VP-denying cards** (#23): Andrew Jackson, Sherbrooke and King Fernando VII of Spain now have *Play Alternative Action* (as Joseph Bonaparte already had), reserving their marker to cancel the opponent's end-of-turn VP.

Deferred to a later alpha: wager winner correction (#21) and the related issue placement offset (#11).
