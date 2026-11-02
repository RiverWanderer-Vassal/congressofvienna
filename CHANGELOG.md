# Changelog

## 2.0.0a60 (in preparation)

**Load your game, then run Tools > Refresh Counters** (defaults) so existing pieces pick up the fixes below.

- **Report an Issue** (#1): Help > Report an Issue opens this repository's bug form with the module, VASSAL and Java versions, scenario and options, and the current game state filled in.
- **Armistice** (#10): the War Status marker can no longer be set to *Armistice* by hand (that blocked France on Fronts A/B without an Armistice). An Armistice won on a National Track now offers *Resolve: Armistice does not occur*, which explains the rule [12.4.1.2]. If the War Status ever shows Armistice without the Armistice in effect, a red warning appears at the end of the Diplomacy Phase and *Correct to Limited War* is offered on the War Status marker.
- **War of 1812 withdrawal** (#12): Front G now reports "No withdrawal in the War of 1812 Box [13.4.2]" instead of a red "Neither side may withdraw!".
- **Resolved issues stay greyed** (#14, #15): Treaty of Ghent / Canada Annexed, Austria at War and Armistice are greyed in every phase once resolved.
- **Army Box over-capacity** (#17): a unit refused by a full Army Box returns into its own deck instead of lying loose on top of it.
- **Situation Cards**: removed two leftover debug lines from the chat log (e.g. "SCRUunitB2 2" on card A-6).
- **VP-denying cards** (#23): Andrew Jackson, Sherbrooke and King Fernando VII of Spain now have *Play Alternative Action* (as Joseph Bonaparte already had), reserving their marker to cancel the opponent's end-of-turn VP.

Deferred to a later alpha: wager winner correction (#21) and the related issue placement offset (#11).
