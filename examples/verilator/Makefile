# Makefile for Verilator simulation with coverage
VERILATOR = verilator
VERILATOR_FLAGS = -Wall -Wno-fatal
VERILATOR_COV_FLAGS = --coverage --coverage-line --coverage-toggle --coverage-user

# Directories
SRC_DIR = .
BUILD_DIR = obj_dir
COV_DIR = coverage

# Source files
SV_SOURCES = counter.sv counter_tb.sv

# Top module
TOP_MODULE = counter_tb

# Verilator build target
.PHONY: all
all: build

# Build the simulation with coverage using --binary flag
.PHONY: build
build:
	@echo "Building Verilator simulation with coverage..."
	$(VERILATOR) $(VERILATOR_FLAGS) $(VERILATOR_COV_FLAGS) \
		--binary -j 0 \
		--top-module $(TOP_MODULE) \
		$(SV_SOURCES)
	@echo "Build complete!"

# Run the simulation
.PHONY: run
run: build
	@echo "Running simulation..."
	@mkdir -p $(COV_DIR)
	./$(BUILD_DIR)/V$(TOP_MODULE)
	@echo "Simulation complete!"
	@echo "Coverage data saved to: coverage.dat"

# Convert Verilator coverage to UCIS SQLite format
.PHONY: convert
convert: run
	@echo "Converting Verilator coverage to UCIS SQLite format..."
	PYTHONPATH=$(shell cd ../.. && pwd)/src pyucis convert \
		--input-format vltcov --output-format sqlite \
		coverage.dat -o $(COV_DIR)/coverage.cdb
	@echo "Conversion complete! UCIS database: $(COV_DIR)/coverage.cdb"

# View the coverage database with PyUCIS TUI
.PHONY: view
view: convert
	@echo "Launching PyUCIS TUI..."
	pyucis view --input-format sqlite $(COV_DIR)/coverage.cdb

# Generate coverage report
.PHONY: report
report: convert
	@echo "Generating coverage report..."
	pyucis show summary --input-format sqlite $(COV_DIR)/coverage.cdb
	@echo ""
	@echo "Coverage hierarchy:"
	pyucis show hierarchy --input-format sqlite $(COV_DIR)/coverage.cdb

# Clean build artifacts
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR) coverage.dat logs
	@echo "Clean complete!"

# Clean everything including coverage database
.PHONY: distclean
distclean: clean
	@echo "Cleaning coverage database..."
	rm -rf $(COV_DIR)
	@echo "Distclean complete!"

# Help
.PHONY: help
help:
	@echo "Verilator Coverage Example - Makefile Targets"
	@echo "=============================================="
	@echo "  make build    - Build Verilator simulation with coverage"
	@echo "  make run      - Run simulation and generate coverage.dat"
	@echo "  make convert  - Convert coverage.dat to UCIS SQLite (.cdb)"
	@echo "  make view     - Launch PyUCIS TUI to view coverage"
	@echo "  make report   - Generate text coverage reports"
	@echo "  make clean    - Remove build artifacts"
	@echo "  make distclean- Remove everything including coverage DB"
	@echo "  make all      - Build (default target)"
	@echo ""
	@echo "Quick start: make run && make convert && make view"
