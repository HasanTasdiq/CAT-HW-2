; sum an array
       go   0
0      ldi  1 .vals1     ; r3 points to first value of first array
       ldi  2 .vals2     ; r4 point to first value of 2nd array
       ldi   3 .vals3     ; r1 points to the first value of the resultant array
       addvector 3 1 2    ; d , s , s
.vals1  dw   1
       dw   2
       dw   3
.vals2  dw   4
       dw   5
       dw   6
.vals3 dw   0
       dw   0
       dw   0