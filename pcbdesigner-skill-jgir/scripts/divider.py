#!/usr/bin/env python3
"""Ideal unloaded divider calculator; account for load and tolerance separately."""
import argparse
p=argparse.ArgumentParser(description=__doc__)
p.add_argument("--vin",type=float,required=True)
p.add_argument("--r1",type=float,required=True,help="Ohms from Vin to output")
p.add_argument("--r2",type=float,required=True,help="Ohms from output to ground")
a=p.parse_args()
if a.r1<=0 or a.r2<=0: p.error("Resistors must be positive")
vout=a.vin*a.r2/(a.r1+a.r2)
i=a.vin/(a.r1+a.r2)
print(f"Vout ideal unloaded = {vout:.9g} V")
print(f"Divider current = {i:.9g} A")
print(f"R1 dissipation = {i*i*a.r1:.9g} W")
print(f"R2 dissipation = {i*i*a.r2:.9g} W")
print("Warning: load impedance and resistor tolerance are not included.")
