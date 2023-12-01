#! python
# (c) DL, UTA, 2009 - 2016
import  sys, string, time , math , random
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
reg3position = reg2position - (numregbits +1)
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
numL1Ref = 0 
numL1hit = 0
numL2Ref = 0
numL2hit = 0                                   
numcoderefs = 0                                      # number of times instructions read
numdatarefs = 0                                      # number of times data read
starttime = time.time()
curtime = starttime
L1cache = []
L1DataCache = []
L1InstructionCache = []
dmL2 = (8 , 8)
# L2cache = [[None] * dmL2[0]] * dmL2[0] 
L2cache = []                            # 8*8 L2 cache with tag
dm0 = [2 , 4]
dm1 = [4 , 4]
dm2 = [2 , 8]
sp0 = [(2 , 2) , (2 , 2)]
sp1 = [(4 , 2) , (4 , 4)]
sa0 = [2 , 8]
mode = sa0

print('comp ee ' , dm2 is sa0)
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
def getdata(a):
   global numL1hit
   global numL2hit
   L1hit = False
   L2hit = False
   print('getData address ' , a)
   val = getL1cache(a , 'data')
   print('data val from L1 cache ' , val)
   if val == -1:
      val = getL2cache(a)
      print('data val from L2 cache ' , val)

      if val == -1:
         val = getdatamem(a)
         print('val from mem ' , val)
      else:
         L2hit = True
         numL2hit +=1
   else:
      L1hit = True
      numL1hit += 1
   if not L1hit:
      replaceL1Cache(a , val , 'data')   
   #    if not L2hit:
   #       replaceL2cache(a , val)
   return val
def getcode(a):
   global numL1hit
   global numL2hit
   L1hit = False
   L2hit = False
   print('getcode address ' , a)
   val = getL1cache(a , 'instruction')
   print('val from L1 cache ' , val)
   if val == -1:
      val = getL2cache(a)
      print('val from L2 cache ' , val)

      if val == -1:
         val = getcodemem(a)
         print('val from mem ' , val)
      else:
         L2hit = True
         numL2hit +=1
   else:
      L1hit = True
      numL1hit += 1
   
   if not L1hit:
      replaceL1Cache(a , val , 'instruction')   
      if not L2hit:
         replaceL2cache(a , val)

   

   
   return val

def getcodemem ( a ):
    global clock
    clock+= 25
    global numMemRefs
    # get code memory at this address
    memval = mem[ a + reg[ codeseg ] ]
    numMemRefs += 1
    return ( memval )
def getL1cache(a , type = ''):
   global numL1Ref
   global clock
   numL1Ref += 1
   clock += 1
   val = -1
   if mode is dm0 or  mode is dm1 or mode is dm2:
      numOfwords = mode[0]
      numOfLines = mode[1]

      offsetnobit = int(math.log2(numOfwords))
      linenobit = int(math.log2(numOfLines))

      print('++++++= ' , offsetnobit)

      offsetMask = numOfwords - 1
      lineMask = numOfLines - 1
      
      offset = a & offsetMask
      line = (a >> offsetnobit) & lineMask
      tag = (a >> (offsetnobit + linenobit))
      print('offest ' , offset)
      print('line ' , line)
      if (L1cache[line][offset] is not None) and (L1cache[line][offset][1] == tag):
         val = L1cache[line][offset][0]
   if mode is sp0 or mode is sp1:
      if type == 'instruction':
         numOfwords = mode[0][0]
         numOfLines = mode[0][1]

         offsetnobit = int(math.log2(numOfwords))
         linenobit = int(math.log2(numOfLines))

         print('++++++= ' , offsetnobit)

         offsetMask = numOfwords - 1
         lineMask = numOfLines - 1
         
         offset = a & offsetMask
         line = (a >> offsetnobit) & lineMask
         tag = (a >> (offsetnobit + linenobit))
         print('offest ' , offset)
         print('line ' , line)
         if (L1InstructionCache[line][offset] is not None) and (L1InstructionCache[line][offset][1] == tag):
            val = L1InstructionCache[line][offset][0]
      if type == 'data':
         numOfwords = mode[1][0]
         numOfLines = mode[1][1]

         offsetnobit = int(math.log2(numOfwords))
         linenobit = int(math.log2(numOfLines))

         print('++++++= ' , offsetnobit)

         offsetMask = numOfwords - 1
         lineMask = numOfLines - 1
         
         offset = a & offsetMask
         line = (a >> offsetnobit) & lineMask
         tag = (a >> (offsetnobit + linenobit))
         print('offest ' , offset)
         print('line ' , line)
         if (L1DataCache[line][offset] is not None) and (L1DataCache[line][offset][1] == tag):
            val = L1DataCache[line][offset][0]
   elif mode is sa0:
      numOfwords = mode[0]
      numOfLines = mode[1]
      numOfSegments = int(numOfLines / 2)

      offsetnobit = int(math.log2(numOfwords))
      segmentnobit = int(math.log2(numOfSegments))

      print('++++++= ' , offsetnobit)

      offsetMask = numOfwords - 1
      segmentMask = numOfSegments - 1
      
      offset = a & offsetMask
      # line = (a >> offsetnobit) & lineMask
      segment = (a >> offsetnobit) & segmentMask
      tag = (a >> (offsetnobit + segmentnobit))
      print('get sa0 offest ' , offset)
      print('segment sa0 ' , segment)
      lines = [l for l in range(segment * 2 , segment * 2 + 2)]
      for line in lines:
         if (L1cache[line][offset] is not None) and (L1cache[line][offset][1] == tag):
            val = L1cache[line][offset][0]
            break
   
   return val
def replaceL1Cache(a , value , type = ''):
   print('replaceL1 address ' , a , mode)
   if mode is dm0 or  mode is dm1 or mode is dm2:
      numOfwords = mode[0]
      numOfLines = mode[1]

      offsetnobit = int(math.log2(numOfwords))
      linenobit = int(math.log2(numOfLines))

      print('++++++= dm ' , offsetnobit)

      offsetMask = numOfwords - 1
      lineMask = numOfLines - 1
      
      offset = a & offsetMask
      line = (a >> offsetnobit) & lineMask
      tag = (a >> (offsetnobit + linenobit))
      print('offest ' , offset)
      print('line ' , line)
      print(tag)

      L1cache[line][offset ] = (value , tag)
   elif mode is sp0 or mode is sp1:
      if type == 'instruction':
         numOfwords = mode[0][0]
         numOfLines = mode[0][1]

         offsetnobit = int(math.log2(numOfwords))
         linenobit = int(math.log2(numOfLines))

         print('++++++= sp' , offsetnobit)

         offsetMask = numOfwords - 1
         lineMask = numOfLines - 1
         
         offset = a & offsetMask
         line = (a >> offsetnobit) & lineMask
         tag = (a >> (offsetnobit + linenobit))
         print('offest ' , offset)
         print('line ' , line)
         L1InstructionCache[line][offset ] = (value , tag)

      if type == 'data':
         numOfwords = mode[1][0]
         numOfLines = mode[1][1]

         offsetnobit = int(math.log2(numOfwords))
         linenobit = int(math.log2(numOfLines))

         print('++++++= sp ' , offsetnobit)

         offsetMask = numOfwords - 1
         lineMask = numOfLines - 1
         
         offset = a & offsetMask
         line = (a >> offsetnobit) & lineMask
         tag = (a >> (offsetnobit + linenobit))
         print('offest sp' , offset)
         print('line sp' , line)
         L1DataCache[line][offset ] = (value , tag)
   elif mode is sa0:
      numOfwords = mode[0]
      numOfLines = mode[1]
      numOfSegments = int(numOfLines / 2)

      offsetnobit = int(math.log2(numOfwords))
      segmentnobit = int(math.log2(numOfSegments))

      print('replace sa0 ++++++= ' , offsetnobit)

      offsetMask = numOfwords - 1
      segmentMask = numOfSegments - 1
      
      offset = a & offsetMask
      segment = (a >> offsetnobit) & segmentMask
      tag = (a >> (offsetnobit + segmentnobit))
      print('replace sa0 offest ' , offset)
      print('replace sa0 seg ' , segment)
      lines = [l for l in range(segment * 2 , segment * 2 + 2)]
      replaced = False
      for line in lines:
         if (L1cache[line][offset] is None):
            L1cache[line][offset] = (value , tag)
            replaced = True
            break
      if not replaced:
         randLine = lines[int(random.random()*len(lines))]
         L1cache[randLine][offset] = (value , tag)

     
def getL2cache(a):
   global numL2Ref
   global clock
   numL2Ref += 1
   clock += 4
   val = -1
      
   numOfwords = dmL2[0]
   numOfLines = dmL2[1]

   offsetnobit = int(math.log2(numOfwords))
   linenobit = int(math.log2(numOfLines))

   print('++++++= ' , offsetnobit)

   offsetMask = numOfwords - 1
   lineMask = numOfLines - 1
      
   offset = a & offsetMask
   line = (a >> offsetnobit) & lineMask
   tag = (a >> (offsetnobit + linenobit))
   if  (L2cache[line][offset] is not None) and (L2cache[line][offset][1] == tag):
      val = L2cache[line][offset][0]
   
   return val
def replaceL2cache(a , value):
   print('replace l2 ' , a , value)
   numOfwords = dmL2[0]
   numOfLines = dmL2[1]

   offsetnobit = int(math.log2(numOfwords))
   linenobit = int(math.log2(numOfLines))

   print('++++++=replace l2 ' , offsetnobit)

   offsetMask = numOfwords - 1
   lineMask = numOfLines - 1
      
   offset = a & offsetMask
   line = (a >> offsetnobit) & lineMask
   tag = (a >> (offsetnobit + linenobit))
   print('replaceL2cache offest ' , offset)
   print('replaceL2cache line ' , line)
   print('replaceL2cache tag' , tag)
   # printL2()
   L2cache[line][offset] = (value , tag)
   # printL2()


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
    replaceL1Cache(a , v)
   #  replaceL2cache(a , v)
def getregval ( r ):
    # get reg or indirect value
    if ( (r & (1<<numregbits)) == 0 ):               # not indirect
       rval = reg[ r ] 
    else:
       rval = getdata( reg[ r - numregs ] )       # indirect data with mem address
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
def initCache():
   if mode is dm0 or  mode is dm1 or mode is dm2 or mode is sa0:
      for line in range(mode[1]):
         entry = [] 
         for word in range(mode[0]):
            entry.append(None)
         L1cache.append(entry)
   elif mode is sp0 or mode is sp1:
      for line in range(mode[0][1]):
         entry = [] 
         for word in range(mode[0][0]):
            entry.append(None)
         L1InstructionCache.append(entry)
      for line in range(mode[1][1]):
         entry = [] 
         for word in range(mode[1][0]):
            entry.append(None)
         L1DataCache.append(entry)

   for line in range(dmL2[1]):
      entry = [] 
      for word in range(dmL2[0]):
         entry.append(None)
      L2cache.append(entry)
   # for line in range(mode[1]):
   #    print(L1cache[line])
def printL1(cache=L1cache):
   for line in range(len(cache)):
      print(cache[line])
def printL2():
   print('-------------------l2----------------')
   for line in range(dmL2[1]):
      print(L2cache[line])
   
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
            3: (1, 'dec'), 4: ( 1, 'inc' ), 5:(5 , 'addvector'),
            7: (3, 'ld'),  8: (3, 'st'), 9: (3, 'ldi'),
           12: (3, 'bnz'), 13: (3, 'brl'),
           14: (1, 'ret'),
           16: (3, 'int') }
initCache()
startexechere( 0 )                                  # start execution here if no "go"
loadmem()                                           # load binary executable
ip = 0                                              # start execution at codeseg location 0
# while instruction is not halt
while( 1 ):
   regEntry = [0] * numregs
   # print('=========== ' ,codeseg , '========')
   ir = getcode( ip )                            # - fetch
   print('ir: ' , ir)
   # clock += 1
   ip = ip + 1
   opcode = ir >> opcposition                       # - decode

   clock += 1
   reg1   = (ir >> reg1position) & regmask
   reg2   = (ir >> reg2position) & regmask
   reg3   = (ir >> reg3position) & regmask
   addr   = (ir) & addmask
   ic = ic + 1
   # if opcode == 5:
   #    print('=== found ')
   #    print('ir' , ir , 'ip' , ip , 'opcode' , opcode , 'reg1' , reg1 , 'reg2' , reg2 ,'reg3' , reg3  ,  'addr' , addr , 'ic' , ic)  
   #    exit()                                             # - operand fetch
   print('ir' , ir , 'ip' , ip , 'opcode' , opcode , 'reg1' , reg1 , 'reg2' , reg2 ,'reg3' , reg3  ,  'addr' , addr , 'ic' , ic)  
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
   elif opcodes[ opcode ] [0] == 5:  
      operand1 = getregval( reg1 )                  #       fetch operands
      regEntry[reg1] = 'w'
      operand2 = getregval( reg2 )
      # print('in line 191 ' , reg2)
      if ( (reg2 & (1<<numregbits)) == 0 ):
         regEntry[reg2] = 'r'
      else:
         regEntry[reg2 - numregs] = 'r'
      
      operand3 = getregval( reg3 )
      # print('in line 191 ' , reg2)
      if ( (reg3 & (1<<numregbits)) == 0 ):
         regEntry[reg3] = 'r'
      else:
         regEntry[reg3 - numregs] = 'r'
      
      print('addvector op decode ' , operand1 , operand2 , operand3)
      # exit()
      

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
   # clock += 1
   if (opcode == 7):                                # get data memory for loads
      memdata = getdata( operand2 )
      # clock+=1
   if (opcode == 8):        
      # memdata = operand1
      clock+=1
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
   elif opcode == 5:
      for i in range(3):
         memdata1 = getdata(operand2)
         memdata2 = getdata(operand3)
         result = memdata1 + memdata2
         storedatamem( operand1 ,result)
         operand1 += 1
         operand2 += 1
         operand3 += 1

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
   print('===========================================================')
   print('===========================================================')
   print('===========================================================')
   printL1(L2cache)
   # time.sleep(10)
   

print( 'clock=', clock, 'IC=', ic, 'Mem reference=', numMemRefs)
# for entry in scoreBoard:
#    print(entry)
# for entry in predictionTable:
#    print(entry , predictionTable[entry])

print('-------------L1InstructionCache----------')
printL1(L1InstructionCache)
print('-------------L1DataCache----------')
printL1(L1DataCache)
print('-------------Unified L1Cache----------')
printL1(L1cache)
print('-------------Unified L2Cache----------')
printL1(L2cache)
print('L1 cache hit rate:' , numL1hit/numL1Ref*100 , '%')
print('L2 cache hit rate:' , numL2hit/numL2Ref*100 , '%')
print( 'clock=', clock, 'IC=', ic, 'Mem reference=', numMemRefs)

# printL2()
   # end of instruction loop     
# end of execution

   
