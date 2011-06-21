#!/usr/bin/env python3

from analysis.reorder import WriteUseValuer

def test(size, visible, breaking, rprob, wprob, rand, valuer):
    for testno in range(5):
        stats = create_statements(size, visible=visible, breaking=breaking, rprob=rprob, wprob=wprob)
        #printSource(stats, PrettyWriter)
        time = timed_reorder(stats, timeout, rand, valuer)
        print(",".join(str(x) for x in [size,visible,breaking,rprob,wprob,rand,valuer.__class__.__name__,testno+1,time]))

if __name__ == "__main__":
    from writer.prettywriter import PrettyWriter
    from writer.sourcewriter import printSource
    from testing.reorder import *

    timeout = 30*60

    print("size,visible,breaking,rprob,wprob,rand,valuer,testno,time")

    for i in range(1, 11):
        for rprob in [0.1, 0.5, 0.9]:
            for wprob in [0.1, 0.5, 0.9]:
                for visible in [0.1, 0.5]:
                    for breaks in [0.1, 0.5]:
                        for rand in [True, False]:
                            for valuer in [None, WriteUseValuer]:
                                test(i, visible, breaks, rprob, wprob, rand, valuer)
