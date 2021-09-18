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
pipenv run bone_market_solver --help
```

These options allow you to specify world qualities, skeleton parameters, and solver options.  
These options do not need to be provided in any particular order, and generally have shorthand versions for ease of typing.

Here's an example, broken into multiple lines for ease of reading:
```sh
pipenv run bone_market_solver \
--bone-market-fluctuations menace \
--occasional-buyer an_enterprising_boot_salesman \
--zoological-mania insect \
--diplomat-fascination antiquity \
--shadowy 302 \
--maximum-exhaustion 4 \
--time-limit 300 \
--blacklist Skull.VICTIM_SKULL Torso.VICTIM_TORSO
```

For best results, it is recommended to specify every world quality you can. Depending on the speed of your computer, setting a time limit may also be helpful.

You do *not* need to specify buyers to use this solver. The solver will try to maximize profit margin for all available buyers if you do not specify any, which may be very useful if you have no particular objective in mind. Specifying multiple buyers will cause the solver to choose from among them.

### Blacklisting

If you wish to prohibit certain options, you may do so by passing their exact identifiers (e.g. "Skull.VICTIM\_SKULL") to the blacklist.

You may wish to blacklist options that:
* require a Profession, Ambition, or story you do not have
* add Exhaustion
* you simply don't have a good source for

To get a list of identifiers, use:
```sh
pipenv run bone_market_solver --list
```
Specific enumerations may be provided to narrow what is shown.

### Configuration Files

Rather than typing out every argument each time you use the solver, you may provide a file path (prefixed with "@") to the CLI.

This file should contain command-line arguments. The solver will interpret these arguments as if they were typed in place of the file path.

Configuration files are read top-to-bottom. Arguments can be delimited by a single space, broken onto different lines, or any combination thereof.

Any number of configuration files may be provided simultaneously.

## Versioning

This tool follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html). The public API consists of the command-line interface, as well as all public Python declarations.

As Fallen London is a living game, the solver may not reflect its present state. With that in mind, version tags include the last known date of relevant changes to Fallen London that are reflected by the tool. Any changes to Fallen London since that date, even if they were made before the tag or commit, should be presumed unimplemented.

While all commits in the main branch are functional, unversioned commits should not be considered *accurate*. They may, for instance, partially incorporate an update to Fallen London, which results in a solver that does reflect the game at any single point in time. Pre-release versions should be considered on case-by-case basis: a pre-release may accurately reflect only a subset of the Bone Market, constraining the solver to avoid options that are no longer correctly evaluated.

## Caveats

The solver aims to maximize profit margin, rather than sheer profit. This is because it may be more profitable to make many smaller skeletons than one massive skeleton.

With the exception of the check for actually selling to buyers, the solver assumes that every challenge will be passed. Among other things, this means that implausibility may be higher in practice than the solver anticipates.

Rather than modelling the entirety of Fallen London, the solver uses a sort of context-free grammar to express the cost of every option. This has some major shortcomings: side-effects are not modelled, for instance, so designs that take such things into account could outperform the solver.

If something seems off, such as the solver favoring an option you consider overly expensive or wasteful, check the costs in the script: if you disagree with them (particularly the costs with a terminal value, which are often fairly arbitrary), feel free to change them yourself. If you do so, please consider submitting a pull request so others may benefit from your improvements. Just make sure that the rationale is fairly obvious to others reading the script.

## Alternative

The Bone Market, Fallen London, and any StoryNexus world may be modelled _exactly_ as a [constrained](https://en.wikipedia.org/wiki/Markov_decision_process#Continuous-time_Markov_decision_process) [partially observable Markov decision process](https://en.wikipedia.org/wiki/Partially_observable_Markov_decision_process). If you truly want a perfect solver without any trade-offs, caveats, or limitations, consider looking into that.
