#!/usr/bin/env python3
"""Build "Make All Sims Heterosexual" - a Sims 4 tuning mod.

Sets a heterosexual baseline for every adult human Sim exactly once, then never
touches them again, so hand-picked exceptions stick.

How it works
------------
Lot51 Core's TuningInjector attaches a hidden Buff to the four adult age traits.
The Buff's _loot_on_instance fires a LootActions that rewrites the Sim's
attraction and WooHoo-interest traits, and finally adds a hidden marker trait.
Both loots blacklist that marker, so a converted Sim is skipped forever.

Confirmed in game: _loot_on_instance is the hook that fires for a trait-injected
buff; _loot_on_addition alone never fires in that delivery path.

All resources are generated. No third-party bytes are embedded - the SimData is
built from EA's published schema by tools/simdata.py, and `python build.py
--audit` fails the build if any foreign identifier appears in the output.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools'))
import dbpf                                                       # noqa: E402
import simdata                                                    # noqa: E402

CREATOR = "Ghost World Tourist"
NS = "gwt"
OUT = "GhostWorldTourist_MakeAllSimsHeterosexual.package"

# Identifiers that must never appear in a built package. The mod began life
# reusing SimData copied from other creators; this gate keeps that from
# regressing.
# The builder's own account name must never ship either.
FORBIDDEN = ["PECO", "Andirz", "CindyRotique", "MakePansexual", os.path.basename(os.path.expanduser("~"))]

LOOT_M = simdata.fnv64(f"{NS}:Loot_Hetero_Male")
LOOT_F = simdata.fnv64(f"{NS}:Loot_Hetero_Female")
BUFF = simdata.fnv64(f"{NS}:Buff_Hidden_Hetero")
INJ = simdata.fnv64(f"{NS}:INJECTOR_Hetero")
MARK = simdata.fnv64(f"{NS}:trait_HeteroBaselineApplied")

# EA sexual-orientation trait ids
EXPLORING, NOT_EXPLORING = 276496, 276497
ATTR_F, ATTR_M, ATTR_NOT_F, ATTR_NOT_M = 276492, 276493, 276494, 276495
WH_M, WH_F, WH_NOT_F, WH_NOT_M = 291674, 291675, 292092, 292093

AGE_TRAITS = [(34317, 'teen'), (34318, 'youngAdult'),
              (34319, 'adult'), (34320, 'elder')]

# A Sim already in a committed romance is left alone: converting them could
# invalidate a relationship the player built.
ROMANTIC_BITS = [(15816, 'Engaged'), (15818, 'GettingMarried'), (15822, 'Married'),
                 (15825, 'Significant_Other'), (99429, 'Promised'),
                 (274846, 'Married_Newlywed'), (491011, 'SecretLover')]


def add(tid, comment):
    return (f'    <V t="trait_add">\n      <U n="trait_add">\n'
            f'        <T n="trait">{tid}<!--{comment}--></T>\n'
            f'        <E n="subject">Actor</E>\n      </U>\n    </V>\n')


def remove(tid, comment):
    return (f'    <V t="trait_remove">\n      <U n="trait_remove">\n'
            f'        <V n="trait" t="specific_trait">\n          <U n="specific_trait">\n'
            f'            <T n="specific_trait">{tid}<!--{comment}--></T>\n'
            f'          </U>\n        </V>\n        <E n="subject">Actor</E>\n'
            f'      </U>\n    </V>\n')


def loot(inst, name, gender):
    if gender == 'MALE':
        on = (ATTR_F, ATTR_NOT_M, WH_F, WH_NOT_M)
        off = (ATTR_M, ATTR_NOT_F, WH_M, WH_NOT_F)
    else:
        on = (ATTR_M, ATTR_NOT_F, WH_M, WH_NOT_F)
        off = (ATTR_F, ATTR_NOT_M, WH_F, WH_NOT_M)
    body = (remove(EXPLORING, 'Sexuality_Exploring')
            + ''.join(remove(t, 'opposite of target orientation') for t in off)
            + add(NOT_EXPLORING, 'Sexuality_NotExploring')
            + ''.join(add(t, 'target orientation') for t in on)
            + add(MARK, 'marker - converted once, never again'))
    bits = ''.join(f'              <T>{i}<!--romantic-{n}--></T>\n'
                   for i, n in ROMANTIC_BITS)
    return f'''<?xml version="1.0" encoding="utf-8"?>
<I c="LootActions" i="action" m="interactions.utils.loot" n="{name}" s="{inst}">
  <L n="loot_actions">
{body}  </L>
  <L n="tests">
    <L>
      <V t="sim_info">
        <U n="sim_info">
          <V n="ages" t="specified">
            <L n="specified">
              <E>TEEN</E>
              <E>YOUNGADULT</E>
              <E>ADULT</E>
              <E>ELDER</E>
            </L>
          </V>
          <V n="species" t="specified">
            <U n="specified">
              <L n="species">
                <E>HUMAN</E>
              </L>
            </U>
          </V>
          <V n="gender" t="specified">
            <E n="specified">{gender}</E>
          </V>
          <E n="who">Actor</E>
        </U>
      </V>
      <V t="trait">
        <U n="trait">
          <L n="blacklist_traits">
            <T>{MARK}<!--already converted--></T>
          </L>
        </U>
      </V>
      <V t="relationship">
        <U n="relationship">
          <T n="num_relations">0</T>
          <U n="prohibited_relationship_bits">
            <L n="match_any">
{bits}            </L>
          </U>
          <L n="subject">
            <E>Actor</E>
          </L>
          <L n="target_sim">
            <E>AllRelationships</E>
          </L>
        </U>
      </V>
    </L>
  </L>
</I>
'''


TRAIT_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<I c="Trait" i="trait" m="traits.traits" n="{NS}:trait_HeteroBaselineApplied" s="{MARK}">
  <E n="trait_type">HIDDEN</E>
  <V n="ui_category" t="disabled" />
</I>
'''

BUFF_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<I c="Buff" i="buff" m="buffs.buff" n="{NS}:Buff_Hidden_Hetero" s="{BUFF}">
  <L n="_loot_on_addition">
    <T>{LOOT_M}</T>
    <T>{LOOT_F}</T>
  </L>
  <L n="_loot_on_instance">
    <T>{LOOT_M}</T>
    <T>{LOOT_F}</T>
  </L>
  <T n="icon" p="InGame\\UI\\Icons\\Debug\\missing_image.png">2f7d0004:00000000:30f0846c783606f9</T>
  <T n="visible">False</T>
</I>
'''

rows = ''.join(f'''    <U>
      <T n="trait">{tid}<!--trait_{nm}--></T>
      <L n="buffs">
        <U>
          <T n="buff_type">{BUFF}</T>
        </U>
      </L>
    </U>
''' for tid, nm in AGE_TRAITS)

INJECTOR_XML = f'''<?xml version="1.0" encoding="utf-8"?>
<I c="TuningInjector" i="snippet" m="lot51_core.snippets.injector" n="{NS}:INJECTOR_Hetero" s="{INJ}">
  <T n="minimum_core_version">1.17</T>
  <T n="mod_name">Make All Sims Heterosexual</T>
  <T n="creator_name">{CREATOR}</T>
  <L n="inject_to_traits">
{rows}  </L>
</I>
'''


def build(out=OUT):
    resources = [
        (dbpf.T_TRAIT, 0, MARK, TRAIT_XML.encode()),
        (dbpf.T_SIMDATA, dbpf.SIMDATA_GROUP[dbpf.T_TRAIT], MARK,
         simdata.build_trait(f"{NS}:trait_HeteroBaselineApplied")),
        (dbpf.T_LOOT, 0, LOOT_M, loot(LOOT_M, f"{NS}:Loot_Hetero_Male", "MALE").encode()),
        (dbpf.T_LOOT, 0, LOOT_F, loot(LOOT_F, f"{NS}:Loot_Hetero_Female", "FEMALE").encode()),
        (dbpf.T_BUFF, 0, BUFF, BUFF_XML.encode()),
        (dbpf.T_SIMDATA, dbpf.SIMDATA_GROUP[dbpf.T_BUFF], BUFF,
         simdata.build_buff(f"{NS}:Buff_Hidden_Hetero")),
        (dbpf.T_SNIPPET, 0, INJ, INJECTOR_XML.encode()),
    ]
    n, size = dbpf.write(out, resources)
    print(f"wrote {out}  ({n} resources, {size} bytes)")
    print(f"  marker trait id: {MARK}  (0x{MARK:016X})")
    return out


def audit(path):
    hits = dbpf.audit(path, FORBIDDEN)
    if hits:
        print("AUDIT FAILED - foreign identifiers present:")
        for k, where in hits.items():
            print(f"   {k!r} in {where}")
        return 1
    print(f"audit OK - none of {FORBIDDEN} appear in {path}")
    return 0


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--audit', action='store_true', help='verify then exit nonzero on failure')
    a = ap.parse_args()
    p = build(a.out)
    sys.exit(audit(p) if a.audit else 0)
