1R testbench
.option post ingold=2
.hdl '../verilog/rram_gp.va'


X1  BL  Nb  rram
+tstep=1ns

.param P_SET  = 1.2V
.param P_READ = 0.5V
.param N_SET  = 1.5V

V_SET1	 t4 0  PULSE (0V  P_SET   24ns 48ns 48ns 25ns 820ns )
V_SET2	 t3 t4 PULSE (0V  P_SET  170ns 48ns 48ns 25ns 820ns )
V_SET3	 t2 t3 PULSE (0V  P_READ 316ns 20ns 20ns 25ns 820ns )
V_SET4	 BL t2 PULSE (0V  P_READ 746ns 20ns 20ns 25ns 820ns )
V_RESET1 Nb t5 PULSE (0V  N_SET  406ns 60ns 60ns 25ns 820ns )
V_RESET2 t5 t1 PULSE (0V  N_SET  576ns 60ns 60ns 25ns 820ns )
v_t1 t1 0 dc 0



.tran   1ns 811ns

.print V(BL,Nb) I(v_t1) V(X1.S_out)

.end
