
from enum import IntFlag

class Cr(IntFlag):
  lt = 0,
  gt = 1,
  eq = 2,
  so = 3

class Registers:
  class XER:
    def __init__(self):
      self.value = 0

    @property
    def so(self):
      return (self.value >> 0) & 1

    @so.setter
    def so(self, val):
      self.value = (self.value & ~0x1) | (val << 0)

    @property
    def ov(self):
      return (self.value >> 1) & 1

    @ov.setter
    def ov(self, val):
      self.value = (self.value & ~0x2) | (val << 1)

    @property
    def ca(self):
      return (self.value >> 2) & 1

    @ca.setter
    def ca(self, val):
      self.value = (self.value & ~0x4) | (val << 2)

  class CRBit:
    LT, GT, EQ, SO = range(4)

  def __init__(self):
    self.msr = 0
    self.iar = 0
    self.lr = 0
    self.ctr = 0
    self.gpr = [0] * 32
    self.xer = Registers.XER()
    self.cr = [[False, False, False, False] for _ in range(8)]  # Lists of 4 booleans
    self.fpscr = 0.0
    self.fpr = [0.0] * 32