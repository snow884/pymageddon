"""Diagnostic run of the ecosystem: python tests/sim_report.py [epochs] [seed]"""

import random
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

import main  # noqa: E402
from common_utils import ecosystem  # noqa: E402
from singleton import realm  # noqa: E402

epochs = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
warmup = 300

from type_defs.objects.base_object import BaseObject  # noqa: E402
from type_defs.objects.effects.base_effect import BaseEffect  # noqa: E402

deaths = {}
_orig_die = BaseObject.die


def _traced_die(self, *args, **kwargs):
    cause = "other"
    frame = sys._getframe(1)
    for _ in range(5):
        if frame is None:
            break
        owner = frame.f_locals.get("self")
        if isinstance(owner, BaseEffect):
            cause = type(owner).__name__
            break
        frame = frame.f_back
    if not self.died_flag:
        key = (ecosystem.SPECIES_OF_TYPE.get(self.type_name, self.type_name), cause)
        deaths[key] = deaths.get(key, 0) + 1
        stage_key = (self.type_name, cause, self.hp <= 0)
        stage_deaths[stage_key] = stage_deaths.get(stage_key, 0) + 1
    return _orig_die(self, *args, **kwargs)


stage_deaths = {}


BaseObject.die = _traced_die

main.populate_map_full(100)
history = {s: [] for s in ecosystem.SPECIES}
t = time.time()
for _ in range(epochs):
    main.simulate_epoch()
    realm.EPOCH_COUNTER += 1
    if realm.EPOCH_COUNTER > warmup and realm.EPOCH_COUNTER % 10 == 0:
        for s, c in ecosystem.species_counts().items():
            history[s].append(c)

print(f"{epochs} epochs in {time.time() - t:.1f}s, capacity {ecosystem.capacity()}")
print(
    f"{'species':20s} {'mean':>6s} {'min':>4s} {'max':>4s} {'immig':>6s}"
    f" {'starve':>6s} {'eaten':>6s}"
)
for s, h in sorted(history.items(), key=lambda kv: statistics.mean(kv[1])):
    eaten = deaths.get((s, "EatObjectInFront"), 0) + deaths.get(
        (s, "EatObjectSteppingIn"), 0
    )
    print(
        f"{s:20s} {statistics.mean(h):6.1f} {min(h):4d} {max(h):4d}"
        f" {realm.IMMIGRATION_COUNTS.get(s, 0):6d}"
        f" {deaths.get((s, 'HpDepletion'), 0):6d} {eaten:6d}"
    )

if len(sys.argv) > 3:
    for sp in sys.argv[3].split(","):
        print(f"--- {sp}")
        for t in ecosystem.SPECIES[sp]:
            rows = {k: v for k, v in stage_deaths.items() if k[0] == t}
            print(" ", t, sorted(rows.items(), key=lambda kv: -kv[1]))

means = {s: statistics.mean(h) for s, h in history.items()}
total_deaths = sum(v for (s, c), v in deaths.items() if s in ecosystem.SPECIES)
print(
    f"SUMMARY mean range {min(means.values()):.1f}-{max(means.values()):.1f}"
    f" ratio {max(means.values()) / min(means.values()):.2f}"
    f" | abs min {min(min(h) for h in history.values())}"
    f" abs max {max(max(h) for h in history.values())}"
    f" | immigration {sum(realm.IMMIGRATION_COUNTS.values())}"
    f" vs deaths {total_deaths}"
)
