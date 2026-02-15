// Test 1: Basic Counting - Tests basic increment functionality
// Covers: enable signal, basic counting, minimal load usage
module test_basic_counting;
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
        
        // Test 1: Basic counting from 0
        $display("Test: Basic Counting");
        #10 enable = 1;
        
        // Count to 50
        repeat(50) begin
            @(posedge clk);
        end
        
        // Verify we counted
        if (count != 50) begin
            $display("ERROR: Expected count=50, got %d", count);
            $finish;
        end
        
        // Disable and verify it stops
        enable = 0;
        #20;
        if (count != 50) begin
            $display("ERROR: Count changed while disabled");
            $finish;
        end
        
        // Re-enable and count more
        enable = 1;
        repeat(30) @(posedge clk);
        
        if (count != 80) begin
            $display("ERROR: Expected count=80, got %d", count);
            $finish;
        end
        
        $display("Test PASSED: Basic counting works correctly");
        $finish;
    end
    
    // Timeout
    initial begin
        #10000;
        $display("ERROR: Test timeout");
        $finish;
    end
    
endmodule
