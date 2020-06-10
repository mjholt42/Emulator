#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""A python version of the MOS 6502 Processor"""

import abc
import itertools
from collections import OrderedDict


class _Status:
    """Performs the role of a status enum allowing us to select multiple bits"""
    def __init__(self):
        self.values = dict(N=1 << 7,
                           V=1 << 6,
                           U=1 << 5,
                           B=1 << 4,
                           D=1 << 3,
                           I=1 << 2,
                           Z=1 << 1,
                           C=1 << 0)

    def __getitem__(self, item):
        if isinstance(item, str):
            'Get value from string'
            out = 0
            for letter in item:
                out += self.values[letter]
        else:
            out = ''
            for letter, num in self.values.items():
                if item & num:
                    out += letter
        return out

    def flags(self):
        return list(self.values.keys())


Status = _Status()


class Ops6502:
    """This class contains all the opcodes - no need for separate class other than for code organisation"""
    def __init__(self, bus):
        """Dummy values"""
        self.A = 0
        self.X = 0
        self.Y = 0
        self.S = 0
        self.PC = 0
        self.P = 0
        self.bus = bus
        self.cycles = 0

    @abc.abstractmethod
    def _read_pc(self): pass

    @abc.abstractmethod
    def _read_bytes_pc(self, length): pass

    @abc.abstractmethod
    def _pop_stack(self): pass

    @abc.abstractmethod
    def _push_stack(self, val): pass

    def _set_if_true(self, condition, flag):
        """Helper function to set status of individual bits"""
        if condition:
            self.P |= Status[flag]
        else:
            self.P &= ~Status[flag]

    def op_adc(self, address_func):
        address, operand, extra_cycle = address_func()
        if extra_cycle:
            self.cycles += 1

        if self.P & Status['D']:
            if self.P & Status['C']:
                carry = 1
            else:
                carry = 0
            intermediate = (self.A & 0x0F) + (operand & 0x0F) + carry

            if intermediate >= 0x0A:
                intermediate = ((intermediate + 0x06) & 0x0F) + 0x10

            output = (self.A & 0xF0) + (operand & 0xF0) + intermediate
            self._set_if_true(output > 0xFF, 'V')
            if output >= 0xA0:
                output += 0x60
            self._set_if_true(output >= 0x100, 'C')
            output &= 0xFF
            self._set_if_true(output & 0x80, 'N')
            self._set_if_true(output == 0, 'Z')
        else:
            if self.P & Status['C']:
                carry = 1
            else:
                carry = 0
            output = self.A + operand + carry

            # Set Flags
            self._set_if_true(output > 0xFF, 'C')
            output &= 0xFF
            self._set_if_true(output == 0, 'Z')
            self._set_if_true(output & 0x80, 'N')
            v_flag = 0
            if self.A & 0x80:
                v_flag += 1
            if operand & 0x80:
                v_flag += 1
            if output & 0x80:
                v_flag += 2
            self._set_if_true(v_flag == 2, 'V')
        self.A = output

    def op_and(self, address_func):
        _, operand, extra_cycle = address_func()
        if extra_cycle:
            self.cycles += 1

        output = self.A & operand
        self._set_if_true(output == 0, 'Z')
        self._set_if_true(output & 0x80, 'N')
        self.A = output

    def op_asl(self, address_func):
        address, operand, _ = address_func()
        output = operand << 1
        self._set_if_true(output > 0xFF, 'C')
        output &= 0xFF
        self._set_if_true(output & 0x80, 'N')
        self._set_if_true(output == 0, 'Z')

        if address is 'ACCUMULATOR':
            self.A = output
        else:
            self.bus[address] = output

    def op_bbr0(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 0
        if not operand & (1 << n):
            self.PC = address

    def op_bbr1(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 1
        if not operand & (1 << n):
            self.PC = address

    def op_bbr2(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 2
        if not operand & (1 << n):
            self.PC = address

    def op_bbr3(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 3
        if not operand & (1 << n):
            self.PC = address

    def op_bbr4(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 4
        if not operand & (1 << n):
            self.PC = address

    def op_bbr5(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 5
        if not operand & (1 << n):
            self.PC = address

    def op_bbr6(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 6
        if not operand & (1 << n):
            self.PC = address

    def op_bbr7(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 7
        if not operand & (1 << n):
            self.PC = address

    def op_bbs0(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 0
        if operand & (1 << n):
            self.PC = address

    def op_bbs1(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 1
        if operand & (1 << n):
            self.PC = address

    def op_bbs2(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 2
        if operand & (1 << n):
            self.PC = address

    def op_bbs3(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 3
        if operand & (1 << n):
            self.PC = address

    def op_bbs4(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 4
        if operand & (1 << n):
            self.PC = address

    def op_bbs5(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 5
        if operand & (1 << n):
            self.PC = address

    def op_bbs6(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 6
        if operand & (1 << n):
            self.PC = address

    def op_bbs7(self, address_func):
        address, operand, _ = address_func()  # Zero page Operand and Rel address
        n = 7
        if operand & (1 << n):
            self.PC = address

    def op_bcc(self, address_func):
        address, _, _ = address_func()
        if not self.P & Status['C']:
            if (address & 0xFF00) != (self.PC & 0xFF00):
                self.cycles += 1
            self.PC = address
        else:
            self.cycles = 0

    def op_bcs(self, address_func):
        address, _, _ = address_func()
        if self.P & Status['C']:
            if (address & 0xFF00) != (self.PC & 0xFF00):
                self.cycles += 1
            self.PC = address
        else:
            self.cycles = 0

    def op_beq(self, address_func):
        address, _, _ = address_func()
        if self.P & Status['Z']:
            if (address & 0xFF00) != (self.PC & 0xFF00):
                self.cycles += 1
            self.PC = address
        else:
            self.cycles = 0

    def op_bit(self, address_func):
        _, operand, _ = address_func()
        self._set_if_true((operand & self.A) == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')
        self._set_if_true(operand & (1 << 6), 'V')

    def op_bit_imm(self, address_func):
        _, operand, _ = address_func()
        self._set_if_true((operand & self.A) == 0, 'Z')

    def op_bmi(self, address_func):
        address, _, _ = address_func()
        if self.P & Status['N']:
            if (address & 0xFF00) != (self.PC & 0xFF00):
                self.cycles += 1
            self.PC = address
        else:
            self.cycles = 0

    def op_bne(self, address_func):
        address, _, _ = address_func()
        if not self.P & Status['Z']:
            if (address & 0xFF00) != (self.PC & 0xFF00):
                self.cycles += 1
            self.PC = address
        else:
            self.cycles = 0

    def op_bpl(self, address_func):
        address, _, _ = address_func()
        if not self.P & Status['N']:
            if (address & 0xFF00) != (self.PC & 0xFF00):
                self.cycles += 1
            self.PC = address
        else:
            self.cycles = 0

    def op_bra(self, address_func):
        address, _, _ = address_func()
        if (address & 0xFF00) != (self.PC & 0xFF00):
            self.cycles += 1
        self.PC = address

    def op_brk(self, _):
        self.P |= Status['B']
        self.PC += 1
        self._push_stack((self.PC & 0xFF00) >> 8)  # PC high byte
        self._push_stack(self.PC & 0xFF)  # PC Low byte
        self._push_stack(self.P)  # Status register
        self.P |= Status['I']
        self.P &= ~Status['D']
        irq_location = 0xFFFE
        self.PC = self.bus[irq_location] | self.bus[irq_location + 1] << 8

    def op_bvc(self, address_func):
        address, _, _ = address_func()
        if not self.P & Status['V']:
            if (address & 0xFF00) != (self.PC & 0xFF00):
                self.cycles += 1
            self.PC = address
        else:
            self.cycles = 0

    def op_bvs(self, address_func):
        address, _, _ = address_func()
        if self.P & Status['V']:
            if (address & 0xFF00) != (self.PC & 0xFF00):
                self.cycles += 1
            self.PC = address
        else:
            self.cycles = 0

    def op_clc(self, _):
        self.P &= ~Status['C']

    def op_cld(self, _):
        self.P &= ~Status['D']

    def op_cli(self, _):
        self.P &= ~Status['I']

    def op_clv(self, _):
        self.P &= ~Status['V']

    def op_cmp(self, address_func):
        _, operand, extra_cycle = address_func()
        if extra_cycle:
            self.cycles += 1
        self._set_if_true(operand == self.A, 'Z')
        self._set_if_true(self.A >= operand, 'C')
        self._set_if_true((self.A - operand) & 0x80, 'N')

    def op_cpx(self, address_func):
        _, operand, extra_cycle = address_func()
        self._set_if_true(operand == self.X, 'Z')
        self._set_if_true(self.X >= operand, 'C')
        self._set_if_true((self.X - operand) & 0x80, 'N')

    def op_cpy(self, address_func):
        _, operand, extra_cycle = address_func()
        self._set_if_true(operand == self.Y, 'Z')
        self._set_if_true(self.Y >= operand, 'C')
        self._set_if_true((self.Y - operand) & 0x80, 'N')

    def op_dec(self, address_func):
        address, operand, _ = address_func()
        operand = (operand - 1) & 0xFF
        self._set_if_true(operand == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')
        if address is 'ACCUMULATOR':
            self.A = operand
        else:
            self.bus[address] = operand

    def op_dex(self, _):
        operand = (self.X - 1) & 0xFF
        self._set_if_true(operand == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')
        self.X = operand

    def op_dey(self, _):
        operand = (self.Y - 1) & 0xFF
        self._set_if_true(operand == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')
        self.Y = operand

    def op_eor(self, address_func):
        _, operand, extra_cycle = address_func()
        if extra_cycle:
            self.cycles += 1
        out = self.A ^ operand
        self._set_if_true(out == 0, 'Z')
        self._set_if_true(out & 0x80, 'N')
        self.A = out

    def op_inc(self, address_func):
        address, operand, _ = address_func()
        operand = (operand + 1) & 0xFF
        self._set_if_true(operand == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')
        if address is 'ACCUMULATOR':
            self.A = operand
        else:
            self.bus[address] = operand

    def op_inx(self, _):
        operand = (self.X + 1) & 0xFF
        self._set_if_true(operand == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')
        self.X = operand

    def op_iny(self, _):
        operand = (self.Y + 1) & 0xFF
        self._set_if_true(operand == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')
        self.Y = operand

    def op_jmp(self, address_func):
        address, _, _ = address_func()
        self.PC = address

    def op_jsr(self, address_func):
        address, _, _ = address_func()
        self.PC -= 1
        self._push_stack((self.PC & 0xFF00) >> 8)  # PC high byte
        self._push_stack(self.PC & 0xFF)  # PC Low byte
        self.PC = address

    def op_lda(self, address_func):
        _, operand, extra_cycle = address_func()
        if extra_cycle:
            self.cycles += 1
        self._set_if_true(operand == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')
        self.A = operand

    def op_ldx(self, address_func):
        _, operand, extra_cycle = address_func()
        if extra_cycle:
            self.cycles += 1
        self._set_if_true(operand == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')
        self.X = operand

    def op_ldy(self, address_func):
        _, operand, extra_cycle = address_func()
        if extra_cycle:
            self.cycles += 1
        self._set_if_true(operand == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')
        self.Y = operand

    def op_lsr(self, address_func):
        address, operand, _ = address_func()
        self._set_if_true(operand & 0x01, 'C')
        operand = operand >> 1
        self._set_if_true(operand == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')

        if address is 'ACCUMULATOR':
            self.A = operand
        else:
            self.bus[address] = operand

    def op_nop(self, _):
        pass

    def op_ora(self, address_func):
        _, operand, extra_cycle = address_func()
        if extra_cycle:
            self.cycles += 1
        operand = operand | self.A
        self._set_if_true(operand == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')
        self.A = operand

    def op_pha(self, _):
        self._push_stack(self.A)

    def op_php(self, _):
        self.P |= Status['B']  # Undocumented behaviour?
        self._push_stack(self.P)

    def op_phx(self, _):
        self._push_stack(self.X)

    def op_phy(self, _):
        self._push_stack(self.Y)

    def op_pla(self, _):
        data = self._pop_stack()
        self._set_if_true(data == 0, 'Z')
        self._set_if_true(data & 0x80, 'N')
        self.A = data

    def op_plp(self, _):
        self.P = self._pop_stack() | Status['U']  # Unused bit must be set at all times

    def op_plx(self, _):
        data = self._pop_stack()
        self._set_if_true(data == 0, 'Z')
        self._set_if_true(data & 0x80, 'N')
        self.X = data

    def op_ply(self, _):
        data = self._pop_stack()
        self._set_if_true(data == 0, 'Z')
        self._set_if_true(data & 0x80, 'N')
        self.Y = data

    def op_rmb0(self, address_func):
        address, operand, _ = address_func()
        n = 0
        operand = operand & ~(1 << n)
        self.bus[address] = operand

    def op_rmb1(self, address_func):
        address, operand, _ = address_func()
        n = 1
        operand = operand & ~(1 << n)
        self.bus[address] = operand

    def op_rmb2(self, address_func):
        address, operand, _ = address_func()
        n = 2
        operand = operand & ~(1 << n)
        self.bus[address] = operand

    def op_rmb3(self, address_func):
        address, operand, _ = address_func()
        n = 3
        operand = operand & ~(1 << n)
        self.bus[address] = operand

    def op_rmb4(self, address_func):
        address, operand, _ = address_func()
        n = 4
        operand = operand & ~(1 << n)
        self.bus[address] = operand

    def op_rmb5(self, address_func):
        address, operand, _ = address_func()
        n = 5
        operand = operand & ~(1 << n)
        self.bus[address] = operand

    def op_rmb6(self, address_func):
        address, operand, _ = address_func()
        n = 6
        operand = operand & ~(1 << n)
        self.bus[address] = operand

    def op_rmb7(self, address_func):
        address, operand, _ = address_func()
        n = 7
        operand = operand & ~(1 << n)
        self.bus[address] = operand

    def op_rol(self, address_func):
        address, operand, _ = address_func()
        to_carry = operand & 0x80
        if self.P & Status['C']:
            carry = 1
        else:
            carry = 0
        operand = ((operand << 1) & 0xFF) + carry
        self._set_if_true(to_carry, 'C')
        self._set_if_true(operand == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')

        if address is 'ACCUMULATOR':
            self.A = operand
        else:
            self.bus[address] = operand

    def op_ror(self, address_func):
        address, operand, _ = address_func()
        to_carry = operand & 0x01
        if self.P & Status['C']:
            carry = 0x80
        else:
            carry = 0
        operand = ((operand >> 1) & 0xFF) + carry
        self._set_if_true(to_carry, 'C')
        self._set_if_true(operand == 0, 'Z')
        self._set_if_true(operand & 0x80, 'N')

        if address is 'ACCUMULATOR':
            self.A = operand
        else:
            self.bus[address] = operand

    def op_rti(self, _):
        self.P = self._pop_stack() | Status['U']  # Unused bit must be set
        low = self._pop_stack()
        high = self._pop_stack()
        self.PC = (high << 8) + low

    def op_rts(self, _):
        low = self._pop_stack()
        high = self._pop_stack()
        self.PC = (high << 8) + low + 1

    def op_sbc(self, address_func):
        _, operand, extra_cycle = address_func()
        if extra_cycle:
            self.cycles += 1

        if self.P & Status['D']:

            # Calculate 99 - operand then add
            operand = (0x90 - (operand & 0xF0)) + (0x09 - (operand & 0x0F))
            if self.P & Status['C']:
                carry = 1
            else:
                carry = 0
            intermediate = (self.A & 0x0F) + (operand & 0x0F) + carry

            if intermediate >= 0x0A:
                intermediate = ((intermediate + 0x06) & 0x0F) + 0x10

            output = (self.A & 0xF0) + (operand & 0xF0) + intermediate
            self._set_if_true(output > 0xFF, 'V')
            if output >= 0xA0:
                output += 0x60
            self._set_if_true(output >= 0x100, 'C')
            output &= 0xFF
            self._set_if_true(output & 0x80, 'N')
            self._set_if_true(output == 0, 'Z')

            # if self.P & Status['C']:
            #     carry = 1
            # else:
            #     carry = 0
            # intermediate = (self.A & 0x0F) - (operand & 0x0F) + carry - 1
            #
            # if intermediate < 0x00:
            #     intermediate = ((intermediate - 0x06) & 0x0F) - 0x10
            #
            # output = (self.A & 0xF0) - (operand & 0xF0) + intermediate
            # self._set_if_true(output < -127, 'V')
            # if output < 0x00:
            #     output -= 0x60
            # self._set_if_true(output >= 0x100, 'C')
            # output &= 0xFF
            # self._set_if_true(output & 0x80, 'N')
            # self._set_if_true(output == 0, 'Z')
        else:
            operand ^= 0xFF  # Invert bits then add
            if self.P & Status['C']:
                carry = 1
            else:
                carry = 0
            output = self.A + operand + carry

            # Set Flags
            self._set_if_true(output > 0xFF, 'C')
            output &= 0xFF
            self._set_if_true(output == 0, 'Z')
            self._set_if_true(output & 0x80, 'N')
            v_flag = 0
            if self.A & 0x80:
                v_flag += 1
            if operand & 0x80:
                v_flag += 1
            if output & 0x80:
                v_flag += 2
            self._set_if_true(v_flag == 2, 'V')
        self.A = output

    def op_sec(self, _):
        self.P |= Status['C']

    def op_sed(self, _):
        self.P |= Status['D']

    def op_sei(self, _):
        self.P |= Status['I']

    def op_smb0(self, address_func):
        address, operand, _ = address_func()
        n = 0
        operand = operand | (1 << n)
        self.bus[address] = operand

    def op_smb1(self, address_func):
        address, operand, _ = address_func()
        n = 1
        operand = operand | (1 << n)
        self.bus[address] = operand

    def op_smb2(self, address_func):
        address, operand, _ = address_func()
        n = 2
        operand = operand | (1 << n)
        self.bus[address] = operand

    def op_smb3(self, address_func):
        address, operand, _ = address_func()
        n = 3
        operand = operand | (1 << n)
        self.bus[address] = operand

    def op_smb4(self, address_func):
        address, operand, _ = address_func()
        n = 4
        operand = operand | (1 << n)
        self.bus[address] = operand

    def op_smb5(self, address_func):
        address, operand, _ = address_func()
        n = 5
        operand = operand | (1 << n)
        self.bus[address] = operand

    def op_smb6(self, address_func):
        address, operand, _ = address_func()
        n = 6
        operand = operand | (1 << n)
        self.bus[address] = operand

    def op_smb7(self, address_func):
        address, operand, _ = address_func()
        n = 7
        operand = operand | (1 << n)
        self.bus[address] = operand

    def op_sta(self, address_func):
        address, _, _ = address_func()
        self.bus[address] = self.A

    @staticmethod
    def op_stp(_):
        print('STP Called')

    def op_stx(self, address_func):
        address, _, _ = address_func()
        self.bus[address] = self.X

    def op_sty(self, address_func):
        address, _, _ = address_func()
        self.bus[address] = self.Y

    def op_stz(self, address_func):
        address, _, _ = address_func()
        self.bus[address] = 0

    def op_tax(self, _):
        self._set_if_true(self.A == 0, 'Z')
        self._set_if_true(self.A & 0x80, 'N')
        self.X = self.A

    def op_tay(self, _):
        self._set_if_true(self.A == 0, 'Z')
        self._set_if_true(self.A & 0x80, 'N')
        self.Y = self.A

    def op_trb(self, address_func):
        address, operand, _ = address_func()
        self._set_if_true((operand & self.A) == 0, 'Z')
        operand &= ~self.A
        self.bus[address] = operand

    def op_tsb(self, address_func):
        address, operand, _ = address_func()
        self._set_if_true((operand & self.A) == 0, 'Z')
        operand |= self.A
        self.bus[address] = operand

    def op_tsx(self, _):
        self._set_if_true(self.S == 0, 'Z')
        self._set_if_true(self.S & 0x80, 'N')
        self.X = self.S

    def op_txa(self, _):
        self._set_if_true(self.X == 0, 'Z')
        self._set_if_true(self.X & 0x80, 'N')
        self.A = self.X

    def op_txs(self, _):
        self.S = self.X

    def op_tya(self, _):
        self._set_if_true(self.Y == 0, 'Z')
        self._set_if_true(self.Y & 0x80, 'N')
        self.A = self.Y

    @staticmethod
    def op_wai(_):
        print('WAI CALLED')

    @staticmethod
    def op_xxx(address_func):
        _, _, _ = address_func()  # Eat up required bytes
        print('XXX CALLED')


class Address6502(abc.ABC):

    def __init__(self, bus):
        self.A = 0
        self.X = 0
        self.Y = 0
        self.S = 0
        self.PC = 0
        self.bus = bus

    @abc.abstractmethod
    def _read_pc(self): pass

    @abc.abstractmethod
    def _read_bytes_pc(self, length): pass

    @abc.abstractmethod
    def _pop_stack(self): pass

    @abc.abstractmethod
    def _push_stack(self, val): pass

    @property
    @abc.abstractmethod
    def zero_page_bug(self): pass

    def absolute(self):
        address = self._read_bytes_pc(2)
        address = address[0] + (address[1] << 8)
        return address, self.bus[address], False

    def absolute_x(self):
        address, _, _ = self.absolute()
        address_out = address + self.X
        if (address_out & 0xFF00) != (address & 0xFF00):
            extra_cycle = True
        else:
            extra_cycle = False
        return address_out, self.bus[address_out], extra_cycle

    def absolute_indirect_x(self):
        address, _, _ = self.absolute_x()
        if self.zero_page_bug and ((address & 0x00FF) == 0xFF):
            address_out = (self.bus[address & 0xFF00] << 8) | self.bus[address]
        else:
            address_out = (self.bus[address + 1] << 8) | self.bus[address]
        return address_out, self.bus[address_out], False

    def absolute_y(self):
        address, _, _ = self.absolute()
        address_out = address + self.Y
        if (address_out & 0xFF00) != (address & 0xFF00):
            extra_cycle = True
        else:
            extra_cycle = False
        return address_out, self.bus[address_out], extra_cycle

    def accumulator(self):
        return 'ACCUMULATOR', self.A, False

    def immediate(self):
        out = self._read_pc()
        return self.PC, out, False

    @staticmethod
    def implied():
        return None, None, False

    def indirect(self):
        address, _, _ = self.absolute()
        if self.zero_page_bug and ((address & 0x00FF) == 0xFF):
            address_out = (self.bus[address & 0xFF00] << 8) | self.bus[address]
        else:
            address_out = (self.bus[address + 1] << 8) | self.bus[address]
        return address_out, self.bus[address_out], False
    
    def relative(self):
        offset = self._read_pc()
        if offset & 0x80:
            offset -= (1 << 8)
        address_out = self.PC + offset
        return address_out, self.bus[address_out], False

    def stack(self):
        return 0x0100 + self.S, self.bus[self.S], False

    def zero_page(self):
        address_out = self._read_pc()
        return address_out, self.bus[address_out], False

    def zero_page_relative(self):
        _, operand, _ = self.zero_page()
        address, _, _ = self.relative()
        return address, operand, False

    def zero_page_x(self):
        address, _, _ = self.zero_page()
        address_out = (address + self.X) & 0x00FF
        return address_out, self.bus[address_out], False

    def zero_page_y(self):
        address, _, _ = self.zero_page()
        address_out = (address + self.Y) & 0x00FF
        return address_out, self.bus[address_out], False

    def zero_page_indirect(self):
        address, _, _ = self.zero_page()
        if (address & 0x00FF) == 0xFF:
            address_out = (self.bus[address & 0xFF00] << 8) | self.bus[address]
        else:
            address_out = (self.bus[address + 1] << 8) | self.bus[address]
        return address_out, self.bus[address_out], False

    def zero_page_indirect_x(self):
        address, _, _ = self.zero_page_x()
        if (address & 0x00FF) == 0xFF:
            address_out = (self.bus[address & 0xFF00] << 8) | self.bus[address]
        else:
            address_out = (self.bus[address + 1] << 8) | self.bus[address]
        return address_out, self.bus[address_out], False

    def zero_page_indirect_y(self):
        address, _, _ = self.zero_page()
        if (address & 0x00FF) == 0xFF:
            address_out = ((self.bus[address & 0xFF00] << 8) | self.bus[address]) + self.Y
        else:
            address_out = ((self.bus[address + 1] << 8) | self.bus[address]) + self.Y
        return address_out, self.bus[address_out], False

    def address_lengths(self, func):
        lengths = {
            self.absolute: 2,
            self.absolute_indirect_x: 2,
            self.absolute_x: 2,
            self.absolute_y: 2,
            self.accumulator: 0,
            self.immediate: 1,
            self.implied: 0,
            self.indirect: 2,
            self.relative: 1,
            self.stack: 0,
            self.zero_page: 1,
            self.zero_page_relative: 2,
            self.zero_page_indirect: 1,
            self.zero_page_indirect_x: 1,
            self.zero_page_indirect_y: 1,
            self.zero_page_x: 1,
            self.zero_page_y: 1,
        }
        return lengths[func]

    @staticmethod
    def _twos_complement(val):
        if val & 0x80:
            return val - (1 << 8)
        else:
            return val

    def address_text(self, func, text, pc):
        mapping = {
            self.absolute: '${1:02X}{0:02X} [a]',
            self.absolute_indirect_x: '$({1:02X}{0:02X}, X) [(a,x)]',
            self.absolute_x: '${1:02X}{0:02X}, X [a, x]',
            self.absolute_y: '${1:02X}{0:02X}, Y [a, y]',
            self.accumulator: '[Acc]',
            self.immediate: '#{0:02X} [Imm]',
            self.implied: '[Imp]',
            self.indirect: '$({1:02X}{0:02X}) [(a)]',
            self.relative: '-> {{{0:04X}}} [Rel]',
            self.stack: '[Sta]',
            self.zero_page: '${0:02X} [zp]',
            self.zero_page_relative: '${0:02X} -> {{{1:04X}}} [zp Rel]',
            self.zero_page_indirect: '$({0:02X}) [(zp)]',
            self.zero_page_indirect_x: '$({0:02X}, X) [(zp, x)]',
            self.zero_page_indirect_y: '(${0:02X}), Y [(zp), y]',
            self.zero_page_x: '${0:02X}, X [zp, x]',
            self.zero_page_y: '${0:02X}, Y [zp, y]',
        }
        if func == self.relative:
            text[0] = pc + self.address_lengths(func) + 1 + self._twos_complement(text[0])
        elif func == self.zero_page_relative:
            text[1] = pc + self.address_lengths(func) + 1 + self._twos_complement(text[1])
        return mapping[func].format(*text)


class Cpu6502(Address6502, Ops6502):

    # noinspection PyMissingConstructor
    def __init__(self, bus, zero_page_bug=True):
        self._zero_page_bug = zero_page_bug
        self.bus = bus
        bus.cpu = self
        self.cycles = 0         # Records number of instructions until next instruction read
        self.A = 0x00           # Accumulator
        self.X = 0x00           # X register
        self.Y = 0x00           # Y register
        self.P = Status['UBI']    # Status register
        self.PC = 0x0000        # Program Counter register
        self.S = 0xFD           # Stack pointer

        self.matrix = [
            (self.op_brk, self.stack, 7),                   # 00
            (self.op_ora, self.zero_page_indirect_x, 6),    # 01
            (self.op_xxx, self.immediate, 0),               # 02
            (self.op_xxx, self.implied, 0),                 # 03
            (self.op_tsb, self.zero_page, 5),               # 04
            (self.op_ora, self.zero_page, 3),               # 05
            (self.op_asl, self.zero_page, 5),               # 06
            (self.op_rmb0, self.zero_page, 5),              # 07
            (self.op_php, self.stack, 3),                   # 08
            (self.op_ora, self.immediate, 2),               # 09
            (self.op_asl, self.accumulator, 2),             # 0A
            (self.op_xxx, self.implied, 0),                 # 0B
            (self.op_tsb, self.absolute, 6),                # 0C
            (self.op_ora, self.absolute, 4),                # 0D
            (self.op_asl, self.absolute, 6),                # 0E
            (self.op_bbr0, self.zero_page_relative, 5),     # 0F

            (self.op_bpl, self.relative, 2),                # 10
            (self.op_ora, self.zero_page_indirect_y, 5),    # 11
            (self.op_ora, self.zero_page_indirect, 5),      # 12
            (self.op_xxx, self.implied, 0),                 # 13
            (self.op_trb, self.zero_page, 5),               # 14
            (self.op_ora, self.zero_page_x, 4),             # 15
            (self.op_asl, self.zero_page_x, 6),             # 16
            (self.op_rmb1, self.zero_page, 5),              # 17
            (self.op_clc, self.implied, 2),                 # 18
            (self.op_ora, self.absolute_y, 4),              # 19
            (self.op_inc, self.accumulator, 2),             # 1A
            (self.op_xxx, self.implied, 0),                 # 1B
            (self.op_trb, self.absolute, 6),                # 1C
            (self.op_ora, self.absolute_x, 4),              # 1D
            (self.op_asl, self.absolute_x, 7),              # 1E
            (self.op_bbr1, self.zero_page_relative, 5),     # 1F

            (self.op_jsr, self.absolute, 6),                # 20
            (self.op_and, self.zero_page_indirect_x, 6),    # 21
            (self.op_xxx, self.immediate, 0),               # 22
            (self.op_xxx, self.implied, 0),                 # 23
            (self.op_bit, self.zero_page, 3),               # 24
            (self.op_and, self.zero_page, 3),               # 25
            (self.op_rol, self.zero_page, 5),               # 26
            (self.op_rmb2, self.zero_page, 5),              # 27
            (self.op_plp, self.stack, 4),                   # 28
            (self.op_and, self.immediate, 2),               # 29
            (self.op_rol, self.accumulator, 2),             # 2A
            (self.op_xxx, self.implied, 0),                 # 2B
            (self.op_bit, self.absolute, 4),                # 2C
            (self.op_and, self.absolute, 4),                # 2D
            (self.op_rol, self.absolute, 6),                # 2E
            (self.op_bbr2, self.zero_page_relative, 5),     # 2F

            (self.op_bmi, self.relative, 2),                # 30
            (self.op_and, self.zero_page_indirect_y, 5),    # 31
            (self.op_and, self.zero_page_indirect, 5),      # 32
            (self.op_xxx, self.implied, 0),                 # 33
            (self.op_bit, self.zero_page_x, 4),             # 34
            (self.op_and, self.zero_page_x, 4),             # 35
            (self.op_rol, self.zero_page_x, 6),             # 36
            (self.op_rmb3, self.zero_page, 5),              # 37
            (self.op_sec, self.implied, 2),                 # 38
            (self.op_and, self.absolute_y, 4),              # 39
            (self.op_dec, self.accumulator, 2),             # 3A
            (self.op_xxx, self.implied, 0),                 # 3B
            (self.op_bit, self.absolute_x, 4),              # 3C
            (self.op_and, self.absolute_x, 4),              # 3D
            (self.op_rol, self.absolute_x, 7),              # 3E
            (self.op_bbr3, self.zero_page_relative, 5),     # 3F

            (self.op_rti, self.stack, 6),                   # 40
            (self.op_eor, self.zero_page_indirect_x, 6),    # 41
            (self.op_xxx, self.immediate, 0),               # 42
            (self.op_xxx, self.implied, 0),                 # 43
            (self.op_xxx, self.immediate, 0),               # 44
            (self.op_eor, self.zero_page, 3),               # 45
            (self.op_lsr, self.zero_page, 5),               # 46
            (self.op_rmb4, self.zero_page, 5),              # 47
            (self.op_pha, self.stack, 3),                   # 48
            (self.op_eor, self.immediate, 2),               # 49
            (self.op_lsr, self.accumulator, 2),             # 4A
            (self.op_xxx, self.implied, 0),                 # 4B
            (self.op_jmp, self.absolute, 3),                # 4C
            (self.op_eor, self.absolute, 4),                # 4D
            (self.op_lsr, self.absolute, 6),                # 4E
            (self.op_bbr4, self.zero_page_relative, 5),     # 4F

            (self.op_bvc, self.relative, 2),                # 50
            (self.op_eor, self.zero_page_indirect_y, 5),    # 51
            (self.op_eor, self.zero_page_indirect, 5),      # 52
            (self.op_xxx, self.implied, 0),                 # 53
            (self.op_xxx, self.immediate, 0),               # 54
            (self.op_eor, self.zero_page_x, 4),             # 55
            (self.op_lsr, self.zero_page_x, 6),             # 56
            (self.op_rmb5, self.zero_page, 5),              # 57
            (self.op_cli, self.implied, 2),                 # 58
            (self.op_eor, self.absolute_y, 4),              # 59
            (self.op_phy, self.stack, 3),                   # 5A
            (self.op_xxx, self.implied, 0),                 # 5B
            (self.op_xxx, self.absolute, 0),                # 5C
            (self.op_eor, self.absolute_x, 4),              # 5D
            (self.op_lsr, self.absolute_x, 7),              # 5E
            (self.op_bbr5, self.zero_page_relative, 5),     # 5F

            (self.op_rts, self.stack, 6),                   # 60
            (self.op_adc, self.zero_page_indirect_x, 6),    # 61
            (self.op_xxx, self.immediate, 0),               # 62
            (self.op_xxx, self.implied, 0),                 # 63
            (self.op_stz, self.zero_page, 3),               # 64
            (self.op_adc, self.zero_page, 3),               # 65
            (self.op_ror, self.zero_page, 5),               # 66
            (self.op_rmb6, self.zero_page, 5),              # 67
            (self.op_pla, self.stack, 4),                   # 68
            (self.op_adc, self.immediate, 2),               # 69
            (self.op_ror, self.accumulator, 2),             # 6A
            (self.op_xxx, self.implied, 0),                 # 6B
            (self.op_jmp, self.indirect, 6),                # 6C
            (self.op_adc, self.absolute, 4),                # 6D
            (self.op_ror, self.absolute, 6),                # 6E
            (self.op_bbr6, self.zero_page_relative, 5),     # 6F

            (self.op_bvs, self.relative, 2),                # 70
            (self.op_adc, self.zero_page_indirect_y, 5),    # 71
            (self.op_adc, self.zero_page_indirect, 5),      # 72
            (self.op_xxx, self.implied, 0),                 # 73
            (self.op_stz, self.zero_page_x, 4),             # 74
            (self.op_adc, self.zero_page_x, 4),             # 75
            (self.op_ror, self.zero_page_x, 6),             # 76
            (self.op_rmb7, self.zero_page, 5),              # 77
            (self.op_sei, self.implied, 2),                 # 78
            (self.op_adc, self.absolute_y, 4),              # 79
            (self.op_ply, self.stack, 4),                   # 7A
            (self.op_xxx, self.implied, 0),                 # 7B
            (self.op_jmp, self.absolute_indirect_x, 6),     # 7C
            (self.op_adc, self.absolute_x, 4),              # 7D
            (self.op_ror, self.absolute_x, 7),              # 7E
            (self.op_bbr7, self.zero_page_relative, 5),     # 7F

            (self.op_bra, self.relative, 3),                # 80
            (self.op_sta, self.zero_page_indirect_x, 6),    # 81
            (self.op_xxx, self.immediate, 0),               # 82
            (self.op_xxx, self.implied, 0),                 # 83
            (self.op_sty, self.zero_page, 3),               # 84
            (self.op_sta, self.zero_page, 3),               # 85
            (self.op_stx, self.zero_page, 3),               # 86
            (self.op_smb0, self.zero_page, 5),              # 87
            (self.op_dey, self.implied, 2),                 # 88
            (self.op_bit_imm, self.immediate, 2),           # 89
            (self.op_txa, self.implied, 2),                 # 8A
            (self.op_xxx, self.implied, 0),                 # 8B
            (self.op_sty, self.absolute, 4),                # 8C
            (self.op_sta, self.absolute, 4),                # 8D
            (self.op_stx, self.absolute, 4),                # 8E
            (self.op_bbs0, self.zero_page_relative, 5),     # 8F

            (self.op_bcc, self.relative, 2),                # 90
            (self.op_sta, self.zero_page_indirect_y, 6),    # 91
            (self.op_sta, self.zero_page_indirect, 5),      # 92
            (self.op_xxx, self.implied, 0),                 # 93
            (self.op_sty, self.zero_page_x, 4),             # 94
            (self.op_sta, self.zero_page_x, 4),             # 95
            (self.op_stx, self.zero_page_y, 4),             # 96
            (self.op_smb1, self.zero_page, 5),              # 97
            (self.op_tya, self.implied, 2),                 # 98
            (self.op_sta, self.absolute_y, 5),              # 99
            (self.op_txs, self.implied, 2),                 # 9A
            (self.op_xxx, self.implied, 0),                 # 9B
            (self.op_stz, self.absolute, 4),                # 9C
            (self.op_sta, self.absolute_x, 5),              # 9D
            (self.op_stz, self.absolute_x, 5),              # 9E
            (self.op_bbs1, self.zero_page_relative, 5),     # 9F

            (self.op_ldy, self.immediate, 2),               # A0
            (self.op_lda, self.zero_page_indirect_x, 6),    # A1
            (self.op_ldx, self.immediate, 2),               # A2
            (self.op_xxx, self.implied, 0),                 # A3
            (self.op_ldy, self.zero_page, 3),               # A4
            (self.op_lda, self.zero_page, 3),               # A5
            (self.op_ldx, self.zero_page, 3),               # A6
            (self.op_smb2, self.zero_page, 5),              # A7
            (self.op_tay, self.implied, 2),                 # A8
            (self.op_lda, self.immediate, 2),               # A9
            (self.op_tax, self.implied, 2),                 # AA
            (self.op_xxx, self.implied, 0),                 # AB
            (self.op_ldy, self.absolute, 4),                # AC
            (self.op_lda, self.absolute, 5),                # AD
            (self.op_ldx, self.absolute, 5),                # AE
            (self.op_bbs2, self.zero_page_relative, 5),     # AF

            (self.op_bcs, self.relative, 2),                # B0
            (self.op_lda, self.zero_page_indirect_y, 5),    # B1
            (self.op_lda, self.zero_page_indirect, 5),      # B2
            (self.op_xxx, self.implied, 0),                 # B3
            (self.op_ldy, self.zero_page_x, 4),             # B4
            (self.op_lda, self.zero_page_x, 4),             # B5
            (self.op_ldx, self.zero_page_y, 4),             # B6
            (self.op_smb3, self.zero_page, 5),              # B7
            (self.op_clv, self.implied, 2),                 # B8
            (self.op_lda, self.absolute_y, 2),              # B9
            (self.op_tsx, self.implied, 2),                 # BA
            (self.op_xxx, self.implied, 0),                 # BB
            (self.op_ldy, self.absolute_x, 4),              # BC
            (self.op_lda, self.absolute_x, 4),              # BD
            (self.op_ldx, self.absolute_y, 4),              # BE
            (self.op_bbs3, self.zero_page_relative, 5),     # BF

            (self.op_cpy, self.immediate, 2),               # C0
            (self.op_cmp, self.zero_page_indirect_x, 6),    # C1
            (self.op_xxx, self.immediate, 0),               # C2
            (self.op_xxx, self.implied, 0),                 # C3
            (self.op_cpy, self.zero_page, 3),               # C4
            (self.op_cmp, self.zero_page, 3),               # C5
            (self.op_dec, self.zero_page, 5),               # C6
            (self.op_smb4, self.zero_page, 5),              # C7
            (self.op_iny, self.implied, 2),                 # C8
            (self.op_cmp, self.immediate, 2),               # C9
            (self.op_dex, self.implied, 2),                 # CA
            (self.op_wai, self.implied, 0),                 # CB
            (self.op_cpy, self.absolute, 4),                # CC
            (self.op_cmp, self.absolute, 4),                # CD
            (self.op_dec, self.absolute, 6),                # CE
            (self.op_bbs4, self.zero_page_relative, 5),     # CF

            (self.op_bne, self.relative, 2),                # D0
            (self.op_cmp, self.zero_page_indirect_y, 5),    # D1
            (self.op_cmp, self.zero_page_indirect, 5),      # D2
            (self.op_xxx, self.implied, 0),                 # D3
            (self.op_xxx, self.immediate, 0),               # D4
            (self.op_cmp, self.zero_page_x, 4),             # D5
            (self.op_dec, self.zero_page_x, 6),             # D6
            (self.op_smb5, self.zero_page, 5),              # D7
            (self.op_cld, self.implied, 2),                 # D8
            (self.op_cmp, self.absolute_y, 4),              # D9
            (self.op_phx, self.stack, 3),                   # DA
            (self.op_stp, self.implied, 0),                 # DB
            (self.op_xxx, self.absolute, 0),                # DC
            (self.op_cmp, self.absolute_x, 4),              # DD
            (self.op_dec, self.absolute_x, 7),              # DE
            (self.op_bbs5, self.zero_page_relative, 5),     # DF

            (self.op_cpx, self.immediate, 2),               # E0
            (self.op_sbc, self.zero_page_indirect_x, 6),    # E1
            (self.op_xxx, self.immediate, 0),               # E2
            (self.op_xxx, self.implied, 0),                 # E3
            (self.op_cpx, self.zero_page, 3),               # E4
            (self.op_sbc, self.zero_page, 3),               # E5
            (self.op_inc, self.zero_page, 5),               # E6
            (self.op_smb6, self.zero_page, 5),              # E7
            (self.op_inx, self.implied, 2),                 # E8
            (self.op_sbc, self.immediate, 2),               # E9
            (self.op_nop, self.implied, 2),                 # EA
            (self.op_xxx, self.implied, 0),                 # EB
            (self.op_cpx, self.absolute, 4),                # EC
            (self.op_sbc, self.absolute, 4),                # ED
            (self.op_inc, self.absolute, 6),                # EE
            (self.op_bbs6, self.zero_page_relative, 5),     # EF

            (self.op_beq, self.relative, 2),                # F0
            (self.op_sbc, self.zero_page_indirect_y, 5),    # F1
            (self.op_sbc, self.zero_page_indirect, 5),      # F2
            (self.op_xxx, self.implied, 0),                 # F3
            (self.op_xxx, self.immediate, 0),               # F4
            (self.op_sbc, self.zero_page_x, 4),             # F5
            (self.op_inc, self.zero_page_x, 6),             # F6
            (self.op_smb7, self.zero_page, 5),              # F7
            (self.op_sed, self.implied, 2),                 # F8
            (self.op_sbc, self.absolute_y, 4),              # F9
            (self.op_plx, self.stack, 4),                   # FA
            (self.op_xxx, self.implied, 0),                 # FB
            (self.op_xxx, self.absolute, 0),                # FC
            (self.op_sbc, self.absolute_x, 4),              # FD
            (self.op_inc, self.absolute_x, 7),              # FE
            (self.op_bbs7, self.zero_page_relative, 5),     # FF
        ]

    @property
    def zero_page_bug(self):
        return self._zero_page_bug

    def _read_pc(self):
        out = self.bus[self.PC]
        self.PC += 1
        return out

    def _read_bytes_pc(self, length):
        return [self._read_pc() for _ in range(length)]
    
    def _pop_stack(self):
        self.S = (self.S + 1) & 0xFF
        out = 0x0100 + self.S
        return self.bus[out]

    def _push_stack(self, val):
        address = 0x0100 + self.S
        self.S = (self.S - 1) & 0xFF
        self.bus[address] = val

    def reset(self):
        reset_location = 0xFFFC
        self.PC = self.bus[reset_location] | self.bus[reset_location+1] << 8
        self.P = Status['UBI']
        self.A = 0x00  # Accumulator
        self.X = 0x00  # X register
        self.Y = 0x00  # Y register
        self.S = 0xFD  # Stack pointer
        self.cycles = 8

    def irq(self):
        if not self.P & Status['I']:
            self.P &= ~Status['B']
            self._push_stack((self.PC & 0xFF00) >> 8)  # PC high byte
            self._push_stack(self.PC & 0xFF)  # PC Low byte
            self._push_stack(self.P)

            irq_location = 0xFFFE
            self.PC = self.bus[irq_location] | self.bus[irq_location + 1] << 8
            self.cycles = 7

    def nmi(self):
        self.P &= ~ Status['B']
        self._push_stack((self.PC & 0xFF00) >> 8)  # PC high byte
        self._push_stack(self.PC & 0xFF)  # PC Low byte
        self._push_stack(self.P)  # Status register

        nmi_location = 0xFFFA
        self.PC = self.bus[nmi_location] | self.bus[nmi_location + 1] << 8
        self.cycles = 8

    def clock(self):
        if self.cycles == 0:
            op_code = self.bus[self.PC]
            self.PC += 1
            operation, address_mode, cycles = self.matrix[op_code]
            self.cycles = cycles
            operation(address_mode)
            return True
        self.cycles -= 1
        return False

    def list_commands(self, number=-1):
        temp_pc = self.PC
        out = OrderedDict()
        if number < 0:
            iterator = itertools.count()
        else:
            iterator = range(number)

        for _ in iterator:
            init_pc = temp_pc
            try:
                op_code = self.bus[temp_pc]
                temp_pc += 1
                operation, address_mode, _ = self.matrix[op_code]
                n_address = self.address_lengths(address_mode)
                address_values = []
                for _ in range(n_address):
                    address_values.append(self.bus[temp_pc])
                    temp_pc += 1
                address_text = self.address_text(address_mode, address_values, init_pc)
            except IndexError:
                break

            name = operation.__name__.split('_')[1].upper()
            out[init_pc] = f'{init_pc:04X}:    {name} {address_text}'
        return out
