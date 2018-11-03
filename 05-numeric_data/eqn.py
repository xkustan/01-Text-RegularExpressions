import numpy
import sys
from copy import deepcopy


def parse_equation(equation, variables):
    var_to_coef = deepcopy(variables)

    matrix_part, solution_part = equation.split("=")
    matrix_part = matrix_part.strip()
    solution_part = solution_part.strip()

    matrix_list = []

    sign = ""
    for x in matrix_part.split():
        if x in {"+", "-"}:
            sign = x
        else:
            matrix_list.append("{0}{1}".format("-" if sign == "-" else "", x))

    for coefficient in matrix_list:
        var = ""
        const = ""
        for x in coefficient:
            if x.isalpha():
                var = x
            else:
                const += x

        if const == "":
            const = 1
        if const == "-":
            const = -1

        var_to_coef[var] = int(const)

    return sorted(var_to_coef.items()), int(solution_part)


def parse_equations(file_path, variables):

    A = []  # matrix
    x = []  # vars
    B = []  # constants, solution

    with open(file_path, "r") as file:

        for equation in file:
            if not equation.strip():
                continue

            equation_dict, result_constant = parse_equation(equation, variables)

            row = []
            tmp_x = []
            for (var, coef) in equation_dict:
                tmp_x.append(var)
                row.append(coef)

            x = tmp_x if not x else x
            if x != tmp_x:
                raise Exception("problem with variables order!")

            B.append(result_constant)
            A.append(row)

        file.close()

    return A, x, B


def solve_equations(a, x, b):
    matrix = numpy.array(a)
    solution_vector = numpy.array(b)

    for i, row in enumerate(a):
        row.append(b[i])

    augmented_matrix = numpy.array(a)
    n = len(x)

    solutions, dimension = rouche_capelli(matrix, augmented_matrix, n)

    if solutions == 0:
        return "no solution"

    elif solutions == 1:
        res = numpy.linalg.solve(matrix, solution_vector)
        output = dict(zip(x, res))

        outs = []
        for v, r in output.items():
            outs.append("{0} = {1}".format(v, r))

        return "solution: " + ", ".join(outs)

    else:
        return "solution space dimension: {0}".format(dimension)


def rouche_capelli(m, am, n):

    coefficient_matrix_rank = numpy.linalg.matrix_rank(m)
    augmented_matrix_rank = numpy.linalg.matrix_rank(am)

    if coefficient_matrix_rank == augmented_matrix_rank:
        if n == coefficient_matrix_rank:
            return 1, None
        else:
            return None, n - coefficient_matrix_rank
    else:
        return 0, None  # no solution


def get_all_variables(file_path):

    variables = set()

    with open(file_path, "r") as file:
        for equation in file:
            if not equation.strip():
                continue

            for x in equation:
                if x.isalpha():
                    variables.add(x)
        file.close()

    return {x: 0 for x in variables}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("Argument has to be path to file with linear equations!")

    filename = sys.argv[1]
    all_variables = get_all_variables(filename)
    matrix, variables, solution = parse_equations(filename, all_variables)
    result = solve_equations(matrix, variables, solution)
    print(result)
