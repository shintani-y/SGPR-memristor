1R testbench
.option post ingold=2
.hdl '../verilog/rram_gp.va'


X1  BL  Nb  rram
+tstep=1ns

.param P_SET  = 1.2V
.param P_READ = 0.5V
.param N_SET  = 1.5V

V_SET1	 t16 0   PULSE (0V  P_READ   24ns 20ns 20ns 25ns 2500ns )
V_SET2	 t15 t16 PULSE (0V  P_READ  284ns 20ns 20ns 25ns 2500ns )
V_SET3	 t14 t15 PULSE (0V  P_SET   374ns 48ns 48ns 25ns 2500ns )
V_SET4	 t13 t14 PULSE (0V  P_READ  520ns 20ns 20ns 25ns 2500ns )
V_SET5	 t12 t13 PULSE (0V  P_READ  780ns 20ns 20ns 25ns 2500ns )
V_SET6	 t11 t12 PULSE (0V  P_SET   870ns 48ns 48ns 25ns 2500ns )
V_SET7	 t10 t11 PULSE (0V  P_READ 1016ns 20ns 20ns 25ns 2500ns )
V_SET8	 t9  t10 PULSE (0V  P_READ 1276ns 20ns 20ns 25ns 2500ns )
V_SET9	 t8  t9  PULSE (0V  P_SET  1366ns 48ns 48ns 25ns 2500ns )
V_SET10	 t7  t8  PULSE (0V  P_READ 1512ns 20ns 20ns 25ns 2500ns )
V_SET11	 t6  t7  PULSE (0V  P_SET  1602ns 48ns 48ns 25ns 2500ns )
V_SET12	 t5  t6  PULSE (0V  P_READ 1748ns 20ns 20ns 25ns 2500ns )
V_SET13	 t4  t5  PULSE (0V  P_SET  1838ns 48ns 48ns 25ns 2500ns )
V_SET14	 t3  t4  PULSE (0V  P_READ 1984ns 20ns 20ns 25ns 2500ns )
V_SET15	 t2  t3  PULSE (0V  P_READ 2244ns 20ns 20ns 25ns 2500ns )
V_SET16	 BL  t2  PULSE (0V  P_SET  2334ns 48ns 48ns 25ns 2500ns )

V_RESET1 Nb  t17 PULSE (0V  N_SET   114ns 60ns 60ns 25ns 2500ns )
V_RESET2 t17 t18 PULSE (0V  N_SET   610ns 60ns 60ns 25ns 2500ns )
V_RESET3 t18 t19 PULSE (0V  N_SET  1106ns 60ns 60ns 25ns 2500ns )
V_RESET4 t19 t1  PULSE (0V  N_SET  2074ns 60ns 60ns 25ns 2500ns )
v_t1 t1 0 dc 0



.tran   1ns 2455ns

.print V(BL,Nb) I(v_t1) V(X1.S_out)

.end
