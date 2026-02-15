// Test 4: Reset Behavior - Tests reset functionality
// Covers: reset signal, initialization, reset during operation
module test_reset;
    logic clk = 0;
    logic rst_n;
    logic enable;
    logic load;
    logic [7:0] load_value;
    logic [7:0] count;
    logic overflow;
    
    // Clock generation
    always #5 clk = ~clk;
    
    // Instantiate counter
    counter dut (
        .clk(clk),
        .rst_n(rst_n),
        .enable(enable),
        .load(load),
        .load_value(load_value),
        .count(count),
        .overflow(overflow)
    );
    
    initial begin
        // Initialize
        rst_n = 0;
        enable = 0;
        load = 0;
        load_value = 0;
        
        $display("Test: Reset Behavior");
        
        // Test 1: Check reset state
        #15;
        if (count != 0) begin
            $display("ERROR: Counter not 0 during reset, got %d", count);
            $finish;
        end
        if (overflow != 0) begin
            $display("ERROR: Overflow not 0 during reset");
            $finish;
        end
        $display("  Initial reset state: PASS");
        
        // Release reset
        rst_n = 1;
        @(posedge clk);
        
        // Test 2: Count up, then reset
        enable = 1;
        repeat(50) @(posedge clk);
        
        if (count == 0) begin
            $display("ERROR: Counter didn't increment");
            $finish;
        end
        
        // Apply reset
        rst_n = 0;
        @(posedge clk);
        
        if (count != 0) begin
            $display("ERROR: Counter not reset to 0, got %d", count);
            $finish;
        end
        $display("  Reset during counting: PASS");
        
        // Test 3: Reset with overflow condition
        rst_n = 1;
        @(posedge clk);
        
        load = 1;
        load_value = 8'd255;
        @(posedge clk);
        load = 0;
        enable = 1;
        @(posedge clk);
        
        // Should have overflow
        if (!overflow) begin
            $display("ERROR: Overflow not set");
            $finish;
        end
        
        // Reset should clear overflow
        rst_n = 0;
        @(posedge clk);
        
        if (overflow != 0) begin
            $display("ERROR: Overflow not cleared by reset");
            $finish;
        end
        $display("  Reset clears overflow: PASS");
        
        // Test 4: Multiple reset cycles
        rst_n = 1;
        enable = 1;
        repeat(10) @(posedge clk);
        
        rst_n = 0;
        @(posedge clk);
        
        rst_n = 1;
        repeat(20) @(posedge clk);
        
        rst_n = 0;
        @(posedge clk);
        
        if (count != 0) begin
            $display("ERROR: Multiple resets failed");
            $finish;
        end
        $display("  Multiple reset cycles: PASS");
        
        $display("Test PASSED: Reset behavior correct");
        $finish;
    end
    
    // Timeout
    initial begin
        #10000;
        $display("ERROR: Test timeout");
        $finish;
    end
    
endmodule
