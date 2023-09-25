# Define a structure to compute polynomials in several variables. A polynomial with n variables
# is a map that sends a vector (a_1,....,a_n) to a rational coefficients.

from __future__ import annotations
from fractions import Fraction

from helpers import *
from polynomial import *

import os

memZ = {}


def CycleIndexSym(n) -> Polynomial:
    """
    Computes the cycle index polynomial of the symmetric group on n letters.
    """
    if n == 0:
        memZ[n] = constant_polynomial(n, Fraction(1, 1))
        return memZ[n]
    if n == 1:
        memZ[n] = x(1)
        return memZ[n]
    if n in memZ:
        return memZ[n]
    else:
        out = zero_polynomial(n)
        for i in range(1, n + 1):
            out += CycleIndexSym(n - i) * x(i)

    return Fraction(1, n) * out


def solution(w, h, s):
    """
    Computes the number of matrices of size w x h with entries in [0,s) up to column and row permutation.
    """
    poly1 = CycleIndexSym(w)
    poly2 = CycleIndexSym(h)

    return str(poly1.direct_product(poly2).eval_all(s))


def main():
    s = (CycleIndexSym(5).direct_product(CycleIndexSym(6))).__str__()

    out = (
        """
\\documentclass{article}
\\usepackage{mathtools}
\\begin{document}

$$
\\begin{matrix*}[l]
    """
        + s
        + """
\\end{matrix*}    
$$
\\end{document}
"""
    )

    path = ""
    with open("funcs.tex", "w") as filein:
        filein.write(out)
        filein.close()
        path = filein.name

    print("compiling .pdf")
    os.system("pdflatex -quiet funcs.tex")
    print("done")
    print(f'.tex saved as "{path}"')
    print(".pdf successfully generated")

    # clean files after compiling
    os.system("rm -r funcs.aux")
    os.system("rm -r funcs.log")


if __name__ == "__main__":
    main()
