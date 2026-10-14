import sys, json, math; sys.path.insert(0, '/home/user/Uncharted-Horizons/design/simulator/power')
import redraw as RD, worlds as W
W.set_world(None)
EO = RD.EO; GAME = 320
hist = json.load(open('/home/user/Uncharted-Horizons/design/simulator/power/redraw_iterations.json'))
span = hist[-1]['span']; RD.apply(span); real, total = RD.measure(30)
for it in range(5):
    T = RD.fork_turns(span); pace = total / GAME
    proposed = {e: real[e] / pace for e in EO}
    target = {e: math.sqrt(T[e] * proposed[e]) for e in EO}          # move halfway, geometrically
    s = GAME / sum(target.values()); target = {e: v * s for e, v in target.items()}
    span = RD.span_for(target); end, T, price = RD.apply(span)
    real, total = RD.measure(30)
    p = {e: real[e] / T[e] for e in EO}
    spread = max(p.values()) - min(p.values())
    print(f"damped {it + 1}: {total:.0f} over {sum(T.values()):.0f}; spread {spread:.2f}; " + ' '.join(f"{e[:3]} {p[e]:.2f}" for e in EO))
    hist.append(dict(span=span, end=end, turns=T, price=price, real=real, total=total, spread=spread))
json.dump(hist, open('/home/user/Uncharted-Horizons/design/simulator/power/redraw_iterations.json', 'w'), indent=1)
