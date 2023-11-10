; sum an array
       go   0
0      ld   0 .count     ; r2 has value of counter
       ldi  1 .vals1     ; r3 points to first value of first array
       ldi  2 .vals2     ; r4 point to first value of 2nd array
       ldi   3 .vals3     ; r1 points to the first value of the resultant array
       ldi 4 0
.loop  add  4 *1      ; r1 = r1 + next array value from 2nd array
       add  4 *2      ; r1 = r1 + next array value from 2nd array
       st   4 3
       inc  1
       inc  2
       inc  3
       dec  0
       bnz  0 .loop
.count dw   1
.vals1  dw   3
       dw   2
       dw   1
.vals2  dw   7
       dw   8
       dw   9
.vals3 dw   0
       dw   0
       dw   0
