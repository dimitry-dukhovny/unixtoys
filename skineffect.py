#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint

# Table of constants from Karakas and Tariq (1988).
# Takes inputs in degrees instead of radians just to look cool, I guess.
kt_table = {
    0:   [ 0.25, -2.091, 0.0453, 5.1313, 1.8672, 1.6*(10**-1), 2.675 ],
    360: [ 0.25, -2.091, 0.0453, 5.1313, 1.8672, 1.6*(10**-1), 2.675 ],
    180: [ 0.5, -2.2025, 0.0943, 3.0373, 1.8115, 2.6*(10**-2), 4.532 ],
    120: [ 0.648, -2.018, 0.0634, 1.6136, 1.7770, 6.6*(10**-3), 5.320 ],
    90:  [ 0.726, -1.905, 0.1038, 1.5674, 1.6935, 1.9*(10**-3), 6.155 ],
    60:  [ 0.813, -1.898, 0.1023, 1.3654, 1.6490, 3.0*(10**-4), 7.509 ],
    45:  [ 0.860, -1.788, 0.2398, 1.1915, 1.6392, 4.6*(10**-5), 8.791 ],
}


class karakastariq:
    def __init__(self, phasing=None, k=None, k_h=None, k_s=None, k_v=None, h_perf=None, l_perf=None, r_perf=None, r_s=None, r_w=None, r_w_primed=None, s_d_0=None, s_h=None, s_v=None, s_wb=None):
        """
        Information collector class for near-well damage calculation.
        --------------
        phasing     == bore inclination in degrees
        --------------
        k           == permeability of the undamaged region
        --------------
        k_h         == horizontal permeability
        --------------
        k_s         == permeability of the damaged region
        --------------
        k_v         == vertical permeability
        --------------
        h_perf      == width of perforation
        --------------
        l_perf      == length of perforation
        --------------
        r_perf      == 
        --------------
        r_w         == well radius
        --------------
        r_s         == sum of well radius and damage penetration beyond the well
        --------------
        r_w_primed  == effective well bore radius
                    = kt_table[phasing][0]
        --------------
        s_d_0       == open-hole equivalent skin effect from hawkins()
        --------------
        s_h         == horizontal skin effect
                    = np.log(r_w / r_w_primed)
        --------------
        s_p         == perforation skin factor
                    = s_h + s_v + s_wb
        --------------
        s_v         == vertical pseudoskin
                    = 10**a * h_d**(b-1) * r_d**b
        --------------
        s_wb        == well bore blockage effect
                    = c_1 * (np.e**(c_2 * r_wd))
        --------------
        s_p_d       == 
                    = 
        """
        self.c = {
            "phasing": phasing,
            "k": k,
            "k_h": k_h,
            "k_s": k_s,
            "k_v": k_v,
            "h_perf": h_perf,
            "l_perf": l_perf,
            "r_perf": r_perf,
            "r_w": r_w,
            "r_s": r_s,
            "r_w_primed": r_w_primed,
            "s_d_0": s_d_0,
            "s_h": s_h,
            "s_p": None,
            "s_v": s_v,
            "s_wb": s_wb,
            "s_p_d": None,
        }
        self.chosen = None
        while str(self.chosen).strip().lower() != "quit":
            self.calculate()
            self.helptext()
            self.prompt()

    def helptext(self):
        self.h = {
            "phasing": ["bore inclination in degrees", self.c['phasing']],
            "k": ["permeability of the undamaged region", self.c['k']],
            "k_h": ["horizontal permeability", self.c['k_h']],
            "k_s": ["permeability of the damaged region", self.c['k_s']],
            "k_v": ["vertical permeability", self.c['k_v']],
            "h_perf": ["width of perforation", self.c['h_perf']],
            "l_perf": ["length of perforation", self.c['l_perf']],
            "r_perf": ["radius of perforation", self.c['r_perf']],
            "r_w": ["well radius", self.c['r_w']],
            "r_s": ["sum of well radius and damage penetration beyond the well", self.c['r_s']],
            "r_w_primed": ["effective well bore radius", self.c['r_w_primed']],
            "s_d_0": ["open-hole equivalent skin effect from hawkins()", self.c['s_d_0']],
            "s_h": ["horizontal skin effect; needs r_w, r_w_primed", self.c['s_h']],
            "s_p": ["perforation skin factor; needs s_h, s_v, s_wb", self.c['s_p']],
            "s_v": ["vertical pseudoskin; needs phasing, k_h, k_v, h_perf, l_perf", self.c['s_v']],
            "s_wb": ["well bore blockage effect; needs phasing, l_perf, r_w", self.c['s_wb']],
            "s_p_d": ["skin effect from damage, needs k, k_s, r_w, r_s, s_p", self.c['s_p_d']],
        }
        for k in self.h.keys():
            print("%s: %s\n %s" % (str(k), str(self.h[k][1]), str(self.h[k][0])))

    def statestate(self):
        """
        Print current knowns.
        """
        pprint(self.c)

    def prompt(self):
        self.chosen = input("Select a value to update or type quit to exit [quit]:  ")
        if self.chosen in self.c.keys():
            print(self.h[self.chosen][0])
            self.c[self.chosen] = promptforfloat(self.c[self.chosen], self.chosen)
            print("Recalculating.")
        elif self.chosen=="quit":
            print("Exiting.")
        else:
            pass

    def calculate(self):
        """
        Recalculate everything as if it was a spreadsheet.
        """
        orig = self.c["r_w_primed"]
        try:
            self.c["r_w_primed"] = effective_well_bore_radius(self.c['phasing'], self.c['r_w'], self.c['l_perf'])
        except:
            self.c["r_w_primed"] = orig
        orig = self.c["s_wb"]
        try:
            self.c["s_wb"] = skin_blockage(self.c['phasing'], self.c['l_perf'], self.c['r_w'])
        except:
            self.c["s_wb"] = orig
        orig = self.c["s_h"]
        try:
            self.c["s_h"] = skin_horizontal(self.c['r_w'], self.c['r_w_primed'])
        except:
            self.c["s_h"] = orig
        orig = self.c["s_v"]
        try:
            self.c["s_v"] = skin_vertical(self.c['phasing'], self.c['k_h'], self.c['k_v'], self.c['r_perf'], self.c['h_perf'], self.c['l_perf'])
        except:
            self.c["s_v"] = orig
        orig = self.c["s_p"]
        try:
            self.c["s_p"] = perforationskineffect(self.c['s_h'], self.c['s_v'], self.c['s_wb'])
        except:
            self.c["s_p"] = orig
        orig = self.c["s_p_d"]
        try:
            self.c["s_p_d"] = skineffect(self.c['k'], self.c['k_s'], self.c['r_s'], self.c['r_w'], self.c['s_p'])
        except:
            self.c["s_p_d"] = orig


class karakastariq_short:
    def __init__(self, k=None, k_s=None, r_s=None, r_w=None, s_p=None, s_d_0=None):
        """
        This is the near-well damage and perforations calculation class from
        6.6.1.5, equation 6-61.
        The return value is s_p_d.
        Feeding the open-hole equivalent skin effect from the Hawkins formula
        runs karakastariq_short.cse() when ( l_perf < r_s ).
        self.kt_se() should equal self.se()
        r_w     == well radius
        r_s     == sum of well radius and damage penetration beyond the well
        k       == permeability of the undamaged region
        k_s     == permeability of the damaged region
        s_p     == perforation skin factor
        s_d_0   == open-hole equivalent skin effect from hawkins()
        """
        self.k = k
        self.k_s = k_s
        self.r_s = r_s
        self.r_w = r_w
        self.s_p = s_p
        self.s_d_0 = s_d_0
        self.select()
        if self.shortform:
            self.kt_se()
        else:
            self.se()

    def select(self):
        """
        Choose how we want to do our math and whether we need more info.
        """
        enough = False
        while not enough:
            if (self.k!=None) and (self.k_s!=None) and (self.s_p!=None):
                if self.s_d_0!=None:
                    enough = True
                    self.shortform = True
                elif (self.r_s != None) and (self.r_w!=None):
                    enough = True
                    self.shortform = False
            if not enough:
                self.prompt()

    def kt_se(self):
        """
        Simplified formula with a given s_d_0.
        """
        self.s_p_d = self.s_d_0 + ( self.k / self.k_s ) * self.s_p
        return(self.s_p_d)

    def se(self):
        """
        Calculate skin effect without a given s_d_0.
        """
        self.s_p_d = (self.k / self.k_s - 1) * (np.log(self.r_s / self.r_w) + self.s_p)
        return(self.s_p_d)

    def prompt(self):
        """
        Demand information.
        """
        helptext = \
"""
    r_w     == well radius
    r_s     == sum of well radius and damage penetration beyond the
               well
    k       == permeability of the undamaged region
    k_s     == permeability of the damaged region
    s_p     == perforation skin factor
    s_d_0   == open-hole equivalent skin effect from hawkins()
"""
        print("I need...\n" + helptext)
        self.s_d_0 = promptforfloat(self.s_d_0, "s_d_0")
        self.k = promptforfloat(self.k, "k")
        self.k_s = promptforfloat(self.k_s, "k_s")
        self.s_p = promptforfloat(self.s_p, "s_p")
        if self.s_d_0==None:
            self.r_s = promptforfloat(self.r_s, "r_s")
            self.r_w = promptforfloat(self.r_w, "r_w")
        
    def speak(self):
        print("Skin effect is %s" % (str(self.s_p_d)))


def perforationskineffect(s_h=0, s_v=0, s_wb=0):
    """
    Calculate perforation skin effect or s_p given...
    s_h     == horizontal skin effect
    s_v     == vertical pseudoskin
    s_wb    == well bore blockage effect
    """
    s_p = s_h + s_v + s_wb
    return(s_p)


def skin_horizontal(r_w=0, r_w_primed=0):
    """
    Calculate s_h given...
    r_w         == well radius
    r_w_primed  == effective well bore radius
    """
    s_h = np.log(r_w / r_w_primed)
    return(s_h)


def skin_vertical(phasing=0, k_h=0, k_v=0, r_perf=0, h_perf=0, l_perf=0):
    """
    phasing == bore inclination in degrees
    r_perf  == 
    k_h     == horizontal permeability
    k_v     == vertical permeability
    l_perf  == length of perforation
    h_perf  == width of perforation
    """
    # Table values
    print("phasing %s, k_h %s, k_v %s, r_perf %s, h_perf %s, l_perf %s" % (phasing, k_h, k_v, r_perf, h_perf, l_perf))
    a_1 = kt_table[phasing][1]
    a_2 = kt_table[phasing][2]
    b_1 = kt_table[phasing][3]
    b_2 = kt_table[phasing][4]
    h_d = (h_perf / l_perf) * ((k_h / k_v)**0.5)
    r_d = (r_perf / (2 * h_perf)) * (1+ ((k_v/k_h)**0.5))
    a = a_1 * np.log(r_d) + a_2
    b = b_1 * r_d + b_2
    s_v = 10**a * h_d**(b-1) * r_d**b
    return(s_v)


def skin_blockage(phasing=0, l_perf=0, r_w=0):
    """
    Well bore blockage efect or s_wb given...
    phasing     == bore inclination in degrees
    l_perf      == length of perforation
    r_w         == well radius
    """
    # Table values
    c_1 = kt_table[phasing][5]
    c_2 = kt_table[phasing][6]
    r_wd = r_w / (l_perf + r_w)
    s_wb = c_1 * (np.e**(c_2 * r_wd))
    return(s_wb)


def skineffect(k=0, k_s=0, r_s=0, r_w=0, s_p=0):
    """
    Calculate skin effect without a given s_d_0.
    """
    s_p_d = (k / k_s - 1) * (np.log(r_s / r_w) + s_p)
    return(s_p_d)


def effective_well_bore_radius(phasing=0, r_w=0, l_perf=0):
    """
    Select the effective well bore radius from Karaks and Tariq's skin
    effect table of constants at fixed phasing.  This is r_w_primed.
    a_theta == kt_table[phasing[0]]
    phasing == degrees of inclination
    r_w     == well radius
    l_perf  == length of perforation
    """
    r_w_primed = kt_table[phasing][0]
    return(r_w_primed)


def promptforfloat(default=None, outstring="Value"):
    """
    Prompt for float values, returning NoneType for bogus results.
    Default value on <ENTER> key is any previously set value.
    """
    try:
        retval = float(input("Enter %s [%s]:  " % \
            (str(outstring), str(default))))
    except:
        retval = default
    return(retval)


def hawkins(k=None, k_s=None, r_s=None, r_w=None):
    """
    Hawkins formula with extraneous parentheses for readability...
    """
    s = ((k / k_s) - 1) * (np.log(r_s / r_w))
    return(s)


def main():
    k = karakastariq(r_w=0.328, h_perf=0.25, r_perf=0.25, l_perf=8, phasing=180, k_h=10, k_v=1)


if __name__=="__main__":
    main()
