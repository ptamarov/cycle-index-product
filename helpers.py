from fractions import Fraction


def _frac_to_latex(r: Fraction) -> str:
    if r.denominator == 1:
        return f"{r.numerator}"
    return "\\frac{" + f"{r.numerator}" + "}{" + f"{r.denominator}" + "}"


def latex_print_monomial(exponents: tuple[int, ...], coefficient: Fraction) -> str:
    if all([e == 0 for e in exponents]):
        return _frac_to_latex(coefficient)
    return (
        _frac_to_latex(coefficient)
        + "&"
        + " ".join(
            [pow(i, exponent) for i, exponent in enumerate(exponents) if exponent != 0]
        )
    )


def pow(i, exponent) -> str:
    return (
        "x_{" + f"{i+1}" + "}" + "^{" + f"{exponent}" + "}"
        if exponent != 1
        else "x_{" + f"{i+1}" + "}"
    )


def get(xs: list[int], i: int) -> int:
    if i < len(xs):
        return xs[i]
    else:
        return 0


def zip_with_zeroes(xs: list[int], ys: list[int]) -> list[tuple[int, int]]:
    """
    Zip xs and ys but add trailing zeroes if there is a length mismatch.
    """

    # nothing to do if both empty
    if len(xs) == 0 and len(ys) == 0:
        return []

    # assume that xs is the longest
    if len(xs) < len(ys):
        xs, ys = ys, xs

    new = []

    for i in range(len(xs)):
        new.append((get(xs, i), get(ys, i)))

    return new


def sum_exponents(xs: list[int], ys: list[int]) -> tuple[int, ...]:
    return tuple(map(sum, zip_with_zeroes(xs, ys)))
