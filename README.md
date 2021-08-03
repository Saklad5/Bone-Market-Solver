# Bone Market Solver

This script uses constraint programming to devise the optimal skeleton at the Bone Market in Fallen London.

Whether you are bewildered by the intricacy of the Bone Market or simply looking to take advantage of current world qualities, the Bone Market Solver can help you squeeze every last penny out of your fossils.

## Prerequisites

* [pipenv](https://github.com/pypa/pipenv)

## Installation

1. Navigate to the directory that contains the script.
2. Run the following command:
```sh
pipenv install
```
This will automatically create a virtual environment with the correct version of Python and all necessary dependencies.

pipenv is not strictly necessary for this script, though it is highly recommended. Managing Python versions and packages yourself, especially on a system-wide level, can cause a lot of headache in the future.

## Usage

Having navigated to the directory that contains the script, you can see the options of the script using the following command:
```sh
pipenv run python Bone\ Market\ Solver.py --help
```

These options allow you to specify world qualities, skeleton parameters, and solver options.  
These options do not need to be provided in any particular order, and generally have shorthand versions for ease of typing.

Here's an example, broken into multiple lines for ease of reading:
```sh
pipenv run python Bone\ Market\ Solver.py \
--bone-market-fluctuations menace \
--occasional-buyer an_enterprising_boot_salesman \
--zoological_mania insect \
--diplomat_fascination antiquity \
--shadowy 302 \
--maximum_exhaustion 4 \
--time-limit 300
```

For best results, it is recommended to specify every world quality you can. Depending on the speed of your computer, setting a time limit may also be helpful.

You do *not* need to specify buyers to use this solver. The solver will try to maximize profit margin for all available buyers if you do not specify any, which may be very useful if you have no particular objective in mind. Specifying multiple buyers will cause the solver to choose from among them.

## Caveats

The solver aims to maximize profit margin, rather than sheer profit. This is because it may be more profitable to make many smaller skeletons than one massive skeleton.

With the exception of the check for actually selling to buyers, the solver assumes that every challenge will be passed. Among other things, this means that implausibility may be higher in practice than the solver anticipates.

Rather than modelling the entirety of Fallen London, the solver uses a sort of context-free grammar to express the cost of every option. This has some major shortcomings: side-effects are not modelled, for instance, so designs that take such things into account could outperform the solver.

If something seems off, such as the solver favoring an option you consider overly expensive or wasteful, check the costs in the script: if you disagree with them (particularly the costs with a terminal value, which are often fairly arbitrary), feel free to change them yourself. If you do so, please consider submitting a pull request so others may benefit from your improvements. Just make sure that the rationale is fairly obvious to others reading the script.