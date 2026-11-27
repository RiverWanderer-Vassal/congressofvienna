# Changelog

## 2.0.0a63 (in preparation)

Everything in 2.0.0a62 below, plus:

- **Space VPs now follow the Army blocks** [13.5] (Mark, 27 Nov 2026). Once the game has started (from the Conference on), moving an Army block on a Front applies the space VPs at once, the same way it already updates hand sizes. The paired block that moves with it scores for its own side, so both sides change together and the chat shows each change ("Army of Elbe to Paris [13.5]: French VP ..."). This follows the pattern Front A already had: every Front space carries, as zone properties, the VP total each power holds on that Front when its block stands there (VPFR for France; VPRU, VPAU or VPBR for the Coalition power). Fronts B to F now have them too, and Austria (Army of Bohemia) has its own on Front A, black spaces only. A black VP number goes to the side that takes the space and is lost by the other; a coloured one (Silesia and Prussia for Russia, Venice for Austria, Naples for Britain) counts only for that power.
- **Paris** [13.6.5]: Paris is always French-controlled, so a French Army withdrawing or retreating into Paris (or its home box on Fronts B, C and F) loses the VPs of the spaces it leaves, and an Allied Army entering or leaving Paris changes nothing. The Grande Armée's automatic move into Paris is a block move too, so the Track A spaces it abandons are scored as captured by the Allies, as the rule says.
- *Return markers: battle over* no longer applies space VPs (the block moves do), so nothing is counted twice. The end-of-battle report now says the VPs follow the block moves.
- Not covered: the Scheldt (British 3 VP, optional rule 15.3) is not on a Front's step track, so its VPs stay manual. Games saved before a63 work as they are: the VPs come from the spaces a block leaves and enters, not from a stored total.

## 2.0.0a62 (not released; superseded by a63)

Everything in 2.0.0a61 below, plus:

- **Start-up alert** (Mark, 27 Nov 2026): starting a game could show "A Military Operation in the War of 1812 Box needs at least one of your units or fleets there [13.1]". The a61 placement checks also ran when the module itself moved markers during setup, before the units were in place. The rule checks and the Front B warning now apply only from the Conference on, when players place Military Operations. Setup moves are left alone, as in a60.

## 2.0.0a61 (not released; superseded by a62)

Builds on 2.0.0a60 (not yet released). **Load your game, then run Tools > Refresh Counters** (defaults) so existing pieces pick up the Military Operation checks.

- **Environment Table, 2nd die**: the 2nd die could be rolled right after the 1st roll, before the National card it called for had been drawn. It now unlocks only once that card is drawn (the chat says so), or straight away when no draw is due.
- **Military Operations dragged to a front** now meet the same rule restrictions as the right-click Front commands. A marker dropped where the rules forbid it goes back and an alert gives the reason: the Armistice (no Military Operation on Fronts A and B or in Denmark/Norway [13.1]), Austria not at war (Front F, and Austria on Front A [12.4.2]), France never attacking Sicily from Naples [13.1], Britain in Sicily without a British unit and a fleet [13.6.3], Britain on Front B without a fleet in the Scheldt, the War of 1812 Box (ended, or none of your units there) and Denmark/Norway without both sides present. A marker dragged straight from a National Track onto a front is now checked too (it used to skip every check, including side and one per Army/Box). A rejected move no longer registers the marker on the front it was dropped on.
- **Paired fronts** [13.6.1], as printed on the map: Britain cannot place a Military Operation to attack Gascony until the Coalition occupies Valencia, or Toulouse until it occupies Catalonia (Front D). This applies to both dragging and the right-click Front C command, because Front D is fought after Front C. A Russian Military Operation to attack Hanover is still allowed without Saxony, because Front A is fought first and may take it. It now brings a warning. If Saxony is still not occupied when Front B is chosen in the battle menu, the Russian Military Operation goes back to the Diplomacy Display and the chat says why [13.6.1.4]. Front B is then cancelled, unless France also has a Military Operation there, in which case the battle goes ahead for the French attack.
- **End of battle** [13.4.4-13.4.6]: the battle track is still played by hand. When the dice are done, *End of battle: read the battle track* (battle menu) works through the post-battle steps in order:
  1. It reads the losses each side inflicts from the battle track under each pawn, names the winner (or a draw, or who withdrew) and says how many units each side removes.
  2. **Major Battle VP**: if both sides started with 4 or more units (Silesia and Bohemia counted together on Front A), nobody withdrew and it is not the War of 1812 Box, the winner gains 1 VP and the loser loses 1 VP, or 2 when the Napoleon card was played in the battle. On Front A both Russia and Austria (when at war) score. The VP markers move by themselves and the chat shows each change.
  3. **Holding the mountains**: *France holds the mountains* / *Coalition holds the mountains* now opens only when it is allowed: the loser defends in a mountain space, nobody withdrew, the losses differ by exactly one and at least one unit would remain. Pressing it logs the extra loss and the cancelled retreat.
  4. It says who retreats and who advances (or that nobody moves), and which space changes hands. The players move the blocks.
  5. *Return markers: battle over* (a61/a62 only; from a63 the block moves do this) applied the space VPs [13.5] for the space that changed hands (none if the mountains were held), then sends the Front's Military Operations to the Diplomacy Display and its Military Support markers to the Force Pools, which locks the Front as before. A black VP number goes to the winner and is lost by the loser. A coloured one (Silesia and Prussia for Russia, Venice for Austria, Scheldt and Naples for Britain) counts only for that power. Castile's 2VP\* and Naples' Austrian 2VP† are end-of-turn VPs and are not touched.
- **Free French Military Operation** [12.4.4]: when the Conference ends with Napoleon available for the War Phase, one French Military Operation not won on a National Track now goes to Paris by itself, from the Diplomacy Display or else the Negotiation Table, and the chat says so. Before, the chat only reminded France to move it by hand. Only one goes, and none if a free one is already in Paris.
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
