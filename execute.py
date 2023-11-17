#! python
# (c) DL, UTA, 2009 - 2016
import  sys, string, time
wordsize = 24                                        # everything is a word
numregbits = 3                                       # actually +1, msb is indirect bit
opcodesize = 5
addrsize = wordsize - (opcodesize+numregbits+1)      # num bits in address
memloadsize = 1024                                   # change this for larger programs
numregs = 2**numregbits
regmask = (numregs*2)-1                              # including indirect bit
addmask = (2**(wordsize - addrsize)) -1
nummask = (2**(wordsize))-1
opcposition = wordsize - (opcodesize + 1)            # shift value to position opcode
reg1position = opcposition - (numregbits +1)            # first register position
reg2position = reg1position - (numregbits +1)
memaddrimmedposition = reg2position                  # mem address or immediate same place as reg2
realmemsize = memloadsize * 1                        # this is memory size, should be (much) bigger than a program
#memory management regs
codeseg = numregs - 1                                # last reg is a code segment pointer
dataseg = numregs - 2                                # next to last reg is a data segment pointer
#ints and traps
trapreglink = numregs - 3                            # store return value here
trapval     = numregs - 4                            # pass which trap/int
mem = [0] * realmemsize                              # this is memory, init to 0 
reg = [0] * numregs                                  # registers
scoreBoard = []
predictionTable = {}
clock = 1                                            # clock starts ticking
ic = 0                                               # instruction count
numMemRefs = 0                                        
numcoderefs = 0                                      # number of times instructions read
numdatarefs = 0                                      # number of times data read
starttime = time.time()
curtime = starttime
def startexechere ( p ):
    # start execution at this address
    reg[ codeseg ] = p    
def loadmem():                                       # get binary load image
  curaddr = 0
  for line in open("a.out", 'r').readlines():
#   for line in open("in.asm", 'r').readlines():
    token = str.split( str.lower( line ))      # first token on each line is mem word, ignore rest
   #  print('[token]' , token)
    if ( token[ 0 ] == 'go' ):
        startexechere(  int( token[ 1 ] ) )
    else:    
        mem[ curaddr ] = int( token[ 0 ], 0 )                
        curaddr = curaddr = curaddr + 1
def getcodemem ( a ):
    global numMemRefs
    # get code memory at this address
    memval = mem[ a + reg[ codeseg ] ]
    numMemRefs += 1
    return ( memval )
def getdatamem ( a ):
    global numMemRefs
    
    # get code memory at this address
    memval = mem[ a + reg[ dataseg ] ]
    numMemRefs += 1

    return ( memval )
def storedatamem(a , v):
    global numMemRefs
    
    mem[ a + reg[ dataseg ] ] = v
    numMemRefs += 1
def getregval ( r ):
    # get reg or indirect value
    if ( (r & (1<<numregbits)) == 0 ):               # not indirect
       rval = reg[ r ] 
    else:
       rval = getdatamem( reg[ r - numregs ] )       # indirect data with mem address
    return ( rval )
def checkres( v1, v2, res):
    v1sign = ( v1 >> (wordsize - 1) ) & 1
    v2sign = ( v2 >> (wordsize - 1) ) & 1
    ressign = ( res >> (wordsize - 1) ) & 1
    if ( ( v1sign ) & ( v2sign ) & ( not ressign ) ):
      return ( 1 )
    elif ( ( not v1sign ) & ( not v2sign ) & ( ressign ) ):
      return ( 1 )
    else:
      return( 0 )
def dumpstate ( d ):
    if ( d == 1 ):
        print('reg', reg)
    elif ( d == 2 ):
        print('mem' ,  mem)
    elif ( d == 3 ):
        print( 'clock=', clock, 'IC=', ic, 'Coderefs=', numcoderefs,'Datarefs=', numdatarefs, 'Start Time=', starttime, 'Currently=', time.time() )
def updateScoreBoard(arr):
   global scoreBoard
   scoreBoard.append(arr)

def detectDataHazard():
   print('----------')
   global ic
   global scoreBoard
   global numregs
   stalls = 0
   regEntry = scoreBoard[ic -1]
   prevRegEntry = scoreBoard[ic -2] if ic >=2 else [0] * numregs
   prevPrevRegEntry = scoreBoard[ic -3] if ic >=3 else [0] * numregs

   for i in range(numregs):
      entry = regEntry[i]
      print(str(entry))
      if 'r' in  str(entry):
         if 'w' in str(prevRegEntry[i]):
            stalls +=2
         if 'w' in str(prevPrevRegEntry[i]):
            stalls +=1
   
   if stalls > 0:
      print('!!!!!!!!!!!!!!!!!!!!!!!!!!! Data hazard exists !!!!!!!!!!!!!!!!!!!!!!!!!!')
      print('Need {} stalls' , stalls)


def detectConditionalHazard(opcode):
   stalls = 0
   if opcode == 12:
      print('!!!!!!!!!!!!!!!!!!!!!!!!!!! Conditional hazard exists !!!!!!!!!!!!!!!!!!!!!!!!!!')
      stalls += 2
      print('Need {} stalls' , stalls)
def updatePredictBranch(ir , guess):
   global predictionTable
   if ir not in predictionTable:
      predictionTable[ir] = [guess]
   else:
      predictionTable[ir].append(guess)



def trap ( t ):
    # unusual cases
    # trap 0 illegal instruction
    # trap 1 arithmetic overflow
    # trap 2 sys call
    # trap 3+ user
    rl = trapreglink                            # store return value here
    rv = trapval
    if ( ( t == 0 ) | ( t == 1 ) ):
       dumpstate( 1 )
       dumpstate( 2 )
       dumpstate( 3 )
    elif ( t == 2 ):                          # sys call, reg trapval has a parameter
       what = reg[ trapval ] 
       if ( what == 1 ):
           a = a        #elapsed time
    return ( -1, -1 )
   #  return ( rv, rl )
# opcode type (1 reg, 2 reg, reg+addr, immed), mnemonic  
opcodes = { 1: (2, 'add'), 2: ( 2, 'sub'), 
            3: (1, 'dec'), 4: ( 1, 'inc' ),
            7: (3, 'ld'),  8: (3, 'st'), 9: (3, 'ldi'),
           12: (3, 'bnz'), 13: (3, 'brl'),
           14: (1, 'ret'),
           16: (3, 'int') }
startexechere( 0 )                                  # start execution here if no "go"
loadmem()                                           # load binary executable
ip = 0                                              # start execution at codeseg location 0
# while instruction is not halt
while( 1 ):
   regEntry = [0] * numregs
   # print('=========== ' ,codeseg , '========')
   ir = getcodemem( ip )                            # - fetch
   clock += 1
   ip = ip + 1
   opcode = ir >> opcposition                       # - decode
   clock += 1
   reg1   = (ir >> reg1position) & regmask
   reg2   = (ir >> reg2position) & regmask
   addr   = (ir) & addmask
   ic = ic + 1
                                                    # - operand fetch
   print('ir' , ir , 'ip' , ip , 'opcode' , opcode , 'reg1' , reg1 , 'reg2' , reg2 , 'addr' , addr , 'ic' , ic)  
   # if ic %10 ==0:
   #    print('-------10----------------')
   #    trap(0)            
   if not (opcode in opcodes):
      tval, treg = trap(0) 
      print('tval ' , tval)
      if (tval == -1):                              # illegal instruction
         break
   memdata = 0                                      #     contents of memory for loads

   if opcodes[ opcode ] [0] == 1:                   #     dec, inc, ret type
      operand1 = getregval( reg1 )                  #       fetch operands
      regEntry[reg1] = 'r/w'
      if opcode == 14:
         regEntry[reg1] = 'r'

   elif opcodes[ opcode ] [0] == 2:                 #     add, sub type
      operand1 = getregval( reg1 )                  #       fetch operands
      regEntry[reg1] = 'r/w'
      operand2 = getregval( reg2 )
      # print('in line 191 ' , reg2)
      if ( (reg2 & (1<<numregbits)) == 0 ):
         regEntry[reg2] = 'r'
      else:
         regEntry[reg2 - numregs] = 'r'

   elif opcodes[ opcode ] [0] == 3:                 #     ld, st, br type
      operand1 = getregval( reg1 )                  #       fetch operands
      operand2 = addr                     

      if opcode == 7 or opcode == 9:
         regEntry[reg1] = 'w'
      elif opcode == 8:
         regEntry[reg1] = 'r'
      elif opcode == 13:
         regEntry[reg1] = 'r'
   
   elif opcodes[ opcode ] [0] == 0:                 #     ? type
      break
   clock += 1
   if (opcode == 7):                                # get data memory for loads
      memdata = getdatamem( operand2 )
      clock+=1
   if (opcode == 8):        
      # memdata = operand1
      operand2 = getregval(addr)

      # print('=====8===' , operand1 , memdata)                        # get data from reg1 for store
   updateScoreBoard(regEntry)
   detectDataHazard()
   detectConditionalHazard(opcode)
   # execute
   if opcode == 1:                     # add
      clock += 1
      result = (operand1 + operand2) & nummask
      if ( checkres( operand1, operand2, result )):
         tval, treg = trap(1) 
         if (tval == -1):                           # overflow
            break
   elif opcode == 2:                   # sub
      clock += 1
      result = (operand1 - operand2) & nummask
      if ( checkres( operand1, operand2, result )):
         tval, treg = trap(1) 
         if (tval == -1):                           # overflow
            break
   elif opcode == 3:                   # dec
      result = operand1 - 1
      clock += 1
   elif opcode == 4:                   # inc
      result = operand1 + 1
      clock += 1
   elif opcode == 7:                   # load
      result = memdata
   elif opcode == 8:                   # store
      result = operand1
   elif opcode == 9:                   # load immediate
      result = operand2
   elif opcode == 12:                  # conditional branch
      result = operand1
      updatePredictBranch(ir , result!=0)
      if result != 0:
         ip = operand2
   elif opcode == 13:                  # branch and link
      result = ip
      ip = operand2
   elif opcode == 14:                   # return
      ip = operand1
   elif opcode == 16:                   # interrupt/sys call
      result = ip
      tval, treg = trap(reg1)
      if (tval == -1):
        break
      reg1 = treg
      ip = operand2

   # write back
   if ( (opcode == 1) | (opcode == 2 ) | 
         (opcode == 3) | (opcode == 4 ) ):     # arithmetic
        reg[ reg1 ] = result
        clock += 1
   elif ( (opcode == 7) | (opcode == 9 )):     # loads
        reg[ reg1 ] = result
        clock += 1
   elif (opcode == 8):
      storedatamem( operand2 ,result)
      clock += 1

   
   elif (opcode == 13):  
        clock += 1
        reg[ reg1 ] = result
   elif (opcode == 16):    
                            # store return address
        clock += 1
        reg[ reg1 ] = result
   

print( 'clock=', clock, 'IC=', ic, 'Mem reference=', numMemRefs)
for entry in scoreBoard:
   print(entry)
for entry in predictionTable:
   print(entry , predictionTable[entry])

   # end of instruction loop     
# end of execution

   
