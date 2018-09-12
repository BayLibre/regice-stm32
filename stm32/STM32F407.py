#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2018 BayLibre
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from libregice.device import Device
from regiceclock import ClockTree, Gate, Mux, PLL, Divider, FixedClock
from regiceclock import InvalidDivider

def get_vco_freq(pll):
    """
        Compute the PLL VCO frequency
        :param pll: Pll clock object
    """
    device = pll.device
    reg = device.RCC.PLLCFGR
    PLLN = reg.PLLN
    PLLM = reg.PLLM
    freq = pll.get_parent().get_freq() * (PLLN // PLLM)

    if PLLM < 2:
        raise InvalidDivider()
    if PLLN < 50 or PLLN > 432:
        raise InvalidDivider()

    return freq

def get_pll_freq(pll):
    """
        Compute the PLL frequency
        :param pll: Pll clock object
    """
    device = pll.device
    PLLP = device.RCC.PLLCFGR.PLLP
    PLLP = (PLLP + 1) * 2
    return pll.get_parent().get_freq() / PLLP

def get_usb_otg_fs_freq(pll):
    """
        Compute the USB PLL frequency
        :param pll: Pll clock object
    """
    device = pll.device
    PLLQ = device.RCC.PLLCFGR.PLLQ
    if PLLQ < 2:
        raise InvalidDivider()
    return pll.get_parent().get_freq() / PLLQ

def get_plli2s_vco_freq(pll):
    """
        Compute the VCO frequency of PLLI2S
        :param pll: Pll clock object
    """
    device = pll.device
    PLLI2SCFGR = device.RCC.PLLI2SCFGR
    PLLCFGR = device.RCC.PLLCFGR
    PLLN = PLLCFGR.PLLN
    PLLM = PLLCFGR.PLLM
    freq = pll.get_parent().get_freq() * (PLLI2SCFGR.PLLI2SNx // PLLM)

    if PLLM < 2:
        raise InvalidDivider()
    if PLLI2SCFGR.PLLI2SNx < 50 or PLLN > 432:
        raise InvalidDivider()

    return freq

def get_plli2s_freq(pll):
    """
        Compute the frequency of PLLI2S
        :param pll: Pll clock object
    """
    if not pll.enabled():
        return 0
    device = pll.device
    PLLI2SCFGR = device.RCC.PLLI2SCFGR
    return pll.get_parent().get_freq() / PLLI2SCFGR.PLLI2SRx

def hpre_get_div(div):
    """
        Compute the clock divider

        :param div: The value of register
        :return: The divider
    """
    if div < 0x8:
        return 1
    return 1 << (div & 0x7)

def ppre_get_div(div):
    """
        Compute the clock divider

        :param div: The value of register
        :return: The divider
    """
    if div < 0x4:
        return 1
    return 2 << (div & 0x3)

def hsertc_get_div(div):
    """
        Compute the clock divider

        :param div: The value of register
        :return: The divider, or None if clock has to be gated
    """
    if div < 2:
        return None
    return div

def make_table(field, compute_cb):
    """
        Generate a divider table

        This call a function to get the divider for each possible value of
        divider field.

        :param field: The divider field
        :param compute_cb: The function that convert a field value to divider
        :return: A clock divider table
    """
    table = {}
    for div in range(0, 1 << field.bitWidth):
        table[div] = compute_cb(div)
    return table

def MHz(freq):
    """
        Convert a frequency given in MHz to Hz

        :param freq: A frequency, given in MHz
        :return: The frequency converted in Hz
    """
    return freq * 1000 * 1000

class STM32F407(Device):
    def init_clock_sources(self):
        """
            Add the clock sources (e.g. oscillators) to clock tree

            Some clocks (e.g HSE) are board dependent, and their frequency
            could not be set here. They have to be set, at runtime,
            using command line parameters or board file.
        """
        FixedClock(tree=self.tree, name='LSI', freq=32000,
                   en_field=self.RCC.CSR.LSION, rdy_field=self.RCC.CSR.LSIRDY)
        FixedClock(tree=self.tree, name='LSE', freq=32768,
                   en_field=self.RCC.BDCR.LSEON, rdy_field=self.RCC.BDCR.LSERDY)
        FixedClock(tree=self.tree, name='HSI', freq=16000000,
                   en_field=self.RCC.CR.HSION, rdy_field=self.RCC.CR.HSIRDY)
        FixedClock(tree=self.tree, name='HSE',
                   en_field=self.RCC.CR.HSEON, rdy_field=self.RCC.CR.HSERDY)
        FixedClock(tree=self.tree, name='I2SCKIN')

    def init_plls(self):
        """
            Add PLL clocks to clock tree

            In addition of PLL clocks, there are two internals clocks
            also defined (e.g VCO clocks). They are internal to the PLL
            but because they are derived for PLL output and because we have
            apply a frequency constraint, they have been added as any clock.
        """
        reg = self.RCC.PLLCFGR
        Mux(tree=self.tree, name='PLLSRC', parents={0: 'HSI', 1: 'HSE'},
            mux_field=reg.PLLSRC)
        PLL(tree=self.tree, name='PLLVCO', parent='PLLSRC',
            get_freq=get_vco_freq, en_field=self.RCC.CR.PLLON,
            min=MHz(100), max=MHz(432))
        PLL(tree=self.tree, name='PLLCLK', parent='PLLVCO', get_freq=get_pll_freq)
        PLL(tree=self.tree, name='PLLUSBOTGFS', parent='PLLVCO',
            get_freq=get_usb_otg_fs_freq)
        PLL(tree=self.tree, name='PLLI2SVCO', parent='PLLSRC',
            get_freq=get_plli2s_vco_freq, en_field=self.RCC.CR.PLLI2SON,
            min=MHz(100), max=MHz(432))
        PLL(tree=self.tree, name='PLLI2S', parent='PLLI2SVCO',
            get_freq=get_plli2s_freq)

    def init_muxs(self):
        """
            Register clock mux to the clock tree
        """
        Mux(tree=self.tree, name="RTCSEL", mux_field=self.RCC.BDCR.RTCSEL,
            parents={0: None, 1: 'LSE', 2: 'LSI', 3: 'HSERTC'})
        # TODO add suppport of mux status
        Mux(tree=self.tree, name="SW", mux_field=self.RCC.CFGR.SW,
            parents={0: 'HSI', 1: 'HSE', 2: 'PLLCLK', 3: None})
        Mux(tree=self.tree, name="I2SSRC", mux_field=self.RCC.CFGR.I2SSRC,
            parents={0: 'PLLI2S', 1: 'I2SCKIN'})

    def init_dividers(self):
        """
            Add clock dividers to the clock tree
        """
        table = make_table(self.RCC.CFGR.RTCPRE, hsertc_get_div)
        Divider(tree=self.tree, name='HSERTC', parent='HSE',
                div_field=self.RCC.CFGR.RTCPRE, table=table,)
#                min=MHz(1), max=MHz(1))
        table = make_table(self.RCC.CFGR.HPRE, hpre_get_div)
        Divider(tree=self.tree, name='AHB', parent='SW',
                div_field=self.RCC.CFGR.HPRE, table=table, min=MHz(25))
        table = make_table(self.RCC.CFGR.PPRE1, ppre_get_div)
        Divider(tree=self.tree, name='APB1', parent='AHB',
                div_field=self.RCC.CFGR.PPRE1, table=table, max=MHz(45))
        Divider(tree=self.tree, name='APB2', parent='AHB',
                div_field=self.RCC.CFGR.PPRE2, table=table, max=MHz(90))

    def init_gates(self):
        """
            Add clock gates to the clock tree
        """
        gate_registers = [
            'AHB1ENR', 'AHB2ENR', 'AHB3ENR', 'APB1ENR', 'APB2ENR',
        ]

        for register_name in gate_registers:
            if 'AHB' in register_name:
                parent = register_name[:3]
            else:
                parent = register_name[:4]
            register = getattr(self.RCC, register_name)
            for field_name in register.fields:
                field = getattr(register, field_name)
                if 'ENR' in field_name:
                    name = field_name[:-3]
                else:
                    name = field_name[:-2]
                Gate(tree=self.tree,
                     name=name, parent=parent, en_field=field)
            Gate(tree=self.tree, name="RTC", parent="RTCSEL",
                 en_field=self.RCC.BDCR.RTCEN)

    def clock_init(self):
        """
            Init the clock tree
        """
        self.tree = ClockTree(self)
        self.tree.add_peripheral(self.RCC)
        self.init_clock_sources()
        self.init_plls()
        self.init_muxs()
        self.init_dividers()
        self.init_gates()

def device_init(svd, client):
    return STM32F407(svd, client)

def is_compatible_with(chip):
    """
        Test if the module is compatible with the device

        :field chip: Name of the device
        :return: True if the device is compatible with the module
    """
    compatible = [
        'STM32F407'
    ]
    return chip in compatible
