from __future__ import annotations

from helpers import *


class Polynomial:
    def __init__(self, num_vars: int, monomials: dict[tuple[int, ...], Fraction]):
        for key in monomials.keys():
            assert len(key) == num_vars, ValueError(
                f"Monomial with {len(key)} variables in polynomial with {num_vars}."
            )
        self.num_vars = num_vars
        self.monomials = monomials

    def copy(self) -> Polynomial:
        copy_monomials = self.monomials.copy()
        return Polynomial(self.num_vars, copy_monomials)

    def __add__(self, other: Polynomial) -> Polynomial:
        c_self = self.copy()
        c_other = other.copy()

        # pad polynomials in case of variable mismatch
        if self.num_vars > other.num_vars:
            c_other = c_other._add_variables(self.num_vars)
        if self.num_vars < other.num_vars:
            c_self = c_self._add_variables(other.num_vars)

        # then perform usual addition
        for exponent in c_self.monomials:
            if exponent in c_other.monomials:
                c_other.monomials[exponent] += c_self.monomials[exponent]
            else:
                c_other.monomials[exponent] = c_self.monomials[exponent]
        return c_other

    def __sub__(self, other: Polynomial) -> Polynomial:
        return (self + (-other))._clean_zeroes()

    def __neg__(self) -> Polynomial:
        return Fraction(-1, 1) * self

    def __mul__(self, other: Polynomial) -> Polynomial:
        new_monomials = {}
        for e in self.monomials:
            for f in other.monomials:
                g = sum_exponents(list(e), list(f))
                if g in new_monomials:
                    new_monomials[g] += self.monomials[e] * other.monomials[f]
                else:
                    new_monomials[g] = self.monomials[e] * other.monomials[f]

        new_num_vars = max(self.num_vars, other.num_vars)
        return Polynomial(new_num_vars, new_monomials)

    def __pow__(self, n: int) -> Polynomial:
        if n == 0:
            return constant_polynomial(self.num_vars, Fraction(1, 1))
        if n == 1:
            return self

        if n % 2 == 0:
            return self.__pow__(n // 2) * self.__pow__(n // 2)
        else:
            return self * self.__pow__(n // 2) * self.__pow__(n // 2)

    def __rmul__(self, other: Fraction | int) -> Polynomial:
        """
        Implements left multiplication of a polynomial by a rational coefficient.
        """
        if type(other) == int:
            return Fraction(other, 1) * self

        if other == Fraction(0, 1):
            return zero_polynomial(self.num_vars)

        new_monomials = {}
        for e in self.monomials:
            new_monomials[e] = self.monomials[e] * other
        return Polynomial(self.num_vars, new_monomials)

    def __str__(self) -> str:
        """
        Prints a polynomial into a LaTeX format.
        """

        if not self.monomials:
            return "0"

        count = 0
        out = []
        memo = []
        for exponents in self.monomials:
            coefficient = self.monomials[exponents]
            memo.append(latex_print_monomial(exponents, coefficient))
            count += 1

            if count == 3:
                out.append("&+&".join(memo))
                count = 0
                memo = []

        return "\\\\\n".join(out)

    def _clean_zeroes(self) -> Polynomial:
        new_monomials = {}
        for exponents in self.monomials:
            if self.monomials[exponents] != Fraction(0, 1):
                new_monomials[exponents] = self.monomials[exponents]
        self.monomials = new_monomials
        return self

    def _add_variables(self, new_vars: int) -> Polynomial:
        """
        Increases the number of variables of a polynomial.
        """
        assert new_vars >= self.num_vars, ValueError(
            f"Cannot turn polynomial in {self.num_vars} to a polynomial in {new_vars} variables."
        )

        if new_vars == self.num_vars:
            return self

        new_monomials: dict[tuple, Fraction] = {}

        for e in self.monomials:
            pad_e = tuple(list(e) + [0 for _ in range(new_vars - self.num_vars)])
            new_monomials[pad_e] = self.monomials[e]

        return Polynomial(new_vars, new_monomials)

    def eval_all(self, value: Fraction | int) -> Fraction:
        if type(value) == int:
            return self.eval_all(Fraction(value, 1))

        if type(value) == Fraction:
            values = [value for _ in range(self.num_vars)]
            return self.eval(values)

        raise NotImplemented

    def eval(self, values: list[Fraction]) -> Fraction:
        assert len(values) == self.num_vars, ValueError(
            f"Length mismatch: {self.num_vars} variables but got tuple with {len(values)} scalars."
        )

        out = Fraction(0, 1)

        for exponent in self.monomials:
            monomial_eval = Fraction(1, 1)
            coefficient = self.monomials[exponent]
            for i, e in enumerate(exponent):
                monomial_eval *= values[i] ** e
            out += coefficient * monomial_eval

        return out

    def direct_product(self, other: Polynomial) -> Polynomial:
        """
        Computes the direct product of two polynomials, following
        the Definition 2.2 of https://doi.org/10.1016/0012-365X(93)90015-L.
        """

        new_monomials = {}
        c_self = self.copy()
        c_other = other.copy()

        # pad polynomials in case of variable mismatch
        if self.num_vars > other.num_vars:
            c_other = c_other._add_variables(self.num_vars)
        if self.num_vars < other.num_vars:
            c_self = c_self._add_variables(other.num_vars)

        for e in c_self.monomials:
            for f in c_other.monomials:
                g = tuple(compute_new_exponent(list(e), list(f)))
                if g in new_monomials:
                    new_monomials[g] += c_self.monomials[e] * c_other.monomials[f]
                else:
                    new_monomials[g] = c_self.monomials[e] * c_other.monomials[f]

        return Polynomial(c_self.num_vars**2, new_monomials)


def x(i: int) -> Polynomial:
    """
    Returns the polynomial x_i. Defaults to i variables.
    """
    new_monomials = {}

    monomial = tuple([int(i == j) for j in range(1, i + 1)])
    new_monomials[monomial] = Fraction(1, 1)

    return Polynomial(i, new_monomials)


def compute_new_exponent(e: list[int], f: list[int]) -> list[int]:
    assert len(e) == len(f), ValueError(f"length mismatch: {len(e)} with {len(f)}")

    g = [0 for _ in range(len(e) ** 2)]
    for i, a in enumerate(e):
        for j, b in enumerate(f):
            exp = a * b * gcd(i + 1, j + 1)
            var_index = (i + 1) * (j + 1) // gcd(i + 1, j + 1)
            g[var_index - 1] += exp
    return g


def gcd(i: int, j: int) -> int:
    while i > 0:
        i, j = j % i, i
    return j


def constant_polynomial(num_vars: int, coefficient: Fraction) -> Polynomial:
    """
    Return a constant polynomial with num_vars variables and with the given coefficient.
    """
    if coefficient == 0:
        return zero_polynomial(num_vars)
    return Polynomial(num_vars, {tuple([0 for _ in range(num_vars)]): coefficient})


def zero_polynomial(num_vars: int) -> Polynomial:
    """
    Returns the zero polynomial in num_var variables.
    """
    return Polynomial(num_vars, {})
