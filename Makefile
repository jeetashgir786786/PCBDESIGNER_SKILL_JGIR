.PHONY: help lint test validate package check example clean

SKILL := pcbdesigner-skill-jgir
KA    := $(SKILL)/scripts/kicad_auto
OUT   ?= /tmp/pcbdesigner_example

help:            ## Show this help
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

lint:            ## Ruff lint (Python)
	ruff check .

test:            ## Unit tests (no KiCad needed)
	pytest -q

validate:        ## Validate SKILL.md frontmatter and folder hygiene
	python3 tools/package_skill.py --check-only

package:         ## Build dist/<skill>-v<version>.zip for upload to Claude
	python3 tools/package_skill.py

check: lint test validate   ## Everything CI runs

example:         ## End-to-end KiCad pipeline on the bundled example (needs KiCad + Freerouting)
	cd $(KA) && ./pipeline.sh examples/usb_uart_spec.py $(OUT) 20 1

clean:           ## Remove build output and caches
	rm -rf dist .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
