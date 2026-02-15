// Test 3: Overflow Testing - Tests overflow detection and wraparound
// Covers: overflow flag, counting past 255, wraparound behavior
module test_overflow;
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
        
        $display("Test: Overflow Detection");
        
        // Test 1: Count to overflow
        #10 load = 1;
        load_value = 8'd250;
        @(posedge clk);
        load = 0;
        enable = 1;
        @(posedge clk);
        
        // Count from 250 to 255 (no overflow yet)
        repeat(5) begin
            @(posedge clk);
            if (overflow) begin
                $display("ERROR: Premature overflow at count=%d", count);
                $finish;
            end
        end
        
        if (count != 255) begin
            $display("ERROR: Expected count=255, got %d", count);
            $finish;
        end
        $display("  Count to 255: PASS");
        
        // Next clock should overflow
        @(posedge clk);
        if (!overflow) begin
            $display("ERROR: Overflow flag not set");
            $finish;
        end
        if (count != 0) begin
            $display("ERROR: Counter didn't wrap to 0, got %d", count);
            $finish;
        end
        $display("  Overflow to 0: PASS");
        
        // Test 2: Multiple overflows
        @(posedge clk);
        if (overflow) begin
            $display("ERROR: Overflow stuck high");
            $finish;
        end
        
        // Count through another full cycle
        load = 1;
        load_value = 8'd253;
        @(posedge clk);
        load = 0;
        @(posedge clk);
        
        // Should overflow in 3 cycles
        repeat(2) @(posedge clk);
        if (overflow) begin
            $display("ERROR: Early overflow in second cycle");
            $finish;
        end
        
        @(posedge clk);
        if (!overflow) begin
            $display("ERROR: Second overflow not detected");
            $finish;
        end
        $display("  Multiple overflows: PASS");
        
        // Test 3: Overflow doesn't happen when disabled
        load = 1;
        load_value = 8'd255;
        @(posedge clk);
        load = 0;
        enable = 0;
        @(posedge clk);
        @(posedge clk);
        
        if (count != 255) begin
            $display("ERROR: Counter changed while disabled");
            $finish;
        end
        if (overflow) begin
            $display("ERROR: Overflow occurred while disabled");
            $finish;
        end
        $display("  No overflow when disabled: PASS");
        
        $display("Test PASSED: Overflow detection works correctly");
        $finish;
    end
    
    // Timeout
    initial begin
        #10000;
        $display("ERROR: Test timeout");
        $finish;
    end
    
endmodule
