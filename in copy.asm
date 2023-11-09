; sum an array
       go   0
0      ld   2 .count     ; r2 has value of counter
       ldi  3 .vals1     ; r3 points to first value of first array
       ldi  4 .vals2     ; r4 point to first value of 2nd array
       ldi  1 0       ; r1 points to the first value of the resultant array
.loop  add  3 *4      ; r1 = r1 + next array value from 2nd array
       st   3 .vals3
       inc  3
       inc  4
       dec  2
       bnz  2 .loop
.count dw   3
.vals1  dw   3
       dw   2
       dw   1
.vals2  dw   7
       dw   8
       dw   9
.vals3 dw   0
       dw   0
       dw   0
