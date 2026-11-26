# Analog & mixed-signal PCB guidance

## 1. Requirements
Signal range, bandwidth, source/load impedance, noise (nV/√Hz, µV rms in band), accuracy (offset, gain, INL), drift (ppm/°C), common-mode range, sampling rate, resolution (ENOB), isolation, calibration plan.

## 2. Circuit checks
- Op-amp: input common-mode and output swing at the actual rails, GBW for closed-loop gain/bandwidth, slew rate (SR ≥ 2π·f·Vpk), noise (voltage, current × source impedance, resistor thermal noise 4kTR), bias current × source R, capacitive-load stability (isolation resistor), phase margin.
- ADC: driver must settle to ½ LSB within acquisition time (charge-kickback RC at the input sized per ADC datasheet); anti-alias filter; reference noise, drive and decoupling (often 10 µF + 0.1 µF right at REF pin); input protection without adding leakage/nonlinearity.
- DAC/reference: load regulation, output buffer.
- Precision resistors: ratio-matched networks for gain; TCR; avoid thermocouple junctions (dissimilar metals) in µV circuits.

## 3. Layout
- One continuous ground plane; partition placement (analog zone, digital zone), route each zone's signals only within its region so return currents don't mix. Place the ADC/DAC straddling the boundary with AGND/DGND pins tied to the same plane at the part (per datasheet).
- Feedback components right at the op-amp pins; minimal area of high-impedance nodes; remove plane under high-Z nodes only if parasitic capacitance matters (and analyse it).
- Guard rings around ultra-high-impedance inputs (pA/fA), driven at the input common-mode voltage, both sides of the board, with mask opened; Teflon standoffs/slots for extreme cases; clean (no-flux-residue) process.
- Kelvin (4-wire) connections to shunts and references; route sense pairs together.
- Keep switching regulators, clocks and digital buses away; filter supplies (LDO/ferrite/RC) per zone; star point decoupling at each IC.
- Thermal: keep precision parts away from heat sources and airflow gradients; symmetric placement of matched parts (thermal gradients create offsets); copper balance around references.
- Shielding cans for sensitive front ends; differential routing for sensor lines; connector pin choices that place GND between sensitive signals.
- Leakage: conformal coating, cleanliness, humidity; guard and spacing for > 100 MΩ circuits.

## 4. Verification
Simulate (SPICE: noise, stability, transient, Monte-Carlo tolerances) and measure (noise floor with shorted input, FFT of ADC capture for SNR/SFDR/ENOB, temperature sweep).
