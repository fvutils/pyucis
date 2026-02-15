# Makefile for Verilator simulation with coverage
VERILATOR = verilator
VERILATOR_FLAGS = -Wall -Wno-fatal
VERILATOR_COV_FLAGS = --coverage --coverage-line --coverage-toggle --coverage-user

# Directories
SRC_DIR = .
BUILD_DIR = obj_dir
COV_DIR = coverage

# Source files
SV_SOURCES = counter.sv
TEST_SOURCES = counter_tb.sv test_basic_counting.sv test_load_operations.sv test_overflow.sv test_reset.sv

# Test names
TESTS = counter_tb test_basic_counting test_load_operations test_overflow test_reset

# Verilator build target
.PHONY: all
all: build

# Build all test executables
.PHONY: build
build:
	@echo "Building all test simulations with coverage..."
	@for test in $(TESTS); do \
		echo "  Building $$test..."; \
		$(VERILATOR) $(VERILATOR_FLAGS) $(VERILATOR_COV_FLAGS) \
			--binary -j 0 \
			--top-module $$test \
			$(SV_SOURCES) $$test.sv || exit 1; \
	done
	@echo "Build complete!"

# Run all tests and collect separate coverage files
.PHONY: run-all
run-all: build
	@echo "Running all tests and collecting coverage..."
	@mkdir -p $(COV_DIR)
	@for test in $(TESTS); do \
		echo ""; \
		echo "================================================="; \
		echo "Running $$test..."; \
		echo "================================================="; \
		./$(BUILD_DIR)/V$$test || exit 1; \
		mv coverage.dat $(COV_DIR)/$$test.dat; \
		echo "Coverage saved to: $(COV_DIR)/$$test.dat"; \
	done
	@echo ""
	@echo "All tests complete!"
	@echo "Coverage files:"
	@ls -lh $(COV_DIR)/*.dat

# Convert all coverage files to separate UCIS databases
.PHONY: convert-all
convert-all: run-all
	@echo "Converting all coverage files to UCIS SQLite format..."
	@for test in $(TESTS); do \
		echo "  Converting $$test.dat..."; \
		PYTHONPATH=$(shell cd ../.. && pwd)/src pyucis convert \
			--input-format vltcov --output-format sqlite \
			$(COV_DIR)/$$test.dat -o $(COV_DIR)/$$test.cdb || exit 1; \
	done
	@echo "Conversion complete!"
	@echo "Individual databases:"
	@ls -lh $(COV_DIR)/*.cdb

# Merge all coverage databases into one
.PHONY: merge
merge: convert-all
	@echo "Merging all coverage databases..."
	PYTHONPATH=$(shell cd ../.. && pwd)/src pyucis merge \
		--input-format sqlite --output-format sqlite \
		-o $(COV_DIR)/merged.cdb \
		$(COV_DIR)/counter_tb.cdb \
		$(COV_DIR)/test_basic_counting.cdb \
		$(COV_DIR)/test_load_operations.cdb \
		$(COV_DIR)/test_overflow.cdb \
		$(COV_DIR)/test_reset.cdb
	@echo "Merge complete! Database: $(COV_DIR)/merged.cdb"

# Run single test (use TEST=<name>)
.PHONY: run
run:
ifndef TEST
	@echo "Error: Please specify TEST=<name>"
	@echo "Available tests: $(TESTS)"
	@exit 1
endif
	@echo "Building and running $(TEST)..."
	$(VERILATOR) $(VERILATOR_FLAGS) $(VERILATOR_COV_FLAGS) \
		--binary -j 0 \
		--top-module $(TEST) \
		$(SV_SOURCES) $(TEST).sv
	@mkdir -p $(COV_DIR)
	./$(BUILD_DIR)/V$(TEST)
	@mv coverage.dat $(COV_DIR)/$(TEST).dat
	@echo "Coverage saved to: $(COV_DIR)/$(TEST).dat"

# Build the simulation with coverage using --binary flag (original test)
.PHONY: build-original
build-original:
	@echo "Building original counter_tb with coverage..."
	$(VERILATOR) $(VERILATOR_FLAGS) $(VERILATOR_COV_FLAGS) \
		--binary -j 0 \
		--top-module counter_tb \
		$(SV_SOURCES) counter_tb.sv
	@echo "Build complete!"

# Run the original simulation
.PHONY: run-original
run-original: build-original
	@echo "Running original simulation..."
	@mkdir -p $(COV_DIR)
	./$(BUILD_DIR)/Vcounter_tb
	@mv coverage.dat $(COV_DIR)/counter_tb.dat
	@echo "Simulation complete!"
	@echo "Coverage data saved to: $(COV_DIR)/counter_tb.dat"

# Convert original coverage to UCIS SQLite format
.PHONY: convert
convert: run-original
	@echo "Converting Verilator coverage to UCIS SQLite format..."
	PYTHONPATH=$(shell cd ../.. && pwd)/src pyucis convert \
		--input-format vltcov --output-format sqlite \
		$(COV_DIR)/counter_tb.dat -o $(COV_DIR)/counter_tb.cdb
	@echo "Conversion complete! UCIS database: $(COV_DIR)/counter_tb.cdb"

# View the merged coverage database with PyUCIS TUI
.PHONY: view
view: merge
	@echo "Launching PyUCIS TUI for merged database..."
	pyucis view --input-format sqlite $(COV_DIR)/merged.cdb

# View individual test coverage
.PHONY: view-test
view-test:
ifndef TEST
	@echo "Error: Please specify TEST=<name>"
	@echo "Available tests: $(TESTS)"
	@exit 1
endif
	@echo "Launching PyUCIS TUI for $(TEST)..."
	pyucis view --input-format sqlite $(COV_DIR)/$(TEST).cdb

# Generate coverage report for merged database
.PHONY: report
report: merge
	@echo "Generating coverage report for merged database..."
	@echo ""
	@echo "======================================"
	@echo "Test Execution Summary"
	@echo "======================================"
	@pyucis show tests --input-format sqlite $(COV_DIR)/merged.cdb | grep -v "PyUCIS\|====\|Skill\|Note\|For more" | grep -A1000 "{"
	@echo ""
	@echo "======================================"
	@echo "Code Coverage Summary"  
	@echo "======================================"
	@PYTHONPATH=$(shell cd ../.. && pwd)/src python3 report_coverage.py $(COV_DIR)/merged.cdb
	@echo ""
	@echo "For detailed test contribution analysis, run: make query-tests"

# Query test coverage information
.PHONY: query-tests
query-tests: merge
	@echo "Querying test coverage information..."
	@echo ""
	@echo "Test Coverage Summary:"
	@echo "======================"
	PYTHONPATH=$(shell cd ../.. && pwd)/src python3 -c "\
from ucis.sqlite import SqliteUCIS; \
from ucis.history_node_kind import HistoryNodeKind; \
db = SqliteUCIS.open_readonly('$(COV_DIR)/merged.cdb'); \
tests = list(db.historyNodes(HistoryNodeKind.TEST)); \
print(f'Total tests: {len(tests)}'); \
print(''); \
for test in tests: \
    print(f'  {test.getLogicalName()}'); \
db.close()"

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
	@echo "Verilator Multi-Test Coverage Example - Makefile Targets"
	@echo "=========================================================="
	@echo ""
	@echo "Multi-Test Workflow:"
	@echo "  make run-all      - Run all tests and generate coverage files"
	@echo "  make convert-all  - Convert all coverage to UCIS databases"
	@echo "  make merge        - Merge all databases into merged.cdb"
	@echo "  make view         - View merged coverage in PyUCIS TUI"
	@echo "  make report       - Generate coverage report"
	@echo "  make query-tests  - Show test coverage information"
	@echo ""
	@echo "Single Test Workflow:"
	@echo "  make run TEST=<name>      - Run specific test"
	@echo "  make view-test TEST=<name>- View specific test coverage"
	@echo ""
	@echo "Available tests:"
	@echo "  counter_tb            - Original comprehensive test"
	@echo "  test_basic_counting   - Basic increment functionality"
	@echo "  test_load_operations  - Load signal testing"
	@echo "  test_overflow         - Overflow detection"
	@echo "  test_reset            - Reset behavior"
	@echo ""
	@echo "Other:"
	@echo "  make build        - Build all test executables"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make distclean    - Remove everything including coverage DB"
	@echo ""
	@echo "Quick start: make merge && make view"

