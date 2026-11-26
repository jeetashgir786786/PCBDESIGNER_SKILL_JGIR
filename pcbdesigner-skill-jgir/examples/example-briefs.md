# Example project briefs

## Beginner: sensor interface board
Create a board interfacing a 3.3 V MCU to a temperature sensor, with USB power, connector, ESD protection, test points, and an explicit board-size constraint. Ask for missing requirements and produce a schematic/layout plan.

## Intermediate: buck converter
Design a non-isolated buck converter with specified input range, output voltage/current, ripple, efficiency, thermal environment, and size. Calculate stresses, choose components from datasheets, and provide layout-critical guidance.

## Advanced: motor driver
Design a motor driver with defined motor, bus, current, PWM, protection, thermal, control interface, and enclosure. Include fault analysis and clearly distinguish calculated from simulated/tested performance.

## Expert: 24-layer compute carrier
Design the stackup, constraints and layout plan for a 24-layer board carrying a 2,000+ ball 1.0 mm-pitch FPGA, two DDR5 memory-down channels, 16 lanes of PCIe Gen5 to a CEM edge connector (1.57 mm finger thickness constraint — discuss), 4× 25G SFP28, and a 0.8 V / 60 A core rail. Select materials (hybrid allowed), compute thickness and aspect ratio, back-drill plan, channel loss budgets, PDN targets, and produce a fab-ready stackup spec and verification plan.

## Expert: 0.4 mm-pitch HDI wearable
Design a 10-layer 3+4+3 HDI board for a 0.4 mm-pitch application processor with LPDDR4X, Wi-Fi/BLE chip antenna and a flex tail. Decide stacked vs staggered microvias, via-in-pad types, impedance on thin build-up layers, and confirm fab capability.
