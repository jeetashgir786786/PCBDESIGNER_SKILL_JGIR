# MCU / SoC / embedded PCB design

## 1. Before schematic
- Exact orderable variant (package, flash/RAM, temperature grade, radio variant), errata, hardware design guide / reference design (e.g. STM32 AN, ESP32 Hardware Design Guidelines, nRF reference layouts, RP2040/RP2350 hardware design, NXP i.MX HW guides).
- Pin-mux plan in the vendor tool (STM32CubeMX, MCUXpresso, ESP pin lists) exported and checked against the schematic; strapping/boot pins identified.

## 2. Schematic essentials
- Every VDD/VDDA/VBAT/VDDIO pin with its datasheet decoupling (typ. 100 nF per pin + bulk 4.7–10 µF per rail; VDDA via ferrite/RC per guide; VCAP/VCORE pins with exact cap values/ESR).
- Reset: RC + ESD-safe button, supervisor if brown-out matters; correct pull-ups.
- Clocks: crystal with load caps (C = 2·(CL − Cstray), Cstray ≈ 2–5 pF), check drive level and negative resistance margin (≥ 5×); 32.768 kHz crystals are very sensitive — very short traces, guard.
- Boot/strapping pins: defined at reset regardless of attached peripherals (watch pins shared with LEDs/peripherals).
- Debug: SWD/JTAG header (or Tag-Connect TC2030 footprint), UART console, BOOT button.
- USB: D+/D− with series R if required by the MCU, ESD diode, VBUS sense divider, CC 5.1 kΩ pull-downs for Type-C sink.
- GPIO: check voltage tolerance (5 V tolerant only when powered?), current limits per pin and per port, analog pins not 5 V tolerant.
- Wireless SoC/module: RF matching network per reference; antenna choice; regulatory (module certification grant conditions — antenna type/gain, layout).

## 3. Layout essentials
- Decoupling caps on the same side as the MCU, as close as possible to each power pin, with the via going straight to the plane (cap → pin first, then via).
- Exposed pad (EP) to GND with via array; QFN EP paste windowpane.
- Crystal directly next to the pins, symmetric short traces, GND pour beneath on L1 stitched to L2, no other signals near/under it.
- Separate the RF section (see rf-layout.md); follow the module's keepout and placement (antenna at board edge).
- SMPS for the MCU core (e.g. ESP32-S3 / nRF54 DC-DC inductors): place inductor and caps exactly as the reference layout.
- Keep high-speed peripherals (QSPI/OSPI flash/PSRAM, SDIO, RMII/RGMII, USB HS) short and length-matched as specified, with GND reference.
- Debug/programming connector accessible; test points for rails, reset, boot, UART TX/RX.

## 4. Bring-up plan (put in the deliverables)
Power rails with current-limited supply → check rail voltages/ripple → clock (scope at crystal output with low-C probe or via MCO pin) → debugger connection → flash test firmware → peripheral-by-peripheral tests → RF conducted test → full system.
