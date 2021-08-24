import argparse
import curses

from .objects.blacklistaction import BlacklistAction
from .objects.bonemarketargumentparser import BoneMarketArgumentParser
from .objects.enumaction import EnumAction
from .objects.listaction import ListAction
from .solve import *
from .read_char import *


parser = BoneMarketArgumentParser(
        prog='Bone Market Solver',
        description="Devise the optimal skeleton at the Bone Market in Fallen London.",
        fromfile_prefix_chars="@",
        argument_default=argparse.SUPPRESS,
        )

parser.add_argument(
        "-l", "--list",
        action=ListAction,
        default=ListAction.list_options,
        choices=ListAction.list_options,
        nargs=argparse.ZERO_OR_MORE,
        help="list specified enumerations and their names and exit",
        dest=argparse.SUPPRESS
        )


world_qualities = parser.add_argument_group(
        "world qualities",
        "Parameters shared across Fallen London, often changing on a routine basis"
        )

world_qualities.add_argument(
        "-f", "--bone-market-fluctuations",
        action=EnumAction,
        type=Fluctuation,
        help="current value of Bone Market Fluctuations, which grants various bonuses to certain buyers",
        dest='bone_market_fluctuations'
        )

world_qualities.add_argument(
        "-m", "--zoological-mania",
        action=EnumAction,
        type=Declaration,
        help="current value of Zoological Mania, which grants a percentage bonus to value for a certain declaration",
        dest='zoological_mania'
        )

world_qualities.add_argument(
        "-o", "--occasional-buyer",
        action=EnumAction,
        type=OccasionalBuyer,
        help="current value of Occasional Buyer, which allows access to a buyer that is not otherwise available",
        dest='occasional_buyer'
        )

world_qualities.add_argument(
        "-d", "--diplomat-fascination",
        action=EnumAction,
        type=DiplomatFascination,
        help="current value of The Diplomat's Current Fascination, which determines what the Trifling Diplomat is interested in",
        dest='diplomat_fascination'
        )


skeleton_parameters = parser.add_argument_group(
        "skeleton parameters",
        "Parameters that determine what you want the solver to produce"
        )

skeleton_parameters.add_argument(
        "-s", "--shadowy",
        type=int,
        default=Char.SHADOWY.value,
        help="the effective level of Shadowy used for selling to buyers",
        dest='shadowy_level'
        )

skeleton_parameters.add_argument(
        "-b", "--buyer", "--desired-buyer",
        action=EnumAction,
        nargs=argparse.ONE_OR_MORE,
        type=Buyer,
        help="specific buyer that skeleton should be designed for (if multiple are specified, will choose from among them)",
        dest='desired_buyers'
        )

skeleton_parameters.add_argument(
        "-c", "--cost", "--maximum-cost",
        type=int,
        help="maximum number of pennies that should be invested in skeleton",
        dest='maximum_cost'
        )

skeleton_parameters.add_argument(
        "-e", "--exhaustion", "--maximum-exhaustion",
        type=int,
        help="maximum exhaustion that skeleton should generate",
        dest='maximum_exhaustion'
        )

skeleton_parameters.add_argument(
        "--blacklist",
        action=BlacklistAction,
        nargs=argparse.ONE_OR_MORE,
        help="components, options, or buyers that should not be used by the solver",
        metavar="Enum.MEMBER",
        dest='blacklist'
        )


solver_options = parser.add_argument_group(
        "solver options",
        "Options that affect how the solver behaves"
        )

solver_options.add_argument(
        "-v", "--verbose",
        action=argparse.BooleanOptionalAction,
        help="whether the solver should output search progress rather than showing intermediate solutions",
        dest='verbose'
        )

solver_options.add_argument(
        "-t", "--time-limit",
        type=float,
        help="maximum number of seconds that the solver runs for",
        dest='time_limit'
        )

solver_options.add_argument(
        "-w", "--workers",
        type=int,
        help="number of search worker threads to run in parallel (default: one worker per available CPU thread)",
        dest='workers'
        )


args = parser.parse_args()

arguments = vars(args)

if not arguments.pop('verbose', False):
    def WrappedSolve(stdscr, arguments):
        # Prevents crash if window is too small to fit text
        stdscr.scrollok(True)
        # Move stdscr to last position
        arguments['stdscr'] = stdscr
        return Solve(**arguments)
    print(curses.wrapper(WrappedSolve, arguments))
else:
    print(Solve(**arguments))
