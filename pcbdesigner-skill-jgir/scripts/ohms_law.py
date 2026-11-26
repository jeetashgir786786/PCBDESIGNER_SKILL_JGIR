#!/usr/bin/env python3
"""Small transparent Ohm's-law calculator. Units: volts, amperes, ohms, watts."""
import argparse

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--voltage", type=float)
    p.add_argument("--current", type=float)
    p.add_argument("--resistance", type=float)
    args = p.parse_args()
    vals = [args.voltage, args.current, args.resistance]
    known = sum(v is not None for v in vals)
    if known != 2:
        p.error("Supply exactly two of --voltage, --current, --resistance")
    V, I, R = vals
    if V is not None and I is not None:
        if I == 0: p.error("Current must be non-zero to infer resistance")
        R = V/I
    elif V is not None and R is not None:
        if R == 0: p.error("Resistance must be non-zero")
        I = V/R
    else:
        V = I*R
    P = V*I
    print(f"V = {V:.9g} V")
    print(f"I = {I:.9g} A")
    print(f"R = {R:.9g} ohm")
    print(f"P = {P:.9g} W")

if __name__ == "__main__":
    main()
