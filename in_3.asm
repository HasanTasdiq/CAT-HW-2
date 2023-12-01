; sum an array
       go   0
0      ld   0 .count     ; r2 has value of counter
       ldi  1 .vals1     ; r3 points to first value of first array
       ldi  2 .vals2     ; r4 point to first value of 2nd array
       ldi   3 .vals3     ; r1 points to the first value of the resultant array
       ldi 4 0
.loop  ldi 4 0 
       add  4 *1      ; r4 = r4 + next array value from 1st array
       add  4 *2      ; r4 = r4 + next array value from 2nd array
       st   4 3
       inc  1
       inc  2
       inc  3
       dec  0
       bnz  0 .loop
       ld 0 .count
       ldi 1 .vals1
       ldi 2 .vals2
       ldi 3 .vals4
.loop2  ldi 4 0 
       add  4 *1      ; r4 = r4 + next array value from 1st array
       add  4 *2      ; r4 = r4 + next array value from 2nd array
       st   4 3
       inc  1
       inc  2
       inc  3
       dec  0
       bnz  0 .loop2
.count dw   10
.vals1  dw   3
       dw   2
       dw   1
       dw 3
       dw 2
       dw 1
       dw 3
       dw 2
       dw 1
       dw 90
.vals2  dw   7
       dw   8
       dw   9
       dw   7
       dw   8
       dw   9
       dw   7
       dw   8
       dw   9
       dw   9
.vals3 dw   0
       dw   0
       dw   0
       dw   0
       dw   0
       dw   0
       dw   0
       dw   0
       dw   0
       dw 0
.vals4 dw   0
       dw   0
       dw   0
       dw   0
       dw   0
       dw   0
       dw   0
       dw   0
       dw   0
       dw 0