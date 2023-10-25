from typing import Dict
import struct
from registers import Registers, Cr
from xex import XEX
from instructions import *
from enum import Enum, unique, auto

HANDLER_TABLE = {}

def u16_to_s16(value):
  value &= 0xFFFF
  if value & 0x8000:
    return value - 0x10000
  return value

def u24_to_s24(value):
  value &= 0xFFFFFF
  if value & 0x800000:
    return value - 0x1000000
  return value

def u32_to_s32(value):
  value &= 0xFFFFFFFF
  if value & 0x80000000:
    return value - 0x100000000
  return value

def u64_to_s64(value):
  value &= 0xFFFFFFFFFFFFFFFF
  if value & 0x8000000000000000:
    return value - 0x10000000000000000
  return value

def pyint_to_u32(value):
  return value & 0xFFFFFFFF

def pyint_to_u64(value):
  return value & 0xFFFFFFFFFFFFFFFF

@unique
class IterReason(Enum):
  IterOk = 0,
  IterContinue = auto(),
  IterReturn = auto()
  
class VirtualMachine:
  def __init__(self, xex: XEX) -> None:
    self.context = Registers()
    self.stack = bytearray([0x69] * 0xffff) # default size, idk
    self.data = bytearray()
    self.executing = bytearray()
    self.xex = xex
    pass
  
  def write(self, address, off, byte_value, register=None):
    val = ' '.join([hex(a)[2:] for a in byte_value])
    print(f'[Write] {hex(address)} + {hex(off)}({hex(address + off)}) = {val}, reg {register}')
    if register is not None:
      if register == 1:
        stack_ptr = self.context.gpr[1] + off
        self.stack[stack_ptr:stack_ptr+len(byte_value)] = byte_value
        return

    address += off
    
    if address <= len(self.stack):
      # likely frame pointer or something similar
      self.stack[address:address+len(byte_value)] = byte_value
      return
    
    xex_base = self.xex.base_address - self.xex.pe_data_offset
    xex_size = len(self.data)
    
    if address >= xex_base and address <= (xex_base + xex_size):
      offset = self.virtual_to_real(address)
      self.data[offset:offset+len(byte_value)] = byte_value
      return
    
    b = ' '.join([hex(a)[2:] for a in byte_value])
    print(f'failed to write, {hex(address)}, {hex(off)}, {b}, {register}')
    pass
  
  def read(self, address, off, size, register=None):
    print(f'[Read] {hex(address)} + {hex(off)}({hex(address + off)}) for {size} bytes, reg {register}')
    if register is not None:
      if register == 1:
        stack_ptr = self.context.gpr[1] + off
        return self.stack[stack_ptr:stack_ptr+size] # stack
      
    address += off
    
    if address <= len(self.stack):
      # likely frame pointer or something similar
      return self.stack[address:address+size]
    
    xex_base = self.xex.base_address - self.xex.pe_data_offset
    xex_size = len(self.data)
    
    if address >= xex_base and address <= (xex_base + xex_size):
      offset = self.virtual_to_real(address)
      return self.data[offset:offset+size]
    
    return [0] * size # temp
  
  def virtual_to_real(self, virtual):
    return virtual - self.xex.base_address - self.xex.pe_data_offset
  
  def branch_to(self, src, dst):
    inst = Bx()
    inst.bits.opcode = 18
    inst.bits.ll = (dst - src) // 4
    
    offset = self.virtual_to_real(src)
    self.executing[offset:offset+4] = struct.pack('>I', inst.value)
    pass
  
  def execute(self):
    self.stack = [0] * len(self.stack)
    self.context.gpr[1] = len(self.stack) // 2
    
    while True:
      iar = self.context.iar * 4
      buffer = self.executing[iar:iar+4]
      
      inst = Instruction()
      inst.value = int.from_bytes(buffer, 'big')
      
      if inst.bits.opcode in HANDLER_TABLE:
        match HANDLER_TABLE[inst.bits.opcode](buffer, self):
          case IterReason.IterContinue:
            continue
          case IterReason.IterReturn:
            return
        
        self.context.iar += 1
      else:
        print(f'opcode {inst.bits.opcode} not setup')
        break

def cmpi(data, vm: VirtualMachine) -> IterReason:
  val = Cmpi()
  val.value = int.from_bytes(data, 'big')
  
  for i in range(len(vm.context.cr[val.bits.crfd])):
    vm.context.cr[val.bits.crfd][i] = False
    
  ra = 0
  ds = 0
  
  if val.bits.l:
    ra = u64_to_s64(vm.context.gpr[val.bits.ra])
    ds = u64_to_s64(val.bits.ds)
  else:
    ra = u32_to_s32(vm.context.gpr[val.bits.ra])
    ds = u32_to_s32(val.bits.ds)
    
  vm.context.cr[val.bits.crfd][Cr.lt] = ra < ds # lt
  vm.context.cr[val.bits.crfd][Cr.gt] = ra > ds # gt
  vm.context.cr[val.bits.crfd][Cr.eq] = ra == ds # eq
  vm.context.cr[val.bits.crfd][Cr.so] = vm.context.xer.so != 0 # so
  
  tag = 'cmpdi' if val.bits.l else 'cmpwi'
  print(f'{tag} cr{val.bits.crfd}, r{val.bits.ra}, {hex(val.bits.ds)}')
  return IterReason.IterOk

def cmpli(data, vm: VirtualMachine) -> IterReason:
  val = Cmpli()
  val.value = int.from_bytes(data, 'big')
  
  for i in range(len(vm.context.cr[val.bits.crfd])):
    vm.context.cr[val.bits.crfd][i] = False
    
  ra = 0
  ds = 0
  
  if val.bits.l:
    ra = pyint_to_u64(vm.context.gpr[val.bits.ra])
    ds = pyint_to_u64(val.bits.ds)
  else:
    ra = pyint_to_u32(vm.context.gpr[val.bits.ra])
    ds = pyint_to_u32(val.bits.ds)
    
  vm.context.cr[val.bits.crfd][Cr.lt] = ra < ds # lt
  vm.context.cr[val.bits.crfd][Cr.gt] = ra > ds # gt
  vm.context.cr[val.bits.crfd][Cr.eq] = ra == ds # eq
  vm.context.cr[val.bits.crfd][Cr.so] = vm.context.xer.so != 0 # so
  
  tag = 'cmpldi' if val.bits.l else 'cmplwi'
  print(f'{tag} cr{val.bits.crfd}, r{val.bits.ra}, {hex(val.bits.ds)}')
  return IterReason.IterOk

def li(data, vm: VirtualMachine) -> IterReason:
  val = Li()
  val.value = int.from_bytes(data, 'big')
  
  si = val.bits.si
  output = si if val.bits.ra == 0 else (vm.context.gpr[val.bits.ra | 0] + si)
  vm.context.gpr[val.bits.rt] = pyint_to_u32(output)

  if val.bits.ra == 0:
    print(f'li r{val.bits.rt}, {hex(val.bits.si)}')
  else:
    print(f'addi r{val.bits.rt}, r{val.bits.ra | 0}, {hex(val.bits.si)}')
  return IterReason.IterOk

def lis(data, vm: VirtualMachine) -> IterReason:
  val = Li()
  val.value = int.from_bytes(data, 'big')
  
  si = pyint_to_u32(val.bits.si)
  ra = pyint_to_u32(val.bits.ra)
  
  if val.bits.ra == 0:
    vm.context.gpr[val.bits.rt] = si if si else 0
    print(f'lis r{val.bits.rt}, {hex(val.bits.si if val.bits.si else 0)}')
  else:
    vm.context.gpr[val.bits.rt] = (ra if ra else 0) + (si if si else 0)
    print(f'addic r{val.bits.rt}, r{val.bits.ra | 0}, {hex(val.bits.si if val.bits.si else 0)}')

  return IterReason.IterOk

def sc(data, vm: VirtualMachine) -> IterReason:
  val = Sc()
  val.value = int.from_bytes(data, 'big')
  
  if val.bits.lev == 2:
    print(f'TODO: Syscall with index {hex(vm.context.gpr[0])}')

  return IterReason.IterOk

def lwz(data, vm: VirtualMachine) -> IterReason:
  val = Lwz()
  val.value = int.from_bytes(data, 'big')
  
  vm.context.gpr[val.bits.rt] = pyint_to_u32(int.from_bytes(vm.read(vm.context.gpr[val.bits.ra], val.bits.ds, 4, val.bits.ra), 'little'))
  
  offset_fmt = '' if val.bits.ds > 0 else '-'
  offset_val = abs(val.bits.ds)
  print(f'lwz r{val.bits.rt}, {offset_fmt}{hex(offset_val)}(r{val.bits.ra}) -> {hex(vm.context.gpr[val.bits.rt])}')

  return IterReason.IterOk

def stwu(data, vm: VirtualMachine) -> IterReason:
  val = Stwu()
  val.value = int.from_bytes(data, 'big')
  
  if val.bits.ra == 1:
    # stack
    current = vm.context.gpr[1]
    vm.context.gpr[1] += u16_to_s16(val.bits.ds)
    
    if vm.context.gpr[1] < 0:
      # expand stack
      vm.stack.extend(abs(vm.context.gpr[1]))
      vm.context.gpr[1] = 0 # bottom of the stack
      pass
    
    vm.write(0, 0, current.to_bytes(8, 'little'), 1)
    print(f'Stack pointer: {hex(vm.context.gpr[1])}')
  else:
    vm.write(vm.context.gpr[val.bits.ra], u16_to_s16(val.bits.ds), vm.context.gpr[val.bits.rt].to_bytes(4, 'little'), val.bits.ra)
  
  offset_fmt = '' if u16_to_s16(val.bits.ds) > 0 else '-'
  offset_val = abs(u16_to_s16(val.bits.ds))
  print(f'stwu r{val.bits.rt}, {offset_fmt}{hex(offset_val)}(r{val.bits.ra})')
  return IterReason.IterOk

def stw(data, vm: VirtualMachine) -> IterReason:
  val = Stw()
  val.value = int.from_bytes(data, 'big')
  
  vm.write(vm.context.gpr[val.bits.ra], u16_to_s16(val.bits.ds), vm.context.gpr[val.bits.rt].to_bytes(4, 'little'), val.bits.ra)
  
  offset_fmt = '' if u16_to_s16(val.bits.ds) > 0 else '-'
  offset_val = abs(u16_to_s16(val.bits.ds))
  print(f'stw r{val.bits.rt}, {offset_fmt}{hex(offset_val)}(r{val.bits.ra})')
  return IterReason.IterOk

def stb(data, vm: VirtualMachine) -> IterReason:
  val = Stb()
  val.value = int.from_bytes(data, 'big')
  
  vm.write(vm.context.gpr[val.bits.ra], u16_to_s16(val.bits.ds), vm.context.gpr[val.bits.rt].to_bytes(1, 'little'), val.bits.ra)
  
  offset_fmt = '' if u16_to_s16(val.bits.ds) > 0 else '-'
  offset_val = abs(u16_to_s16(val.bits.ds))
  print(f'stb r{val.bits.rt}, {offset_fmt}{hex(offset_val)}(r{val.bits.ra})')
  return IterReason.IterOk

def b(data, vm: VirtualMachine) -> IterReason:
  val = Bx()
  val.value = int.from_bytes(data, 'big')
  
  if val.bits.lk:
    vm.context.lr = vm.context.iar + 1
    
  offset = val.bits.ll - 1
  if val.bits.aa == 0:
    vm.context.iar += u24_to_s24(offset)
  else:
    vm.context.iar = offset
  
  key = 'b'
  if val.bits.aa == 1 and val.bits.lk == 0:
    key = 'ba'
  elif val.bits.aa == 0 and val.bits.lk == 1:
    key = 'bl'
  elif val.bits.aa == 1 and val.bits.lk == 1:
    key = 'bla'
    
  print(f'{key} {hex(u24_to_s24(offset) * 4)}')  
  return IterReason.IterOk

def bc(data, vm: VirtualMachine) -> IterReason:
  val = Bcx()
  val.value = int.from_bytes(data, 'big')
  
  cr_field = val.bits.bi >> 2
  cr_field_bit = val.bits.bi & 3
  branch_offset = (val.bits.bd << 2) - 1
  
  offset_fmt = '' if u16_to_s16(branch_offset) > 0 else '-'
  offset_val = abs(u16_to_s16(branch_offset))
    
  decrement = False
  if not (val.bits.bo & 0b00100):
    vm.context.ctr -= 1
    decrement = True
    
  branch = False
  if (val.bits.bo & 0b10000):
    if decrement:
      branch = True
    elif (val.bits.bo & 0b00010):
      branch = vm.context.ctr == 0
      print(f'bdz cr{cr_field}, {offset_fmt}{hex(offset_val)}')
    else:
      branch = vm.context.ctr != 0
      print(f'bdnz cr{cr_field}, {offset_fmt}{hex(offset_val)}')
  else:
    if (val.bits.bo & 0b01000):
      branch = vm.context.cr[cr_field][cr_field_bit]
      match cr_field_bit:
        case 0:
          print(f'blt cr{cr_field}, {offset_fmt}{hex(offset_val)}')
        case 1:
          print(f'bgt cr{cr_field}, {offset_fmt}{hex(offset_val)}')
        case 2:
          print(f'beq cr{cr_field}, {offset_fmt}{hex(offset_val)}')
    else:
      branch = not (vm.context.cr[cr_field][cr_field_bit])
      match cr_field_bit:
        case 0:
          print(f'bge cr{cr_field}, {offset_fmt}{hex(offset_val)}')
        case 1:
          print(f'ble cr{cr_field}, {offset_fmt}{hex(offset_val)}')
        case 2:
          print(f'bne cr{cr_field}, {offset_fmt}{hex(offset_val)}')
  
  if branch:
    if val.bits.lk:
      vm.context.lr = vm.context.iar + 1
      
    offset = (branch_offset & 0xFFFF if branch_offset & 0x8000 else branch_offset) // 4
    vm.context.iar = offset if val.bits.aa else vm.context.iar + offset
  
  return IterReason.IterOk

def or_mr(data, vm: VirtualMachine, bundle: Bundle31) -> IterReason:
  val = Or()
  val.value = int.from_bytes(data, 'big')
  
  vm.context.gpr[val.bits.ra] = vm.context.gpr[val.bits.rs] | vm.context.gpr[val.bits.rb]
  
  if val.bits.rb == val.bits.rs:
    print(f'mr r{val.bits.ra}, r{val.bits.rb}')
  else:
    print(f'or r{val.bits.ra}, r{val.bits.rs}, r{val.bits.rb}')
  
  return IterReason.IterOk

def cmp(data, vm: VirtualMachine, bundle: Bundle31) -> IterReason:
  val = Cmp()
  val.value = int.from_bytes(data, 'big')
  
  for i in range(len(vm.context.cr[val.bits.crfd])):
    vm.context.cr[val.bits.crfd][i] = False
    
  ra = 0
  rb = 0
  
  if val.bits.l:
    ra = u64_to_s64(vm.context.gpr[val.bits.ra])
    rb = u64_to_s64(vm.context.gpr[val.bits.rb])
  else:
    ra = u32_to_s32(vm.context.gpr[val.bits.ra])
    rb = u32_to_s32(vm.context.gpr[val.bits.rb])
    
  vm.context.cr[val.bits.crfd][Cr.lt] = ra < rb # lt
  vm.context.cr[val.bits.crfd][Cr.gt] = ra > rb # gt
  vm.context.cr[val.bits.crfd][Cr.eq] = ra == rb # eq
  vm.context.cr[val.bits.crfd][Cr.so] = vm.context.xer.so != 0 # so
  
  tag = 'cmpd' if val.bits.l else 'cmpw'
  ctrl = '.' if bundle.bits.rc else ''
  print(f'{tag}{ctrl} cr{val.bits.crfd}, r{val.bits.ra}, r{val.bits.rb}')
  return IterReason.IterOk

def cmpl(data, vm: VirtualMachine, bundle: Bundle31) -> IterReason:
  val = Cmpl()
  val.value = int.from_bytes(data, 'big')
  
  for i in range(len(vm.context.cr[val.bits.crfd])):
    vm.context.cr[val.bits.crfd][i] = False
    
  ra = 0
  rb = 0
  
  if val.bits.l:
    ra = pyint_to_u64(vm.context.gpr[val.bits.ra])
    rb = pyint_to_u64(vm.context.gpr[val.bits.rb])
  else:
    ra = pyint_to_u32(vm.context.gpr[val.bits.ra])
    rb = pyint_to_u32(vm.context.gpr[val.bits.rb])
    
  vm.context.cr[val.bits.crfd][Cr.lt] = ra < rb # lt
  vm.context.cr[val.bits.crfd][Cr.gt] = ra > rb # gt
  vm.context.cr[val.bits.crfd][Cr.eq] = ra == rb # eq
  vm.context.cr[val.bits.crfd][Cr.so] = vm.context.xer.so != 0 # so
  
  tag = 'cmpld' if val.bits.l else 'cmplw'
  ctrl = '.' if bundle.bits.rc else ''
  print(f'{tag}{ctrl} cr{val.bits.crfd}, r{val.bits.ra}, r{val.bits.rb}')
  return IterReason.IterOk

def add(data, vm: VirtualMachine, bundle: Bundle31) -> IterReason:
  val = Addx()
  val.value = int.from_bytes(data, 'big')
  
  ra = pyint_to_u64(vm.context.gpr[val.bits.ra])
  rb = pyint_to_u64(vm.context.gpr[val.bits.rb])
  
  vm.context.gpr[val.bits.rt] = ra + rb

  rt = pyint_to_u64(vm.context.gpr[val.bits.rt])
  
  if val.bits.oe:
    if (ra ^ ~rb) & (ra ^ rt) & 0x80000000:
      vm.context.xer.so = 1
      vm.context.xer.ov = 1
    else:
      vm.context.xer.ov = 0
  
  if val.bits.rc:
    for i in range(vm.context.cr[0]):
      vm.context.cr[0][i] = False
      
    if vm.context.gpr[val.bits.rt] == 0:
      vm.context.cr[0][Cr.eq] = True
    elif (vm.context.gpr[val.bits.rt] & 0x80000000):
      vm.context.cr[0][Cr.lt] = True
    else:
      vm.context.cr[0][Cr.gt] = True
      
    vm.context.cr[0][Cr.so] = vm.context.xer.so != 0
  
  key = 'add'
  if val.bits.oe == 0 and val.bits.rc == 1:
    key = 'add.'
  elif val.bits.oe == 1 and val.bits.rc == 0:
    key = 'addo'
  elif val.bits.oe == 1 and val.bits.rc == 1:
    key = 'addo.'
    
  print(f'{key} r{val.bits.rt}, r{val.bits.ra}, r{val.bits.rb}')
  return IterReason.IterOk

def mfspr(data, vm: VirtualMachine, bundle: Bundle31) -> IterReason:
  val = Mfspr()
  val.value = int.from_bytes(data, 'big')
  
  match (((val.bits.spr >> 5) & 0x1F) | (val.bits.spr & 0x1F)):
    case 1: # xer
      vm.context.gpr[val.bits.rt] = vm.context.xer.value
      print(f'mfxer r{val.bits.rt}')
    case 8: # lr
      vm.context.gpr[val.bits.rt] = vm.context.lr
      print(f'mflr r{val.bits.rt}')
    case 9: # ctr
      vm.context.gpr[val.bits.rt] = vm.context.ctr
      print(f'mfctr r{val.bits.rt}')
  
  return IterReason.IterOk

def mtspr(data, vm: VirtualMachine, bundle: Bundle31) -> IterReason:
  val = Mtspr()
  val.value = int.from_bytes(data, 'big')
  
  match (((val.bits.spr >> 5) & 0x1F) | (val.bits.spr & 0x1F)):
    case 1: # xer
      vm.context.xer.value = vm.context.gpr[val.bits.rt]
      print(f'mtxer r{val.bits.rt}')
    case 8: # lr
      vm.context.lr = vm.context.gpr[val.bits.rt]
      print(f'mtlr r{val.bits.rt}')
    case 9: # ctr
      vm.context.ctr = vm.context.gpr[val.bits.rt]
      print(f'mtctr r{val.bits.rt}')
  
  return IterReason.IterOk

def bclr(data, vm: VirtualMachine, bundle: Bundle19) -> IterReason:
  if bundle.bits.bo & 0b10100:
    print('blr')
    
    if vm.context.lr == 0:
      return IterReason.IterReturn
    
    vm.context.iar = vm.context.lr
    return IterReason.IterContinue
  return IterReason.IterOk

def bundle_31(data, vm: VirtualMachine) -> IterReason:
  val = Bundle31()
  val.value = int.from_bytes(data, 'big')
  
  match val.bits.sub:
    case 0:
      return cmp(data, vm, val)
    case 32:
      return cmpl(data, vm, val)
    case 444:
      return or_mr(data, vm, val)
    case 266:
      return add(data, vm, val)
    case 339:
      return mfspr(data, vm, val)
    case 467:
      return mtspr(data, vm, val)
  
  return IterReason.IterOk

def bundle_19(data, vm: VirtualMachine) -> IterReason:
  val = Bundle19()
  val.value = int.from_bytes(data, 'big')
  
  print(val.bits.sub)
  
  match val.bits.sub:
    case 16:
      return bclr(data, vm, val)
  
  return IterReason.IterOk

HANDLER_TABLE = {
  10: cmpli,
  11: cmpi,
  14: li,
  15: lis,
  16: bc,
  17: sc,
  18: b,
  19: bundle_19,
  31: bundle_31,
  32: lwz,
  36: stw,
  37: stwu,
  38: stb,
}