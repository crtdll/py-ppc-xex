import ctypes
import struct

class Instruction(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('data', ctypes.c_uint32, 26),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]

class Bx(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('lk', ctypes.c_uint32, 1),
      ('aa', ctypes.c_uint32, 1),
      ('ll', ctypes.c_uint32, 24),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]

class Bcx(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('lk', ctypes.c_uint32, 1),
      ('aa', ctypes.c_uint32, 1),
      ('bd', ctypes.c_uint32, 14),
      ('bi', ctypes.c_uint32, 5),
      ('bo', ctypes.c_uint32, 5),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
  
class Cmpi(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('ds', ctypes.c_uint32, 16),
      ('ra', ctypes.c_uint32, 5),
      ('l', ctypes.c_uint32, 1),
      ('_unused', ctypes.c_uint32, 1),
      ('crfd', ctypes.c_uint32, 3),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
  
class Cmpli(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('ds', ctypes.c_uint32, 16),
      ('ra', ctypes.c_uint32, 5),
      ('l', ctypes.c_uint32, 1),
      ('_unused', ctypes.c_uint32, 1),
      ('crfd', ctypes.c_uint32, 3),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
  
class Cmp(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('_unused3', ctypes.c_uint32, 1),
      ('_unused2', ctypes.c_uint32, 10),
      ('rb', ctypes.c_uint32, 5),
      ('ra', ctypes.c_uint32, 5),
      ('l', ctypes.c_uint32, 1),
      ('_unused', ctypes.c_uint32, 1),
      ('crfd', ctypes.c_uint32, 3),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
  
class Cmpl(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('_unused3', ctypes.c_uint32, 1),
      ('_unused2', ctypes.c_uint32, 10),
      ('rb', ctypes.c_uint32, 5),
      ('ra', ctypes.c_uint32, 5),
      ('l', ctypes.c_uint32, 1),
      ('_unused', ctypes.c_uint32, 1),
      ('crfd', ctypes.c_uint32, 3),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
  
class Li(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('si', ctypes.c_uint32, 16),
      ('ra', ctypes.c_uint32, 5),
      ('rt', ctypes.c_uint32, 5),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
  
class Sc(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('lev', ctypes.c_uint32, 26),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
  
class Lwz(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('ds', ctypes.c_uint32, 16),
      ('ra', ctypes.c_uint32, 5),
      ('rt', ctypes.c_uint32, 5),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
  
class Stwu(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('ds', ctypes.c_uint32, 16),
      ('ra', ctypes.c_uint32, 5),
      ('rt', ctypes.c_uint32, 5),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
  
class Stw(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('ds', ctypes.c_uint32, 16),
      ('ra', ctypes.c_uint32, 5),
      ('rt', ctypes.c_uint32, 5),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
  
class Stb(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('ds', ctypes.c_uint32, 16),
      ('ra', ctypes.c_uint32, 5),
      ('rt', ctypes.c_uint32, 5),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
  
class Or(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('rc', ctypes.c_uint32, 1),
      ('sub', ctypes.c_uint32, 10),
      ('rb', ctypes.c_uint32, 5),
      ('ra', ctypes.c_uint32, 5),
      ('rs', ctypes.c_uint32, 5),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
  
class Addx(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('rc', ctypes.c_uint32, 1),
      ('sub', ctypes.c_uint32, 9),
      ('oe', ctypes.c_uint32, 1),
      ('rb', ctypes.c_uint32, 5),
      ('ra', ctypes.c_uint32, 5),
      ('rt', ctypes.c_uint32, 5),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
    
class Mfspr(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('rc', ctypes.c_uint32, 1),
      ('sub', ctypes.c_uint32, 10),
      ('spr', ctypes.c_uint32, 10),
      ('rt', ctypes.c_uint32, 5),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]
    
class Mtspr(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('rc', ctypes.c_uint32, 1),
      ('sub', ctypes.c_uint32, 10),
      ('spr', ctypes.c_uint32, 10),
      ('rt', ctypes.c_uint32, 5),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]

class Bundle31(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('rc', ctypes.c_uint32, 1),
      ('sub', ctypes.c_uint32, 9),
      ('oe', ctypes.c_uint32, 1),
      ('rb', ctypes.c_uint32, 5),
      ('ra', ctypes.c_uint32, 5),
      ('rt', ctypes.c_uint32, 5),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]

class Bundle19(ctypes.Union):
  class _Bits(ctypes.LittleEndianStructure):
    _fields_ = [
      ('lk', ctypes.c_uint32, 1),
      ('sub', ctypes.c_uint32, 10),
      ('bh', ctypes.c_uint32, 2),
      ('reserved', ctypes.c_uint32, 3),
      ('bl', ctypes.c_uint32, 5),
      ('bo', ctypes.c_uint32, 5),
      ('opcode', ctypes.c_uint32, 6)
    ]

  _fields_ = [
    ('value', ctypes.c_uint32),
    ('bits', _Bits)
  ]