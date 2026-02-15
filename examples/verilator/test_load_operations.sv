// Test 2: Load Operations - Tests load functionality thoroughly
// Covers: load signal, load_value usage, interaction with enable
module test_load_operations;
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
        
        // Release reset
        #15 rst_n = 1;
        
        $display("Test: Load Operations");
        
        // Test 1: Load while disabled
        #10 load = 1;
        load_value = 8'd42;
        @(posedge clk);
        load = 0;
        @(posedge clk);
        
        if (count != 42) begin
            $display("ERROR: Load failed, expected 42, got %d", count);
            $finish;
        end
        $display("  Load while disabled: PASS");
        
        // Test 2: Load while enabled (load takes priority)
        enable = 1;
        repeat(5) @(posedge clk);  // Count a bit
        
        load = 1;
        load_value = 8'd100;
        @(posedge clk);
        load = 0;
        @(posedge clk);
        
        if (count != 101) begin  // Should be 100 + 1 (one count after load)
            $display("ERROR: Load during enable failed, expected 101, got %d", count);
            $finish;
        end
        $display("  Load while enabled: PASS");
        
        // Test 3: Multiple loads
        load = 1;
        load_value = 8'd200;
        @(posedge clk);
        load_value = 8'd150;
        @(posedge clk);
        load = 0;
        @(posedge clk);
        
        if (count != 151) begin  // Should be 150 + 1
            $display("ERROR: Multiple loads failed, expected 151, got %d", count);
            $finish;
        end
        $display("  Multiple loads: PASS");
        
        // Test 4: Load at boundaries
        enable = 0;
        load = 1;
        load_value = 8'd255;  // Max value
        @(posedge clk);
        load = 0;
        @(posedge clk);
        
        if (count != 255) begin
            $display("ERROR: Load max value failed");
            $finish;
        end
        $display("  Load max value: PASS");
        
        load = 1;
        load_value = 8'd0;  // Min value
        @(posedge clk);
        load = 0;
        @(posedge clk);
        
        if (count != 0) begin
            $display("ERROR: Load min value failed");
            $finish;
        end
        $display("  Load min value: PASS");
        
        $display("Test PASSED: All load operations work correctly");
        $finish;
    end
    
    // Timeout
    initial begin
        #10000;
        $display("ERROR: Test timeout");
        $finish;
    end
    
endmodule
