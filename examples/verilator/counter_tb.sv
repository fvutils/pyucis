// Testbench for counter module
module counter_tb;
    logic       clk;
    logic       rst_n;
    logic       enable;
    logic       load;
    logic [7:0] load_value;
    logic [7:0] count;
    logic       overflow;

    // Instantiate the counter
    counter #(.WIDTH(8)) dut (
        .clk(clk),
        .rst_n(rst_n),
        .enable(enable),
        .load(load),
        .load_value(load_value),
        .count(count),
        .overflow(overflow)
    );

    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Test stimulus
    initial begin
        // Initialize signals
        rst_n = 0;
        enable = 0;
        load = 0;
        load_value = 0;

        // Apply reset
        repeat(2) @(posedge clk);
        rst_n = 1;
        @(posedge clk);

        // Test 1: Basic counting
        $display("Test 1: Basic counting");
        enable = 1;
        repeat(20) @(posedge clk);

        // Test 2: Load operation
        $display("Test 2: Load operation");
        enable = 0;  // Disable first
        @(posedge clk);
        load = 1;
        load_value = 8'd100;
        @(posedge clk);
        load = 0;
        @(posedge clk);  // Wait one more cycle
        enable = 1;  // Now enable
        repeat(10) @(posedge clk);

        // Test 3: Disable counting
        $display("Test 3: Disable counting");
        enable = 0;
        repeat(5) @(posedge clk);

        // Test 4: Load while disabled, then enable
        $display("Test 4: Load then enable");
        enable = 0;
        load = 1;
        load_value = 8'd200;
        @(posedge clk);
        load = 0;
        @(posedge clk);
        enable = 1;
        repeat(10) @(posedge clk);

        // Test 5: Count to overflow
        $display("Test 5: Count to overflow");
        load = 1;
        load_value = 8'd250;
        @(posedge clk);
        load = 0;
        enable = 1;
        repeat(10) @(posedge clk);

        // Test 6: Multiple overflow events
        $display("Test 6: Multiple overflow events");
        repeat(20) @(posedge clk);

        // Test 7: Random operations
        $display("Test 7: Random operations");
        repeat(50) begin
            load = $urandom_range(0, 1);
            if (load) load_value = $urandom;
            enable = $urandom_range(0, 1);
            @(posedge clk);
        end

        // Finish simulation
        repeat(5) @(posedge clk);
        $display("Simulation completed successfully!");
        $finish;
    end

    // Monitor outputs
    initial begin
        $display("Time\tRst\tEnable\tLoad\tLoad_Val\tCount\tOverflow");
        $monitor("%0t\t%b\t%b\t%b\t%d\t\t%d\t%b",
                 $time, rst_n, enable, load, load_value, count, overflow);
    end

endmodule
