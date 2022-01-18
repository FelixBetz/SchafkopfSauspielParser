"""This module parses chat log from www.sauspiel.de and generates some statistics"""
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


class Player:
    """contains player information"""

    def __init__(self, name):
        self.name = name
        self.points_history = []

    def get_name(self):
        """returns player name"""
        return self.name

    def get_points(self):
        """returns player points"""
        if len(self.points_history) > 0:
            return self.points_history[-1][1]
        return 0

    def add_game_points(self, arg_points):
        """adds game to player points"""
        if len(self.points_history) > 0:
            last_point_value = self.points_history[-1][1]
            arg_points = (arg_points[0], last_point_value + arg_points[1])
        self.points_history.append(arg_points)

    def get_points_history(self):
        """returns game history of the player"""
        return self.points_history


class Game:
    """contains game information"""

    def __init__(self, arg_id, arg_num, arg_players):
        self.identifier = arg_id
        self.num = arg_num
        self.data = []
        self.calling_players = []

        for loc_player in arg_players:
            self.data.append((loc_player, 0))

        self.game_type = "weiter"

    def get_num(self):
        """returns game number"""
        return self.num

    def get_id(self):
        """returns game id"""
        return self.identifier

    def set_data(self, arg_data, arg_game_type, arg_calling_players):
        """sets game data"""
        self.data = arg_data
        self.game_type = arg_game_type
        self.calling_players = arg_calling_players

    def get_data(self):
        """returns game data"""
        return self.data

    def get_game_type(self):
        """returns game type"""
        return self.game_type

    def get_calling_players(self):
        """returns calling players"""
        return self.calling_players


###########################################################################
# add player to list
def add_player_to_list(arg_players_list, arg_player_name):
    """add a player to the given player list"""
    player_exists = False
    for loc_player in arg_players_list:
        if loc_player.get_name() == arg_player_name:
            player_exists = True
            break

    if not player_exists:
        arg_players_list.append(Player(arg_player_name))
        debug("\tnew player " + arg_player_name)
    return arg_players_list


###########################################################################
# debug print
DEBUG_PRINT_ACTIVE = False


def debug(text):
    """prints debug messages, if activated"""
    if DEBUG_PRINT_ACTIVE:
        print(text)


###########################################################################
# read input file
INPUT_FILE_PATH = "2021_12_09_log.txt"
input_file_lines = []
with open(INPUT_FILE_PATH, encoding="utf-8") as fp:
    for cnt, line in enumerate(fp):
        input_file_lines.append(line)

###########################################################################
# parse games
games = []
players = []

MY_NAME = "KiliW"
my_name_replace_strings = ["Du", "Dir"]

entry_strings = ["an den Stammtisch gesetzt.", "die Wirtschaft betreten"]
exit_strings = [
    "hat den Stammtisch verlassen",
]

points_strings = ["gewonnen", "verloren"]

currentPlayers = []

for i, line in enumerate(input_file_lines):

    # remove new line at the end of the line
    line = line.replace("\n", "")

    # replace my_name_replace_strings with my_name
    for my_name_replace_string in my_name_replace_strings:
        line = line.replace(my_name_replace_string, MY_NAME)
    debug("\n" + str(i) + "#: " + line)

    # check entry player
    if any(entry_string in line for entry_string in entry_strings):
        player_name = line.split(" ")[0]
        players = add_player_to_list(players, player_name)
        if player_name not in currentPlayers:
            currentPlayers.append(player_name)
            debug("\tadd player " + player_name)

    # exit entry player
    elif any(exit_string in line for exit_string in exit_strings):
        player_name = line.split(" ")[0]
        currentPlayers.remove(player_name)
        debug("\tremove player " + player_name)

    # check for new game
    elif line.startswith("Spiel"):
        gameId = line.split(" ")[1]
        games.append(Game(gameId, len(games) + 1, currentPlayers))
        debug("\tnew game")

    # parse Points
    elif any(points_string in line for points_string in points_strings):

        line_split = line.split(" ")
        points = int(line_split[-3])

        data = []

        # 2 players game
        twoPlayersStrings = [" hat mit ", " hast mit "]
        if any(twoPlayersString in line for twoPlayersString in twoPlayersStrings):
            calling_players = [line_split[0], line_split[3]]
            if line_split[6] == "verloren.":
                points *= -1
            game_type = line_split[5]

            for player in currentPlayers:
                if player in calling_players:
                    data.append((player, points))
                else:
                    data.append((player, -1 * points))

        # 1 player game
        else:

            calling_players = [line_split[0]]
            parsed_points = int(line_split[-3])

            if line_split[-1] == "verloren.":
                parsed_points *= -1

            game_type = line_split[3]

            if calling_players[0] == MY_NAME:
                calling_player_points = parsed_points
                othersPoints = parsed_points / -3
            else:
                calling_player_points = parsed_points * -3
                othersPoints = parsed_points

            for player in currentPlayers:
                if player in calling_players:
                    data.append((player, calling_player_points))
                else:
                    data.append((player, othersPoints))

        # add game Data
        games[-1].set_data(data, game_type, calling_players)

        debug(
            "\t"
            + games[-1].get_id()
            + ", "
            + str(games[-1].get_num())
            + ", "
            + games[-1].get_game_type()
            + ", "
            + str(games[-1].get_data())
        )

    # unparsed lines
    else:
        pass
        # print("not parsed line: \r\n",line)

###########################################################################
# accumulate points for each player
for g in games:
    data = g.get_data()
    for d in data:
        for p in players:
            if p.get_name() == d[0]:
                p.add_game_points((g.get_num(), d[1]))

fontP = FontProperties()
fontP.set_size(20)

MY_DPI = 96
WIDTH = 1900
HEIGHT = 540

plt.figure(figsize=(WIDTH / MY_DPI, HEIGHT / MY_DPI))
plt.grid(linestyle="-", linewidth=0.5)
plt.xlabel("games", fontsize=20)
plt.ylabel("points", fontsize=20)

# plot players
for p in players:
    labelString = p.get_name() + ", "
    if p.get_points() > 0:
        labelString += "+"
    labelString += str(p.get_points())

    plt.plot(
        *zip(*p.get_points_history()),
        label=labelString,
        linewidth=3.5,
        markersize=8,
        marker="o"
    )

legend = plt.legend(
    loc="upper center",
    ncol=4,
    bbox_to_anchor=(0.5, -0.15),
    prop=fontP,
    fancybox=True,
    shadow=True,
    title="total players: " + str(len(players)),
)
plt.setp(legend.get_title(), fontsize=30)
plt.show()

# plot gameType distribution
game_types = []
for g in games:
    game_types.append(g.get_game_type())

game_types_dict = dict(Counter(game_types))
game_types_values = list(game_types_dict.values())
game_types_labels = list(game_types_dict.keys())

for i, l in enumerate(game_types_labels):
    game_types_labels[i] += ": " + str(game_types_values[i])

WIDTH -= 700
fig1, (ax1, ax2) = plt.subplots(
    nrows=1, ncols=2, figsize=(WIDTH / MY_DPI, HEIGHT / MY_DPI)
)


cmap = plt.get_cmap(
    "tab20"
)  # https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
colors = cmap(list(range(0, 2 * len(game_types_values), 2)))

ax1.pie(
    game_types_values,
    labels=game_types_labels,
    radius=1,
    autopct="%0.1f%%",
    colors=colors,
)
ax1.legend(
    title="total games: " + str(sum(game_types_values)),
    loc="upper left",
    ncol=3,
    shadow=True,
    bbox_to_anchor=(0, 0),
)

solo_games = []
for g in games:
    calling_players = g.get_calling_players()
    if len(calling_players) == 1 and g.get_game_type() != "Ramsch":
        solo_games.append((calling_players[0], g.get_game_type()))


player_solo_games = list(dict(solo_games).keys())


inner_vals = []
outer_vals = []
inner_labels = []
outer_colors = []
inner_colors = []

for p in player_solo_games:
    tmp = []
    for s in solo_games:
        if p == s[0]:
            tmp.append(s[1])
    player_dict = dict(Counter(tmp))

    tmp_vals = list(player_dict.values())
    tmp_lables = list(player_dict.keys())
    for i, l in enumerate(tmp_lables):
        tmp_lables[i] += ": " + str(tmp_vals[i])

    inner_labels += tmp_lables
    inner_vals += tmp_vals
    outer_vals.append(sum(tmp_vals))

    OUTER_COLOR_INDEX = (len(outer_vals) - 1) * 4
    for i, tmpVal in enumerate(tmp_vals):
        inner_colors.append(1 + i + OUTER_COLOR_INDEX)

outer_labels = player_solo_games
for i, l in enumerate(outer_labels):
    outer_labels[i] += ": " + str(outer_vals[i])
    outer_colors.append(i * 4)

cmap = plt.get_cmap(
    "tab20c"
)  # https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
outer_colors = cmap(outer_colors)
inner_colors = cmap(inner_colors)

ax2.pie(
    outer_vals,
    radius=1,
    labels=outer_labels,
    colors=outer_colors,
    autopct="%0.1f%%",
    wedgeprops=dict(width=0.25, edgecolor="w"),
    labeldistance=1.1,
    pctdistance=0.88,
)

ax2.legend(
    title="total solo games: " + str(len(solo_games)),
    loc="upper left",
    ncol=2,
    bbox_to_anchor=(0, 0),
    shadow=True,
)
ax2.pie(
    inner_vals,
    radius=0.75,
    colors=inner_colors,
    labels=inner_labels,
    wedgeprops=dict(width=0.7, edgecolor="w"),
    labeldistance=0.5,
    pctdistance=2,
)


# ax.set(aspect="equal", title='Pie plot with `ax.pie`')
plt.show()


# 3850 4220  970
