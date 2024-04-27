import os
import random
import time

import dash
import dash_cytoscape as cyto
import git
from git import Commit
import matplotlib.colors as mcolors
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from perun.select.better_repository_selection import BetterRepositorySelection
from perun.vcs.git_repository import GitRepository

app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True
)
repo_path = os.getcwd()
repo = git.Repo(repo_path)
repo_commits = list(repo.iter_commits())
branches_checkbox, author_checkbox = [], []
selected_nodes = []
selected_options_state = []
selected_authors_state = []
LOADED_COMMITS = {}
branch_colors = {}
selection = BetterRepositorySelection(repo_path)
max_confidence = 0

branches_trans = {}
branches_commits = {}


def build_branch_name(branch_name: str, commit: Commit) -> str:
    if branch_name == "master~1" or branch_name == "master~383":
        print("")

    if any(x in commit.message for x in ["Merge pull request", "Merge branch"]):
        if "Merge pull request" in commit.message:
            branch_name_tmp = commit.message.split("\n")[0].rsplit(" ", 1)[1]
        elif "Merge branch" in commit.message:
            branch_name_tmp = commit.message.split("'", 2)[1]
        znak_count = branch_name.count("^")

        for parent_commit in commit.parents:
            if znak_count < repo.git.name_rev(parent_commit.hexsha, name_only=True).count("^"):
                branches_commits[parent_commit.hexsha] = f"{branch_name_tmp} (branch deleted)"

    if "tags" in branch_name:
        branch_name = branch_name.split("^", 1)[0].split("~", 1)[0]
    else:
        if branch_name.rfind("~", 1) > branch_name.rfind("^", 1):
            parts = branch_name.rsplit("~", 1)
            branch_name = parts[0]

    if commit.hexsha in branches_commits:
        branches_trans[branch_name] = branches_commits[commit.hexsha]

    if branch_name in branches_trans:
        branch_name = branches_trans[branch_name]

    return branch_name


def build_checkboxes(branch_name: str, commit: Commit, branch_color: str) -> None:
    if branch_name not in [item["value"] for item in branches_checkbox]:
        branches_checkbox.append(
            {
                "label": html.Div(
                    [
                        html.Span(branch_name, style={"max-width": "90%"}),
                        html.Span(
                            "●",
                            style={
                                "color": branch_color,
                                "margin-left": "4px",
                                "max-width": "10%",
                                "font-size": "x-large",
                                # "display": "inline",
                            },
                        ),
                    ],
                    style={"display": "inline-block", "margin-left": "4px"},
                ),
                "value": branch_name,
            }
        )

    if commit.author.email not in [item["value"] for item in author_checkbox]:
        author_checkbox.append(
            {
                "label": html.Div(
                    commit.author.email,
                    style={
                        "margin-left": "4px",
                        "display": "inline-block",
                    },
                ),
                "value": commit.author.email,
            }
        )


def generate_commit_tree(max_commits: int) -> dict:
    global max_confidence
    commits = {}
    i = 0
    for commit in repo_commits[: max_commits if max_commits > 0 else 99999999]:
        if (
            i == len(repo_commits[: max_commits if max_commits > 0 else 99999999])
            or i == len(repo_commits[: max_commits if max_commits > 0 else 99999999]) - 1
        ):
            print("")
        i += 1
        branch_name_full = repo.git.name_rev(commit.hexsha, name_only=True)
        branch_name = build_branch_name(branch_name_full, commit)

        try:
            ds, confidence, diff_result = selection.should_check_version(
                GitRepository(repo_path).get_minor_version_info(commit.hexsha)
            )
        except Exception as e:
            print(f"CHYBICKA: {e}")
            ds, confidence, diff_result = False, -1, None

        if confidence > max_confidence:
            max_confidence = confidence

        commits[commit.hexsha] = {
            "parents": [parent.hexsha for parent in commit.parents if parent.hexsha],
            "branch": branch_name,
            "author": commit.author.email,
            "branch_full": branch_name_full,
            "message": commit.summary,
            "should_check": ds,
            "confidence": confidence,
            "diff_result": diff_result,
        }
        if branch_name not in branch_colors:
            branch_colors[branch_name] = generate_hex_color()

        build_checkboxes(branch_name, commit, branch_colors[branch_name])

    return commits


@app.callback(
    Output("statistic-button", "style"),
    Input("commit-graph", "tapNodeData"),
    priority=1,
)
def show_hide_statistic_button(_) -> dict:
    global selected_nodes
    time.sleep(0.1)
    if len(selected_nodes) != 2:
        return {"display": "none"}
    else:
        return {"display": "block"}


@app.callback(
    Output("find-button", "style"),
    Input("commit-graph", "tapNodeData"),
    priority=1,
)
def show_hide_find_button(_) -> dict:
    global selected_nodes
    time.sleep(0.1)
    if len(selected_nodes) != 1:
        return {"display": "none"}
    else:
        return {"display": "block"}


@app.callback(
    Output("show/hide_confidence-button", "children"),
    Input("show/hide_confidence-button", "n_clicks"),
    priority=2,
)
def show_hide_confidence_button(n_clicks: int) -> str:
    if n_clicks % 2 == 0:
        return "Show confidence"
    else:
        return "Hide confidence"


@app.callback(
    Output("statistic-button", "children"), Input("statistic-button", "n_clicks"), priority=2
)
def show_hide_statistics_button(n_clicks: int) -> str:
    if n_clicks % 2 == 0:
        return "Show statistics"
    else:
        return "Hide statistics"


def generate_hex_color() -> str:
    return "#{:02x}{:02x}{:02x}".format(
        random.randint(60, 190), random.randint(60, 190), random.randint(60, 190)
    )


@app.callback(
    Output("commit-graph", "elements", allow_duplicate=True),
    [
        Input("num-commits-input", "value"),
        Input("branch_and_tags_checklist", "value"),
        Input("authors_checklist", "value"),
        Input("commit-graph", "tapNodeData"),
        Input("show/hide_confidence-button", "n_clicks"),
        Input("find-button", "n_clicks"),
    ],
    prevent_initial_call=True,
    priority=99,
)
def delete_graph(*_, **__):
    return []


@app.callback(
    [
        Output("placeholder-output", "children"),
    ],
    [Input("commit-graph", "tapNodeData")],
    priority=2,
)
def display_selected_commit(tapNodeData):
    if tapNodeData and (node_id := tapNodeData["id"]):
        if node_id in selected_nodes:
            selected_nodes.remove(node_id)
        else:
            if len(selected_nodes) < 2:
                selected_nodes.append(node_id)
    return ""


def commit_filtering(commits, selected_branches, selected_authors, num_commits):
    global max_confidence
    if selected_branches:
        commits = {
            key: value for key, value in commits if value["branch"] in selected_branches
        }.items()

    if selected_authors:
        commits = {
            key: value for key, value in commits if value["author"] in selected_authors
        }.items()

    commits = [
        {
            "hexsha": key,
            "parents": value["parents"],
            "branch": value["branch"],
            "branch_full": value["branch_full"],
            "message": value["message"],
            "should_check": value["should_check"],
            "confidence": value["confidence"],
            "diff_result": value["diff_result"],
        }
        for key, value in commits
    ][:num_commits]

    max_confidence = 0
    for commit in commits:
        if commit["confidence"] > max_confidence:
            max_confidence = commit["confidence"]

    return commits


def interpolate_color(value):
    global max_confidence
    max_value = max_confidence if max_confidence > 0 else 0.00000001
    red = (max_value - value) / max_value * 255
    green = value / max_value * 255
    rgb_color = (red, green, 0)
    hex_color = mcolors.rgb2hex([x / 255 for x in rgb_color])
    return hex_color


@app.callback(
    Output("commit-graph", "elements"),
    [
        Input("num-commits-input", "value"),
        Input("branch_and_tags_checklist", "value"),
        Input("authors_checklist", "value"),
        Input("commit-graph", "tapNodeData"),
        Input("show/hide_confidence-button", "n_clicks"),
        Input("find-button", "n_clicks"),
    ],
    priority=1,
)
def update_graph(
    num_commits: int,
    selected_branches: list,
    selected_authors: list,
    _,
    show_hide_confidence_n_clicks,
    find_button_n_clicks,
    *args,
    **kwargs,
) -> (list, list):
    time.sleep(0.1)

    global LOADED_COMMITS, max_confidence
    x_position = 0

    new_commits = commit_filtering(
        LOADED_COMMITS.copy().items(), selected_branches, selected_authors, num_commits
    )
    new_commit_hashes = {commit["hexsha"] for commit in new_commits.copy()}
    show_confidence = False if show_hide_confidence_n_clicks % 2 == 0 else True
    new_branch_positions = {"x8494156e1qw56ewq16e5q": "?"}
    for commit in new_commits:
        if (branch := commit["branch"]) not in new_branch_positions:
            new_branch_positions[branch] = {
                "position": x_position,
                # "color": generate_hex_color(),
                "color": branch_colors[branch],
                "count": 1,
                "last": 2,
            }
            x_position += 110
        else:
            new_branch_positions[branch]["count"] += 1

    branches = new_branch_positions.copy()

    if find_button_n_clicks % 2 != 0:
        finding_suitable_versions_to_compare(new_commits)

    new_nodes = create_nodes(new_commits, branches, new_branch_positions, show_confidence)
    new_edges = create_edges(new_commits, new_commit_hashes, branches)

    return new_nodes + new_edges


def create_nodes(new_commits, xd_branches, new_branch_positions, show_confidence):
    new_nodes = []
    brach_x_position = {}

    for i, commit in enumerate(new_commits):
        if "bgcolor" in commit:
            bg_color = commit["bgcolor"]
        elif show_confidence:
            bg_color = (
                interpolate_color(commit["confidence"]) if commit["confidence"] >= 0 else "#000000"
            )
        else:
            if selected_nodes:
                if commit["hexsha"] in selected_nodes:
                    bg_color = "#02C7DE"
                else:
                    bg_color = "#797979"
            else:
                bg_color = xd_branches.get(commit["branch"], {}).get("color", "#000000")

        if commit["branch"] not in brach_x_position:
            brach_x_position[commit["branch"]] = (
                list(new_branch_positions.keys()).index(commit["branch"]) * 110
            )

        x_position = brach_x_position[commit["branch"]]
        commit_message = commit["message"].replace("\n", " ")
        node = {
            "data": {
                "id": commit["hexsha"],
                "label": f"Commit hash: {commit['hexsha'][:6]} \n Branch name: {commit['branch']} \n Commit message: {commit_message}",
            },
            "position": {
                "x": x_position,
                "y": 120 * i,
            },
            "style": {"background-color": bg_color},
        }
        new_branch_positions[commit["branch"]]["count"] -= 1
        if new_branch_positions[commit["branch"]]["count"] <= 0:
            del new_branch_positions[commit["branch"]]

        new_nodes.append(node)

    return new_nodes


def create_edges(new_commits, new_commit_hashes, xd_branches):
    return [
        {
            "data": {"source": parent, "target": commit["hexsha"]},
            "style": {
                "events": "no",
                "line-color": (
                    "#797979"
                    if selected_nodes
                    else xd_branches.get(commit["branch"], {}).get("color", "#000000")
                ),
            },
        }
        for commit in new_commits
        for parent in commit["parents"]
        if parent in new_commit_hashes
    ]


def finding_suitable_versions_to_compare(new_commits):
    global max_confidence, repo_path
    git_repo = GitRepository(repo_path)
    skip = True

    for commit in new_commits:
        if commit["hexsha"] in selected_nodes:
            skip = False
            continue

        if skip:
            continue

        try:
            ds, confidence, diff_result = selection.should_check_versions(
                GitRepository(repo_path).get_minor_version_info(selected_nodes[0]),
                git_repo.get_minor_version_info(commit["hexsha"]),
            )
        except:
            print("CHIBYCKA")
            ds = False
            confidence = -1
            diff_result = None

        if confidence > max_confidence:
            max_confidence = confidence

        commit["compare_with_version"] = {
            "should_check": ds,
            "confidence": confidence,
            "diff_result": diff_result,
        }

    for commit in new_commits:
        if "compare_with_version" in commit:
            commit["bgcolor"] = (
                interpolate_color(commit["compare_with_version"]["confidence"])
                if commit["compare_with_version"]["confidence"] >= 0
                else "#000000"
            )


@app.callback(
    Output("find-button", "children"),
    [Input("find-button", "n_clicks")],
    [State("commit-graph", "tapNodeData")],
    priority=2,
)
def update_button_text(n_clicks, _):
    if n_clicks % 2 == 0:
        return "Click here to find a suitable versions to compare"
    else:
        return "Hide compared versions"


@app.callback(
    Output("show_statistics", "children"),
    Input("statistic-button", "n_clicks"),
)
def show_statistics(n_clicks):
    global selected_nodes, repo_path

    if n_clicks % 2 == 0:
        return []

    # if len(selected_nodes) != 2:
    #     return [html.P("Select two commits to compare")]
    git_repo = GitRepository(repo_path)
    data, confidence, diff_result = selection.should_check_versions(
        GitRepository(repo_path).get_minor_version_info(selected_nodes[0]),
        git_repo.get_minor_version_info(selected_nodes[1]),
    )

    for item in diff_result:
        count, true_count = 0, 0
        for rule_list in item["data"]:
            for rule in rule_list:
                if isinstance(rule, list):
                    for rul in rule:
                        count += 1
                        if rul["result"]:
                            true_count += 1
                else:
                    count += 1
                    if rule["result"]:
                        true_count += 1
        item["count"] = count
        item["true_count"] = true_count

    sorted_diff_result = sorted(diff_result, key=lambda x: x["true_count"], reverse=True)
    max_true_rules = max([item["true_count"] for item in sorted_diff_result])

    cards = [
        html.H3("Difference statistics:", style={"margin-bottom": "5px"}),
    ]
    cards.append(
        html.Strong(f"This versions should be checked!", style={"color": "green", "fontSize": 36})
        if data
        else html.Strong(f"Dont check this versions!", style={"color": "red", "fontSize": 36})
    )

    cards.extend(
        [
            html.Br(),
            html.Strong(f"Confidence:"),
            html.Div(f"{confidence}"),
            html.Strong(f"Files & rules:"),
        ]
    )

    for index, item in enumerate(sorted_diff_result):
        if item["true_count"] == 0:
            continue


        background_color = get_green_color(max_true_rules, item["true_count"])
        parser_rules = {}
        for rule_item in item["data"]:
            for rules in rule_item:
                if not isinstance(rules, list):
                    rules = [rules]

                for rule in rules:
                    indicator_name = rule.get("parser_name").replace("Parser", "Indicator")
                    parser_rules.setdefault(indicator_name, []).append(rule)

        rules_components = []
        for indicator_name, rules_list in parser_rules.items():
            rules_components.append(
                html.Details(
                    [
                        html.Summary(
                            [
                                html.Strong("Indicator: "),
                                f"{indicator_name}",
                            ], style={"background-color": background_color}
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(f"Rule: {item['rule']}"),
                                        html.Div(f"Variable: {item['key']}"),
                                        html.Div(f"Value: {item['value']}"),
                                    ],
                                    style={
                                        "border-bottom": "1px solid lightgray",
                                        "padding-left": "20px",
                                    },
                                )
                                for item in rules_list
                                if "True" in str(item)
                            ],
                            style={"max-height": "200px", "overflow-y": "auto", "background-color": background_color},
                        ),
                    ],
                    style={
                        "padding-left": "20px",
                    },
                )
            )

        card = html.Details(
            [
                html.Summary(
                    [
                        html.Strong("Path: "),
                        f"{item['path']}",
                        html.Br(),
                        html.Strong("True rules: "),
                        f"{item['true_count']}",
                    ]
                ),
                html.Div(
                    rules_components,
                    style={
                        "max-height": "200px",
                        "overflow-y": "auto",
                        "background-color": background_color,
                    },
                    className="details-container",
                ),
            ],
            style={"border": "1px solid lightgray", "padding": "10px", "background-color": background_color},
        )
        cards.append(card)
    return cards

def get_green_color(max_true_rules, true_count):
    color = 1 - true_count / max_true_rules * 0.5
    return mcolors.rgb2hex((color, 1, color))


@app.callback(
    Output("graph-legend", "children"),
    [Input("find-button", "n_clicks")],
    priority=-10,
)
def update_button_text(n_clicks, _):
    if n_clicks % 2 == 0:
        return ""
    else:
        return "Hide compared versions"


app.layout = html.Div(
    [
        cyto.Cytoscape(
            id="commit-graph",
            layout={
                "name": "preset",
                "viewport": {"zoom": 1, "pan": {"x": 0, "y": 0}},
                "boundingBox": {"x1": 0, "y1": 0, "x2": 100, "y2": 100},
            },
            style={
                "width": "35%",
                "height": "100vh",
                # "border": "1px solid black",
            },
            maxZoom=1.25,
            minZoom=0.1,
            stylesheet=[
                {
                    "selector": "node",
                    "style": {"label": "data(label)", "text-wrap": "wrap"},
                },
            ],
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Number of Commits to Display:", style={"margin-bottom": "5px"}),
                        dcc.Input(
                            id="num-commits-input",
                            type="number",
                            value=25,
                            style={
                                "width": "13%",
                                "border-style": "solid",
                                "border-color": "#000000",
                                "border-top-width": "0px",
                                "border-right-width": "0px",
                                "border-left-width": "0px",
                                "border-bottom-width": "5px",
                            },
                        ),
                        html.Div(id="output-container"),
                    ],
                    style={
                        "width": "100%",
                        "margin-bottom": "10px",
                        "border-bottom": "1px solid lightgray",
                    },
                ),
                html.Div(id="button-place"),
                html.H3("Branches & Tags", style={"margin-bottom": "5px"}),
                html.Div(
                    dcc.Checklist(
                        id="branch_and_tags_checklist",
                        options=branches_checkbox,
                        value=selected_options_state,
                    ),
                    style={
                        "max-height": "45vh",
                        "overflow-y": "auto",
                        "border-bottom": "1px solid lightgray",
                        "margin-left": "10px",
                    },
                ),
                html.Br(),
                html.H3("Authors", style={"margin-bottom": "5px"}),
                html.Div(
                    dcc.Checklist(
                        id="authors_checklist",
                        options=author_checkbox,
                        value=selected_authors_state,
                    ),
                    style={
                        "max-height": "45vh",
                        "overflow-y": "auto",
                        "border-bottom": "1px solid lightgray",
                        "margin-left": "10px",
                    },
                ),
                html.Br(),
                html.Div(
                    [
                        dbc.Button(
                            "Show/Hide confidence",
                            color="primary",
                            outline=True,
                            id="show/hide_confidence-button",
                            n_clicks=0,
                        ),
                    ],
                    style={"display": "block", "margin-bottom": "10px"},
                ),
                html.Div(
                    [
                        dbc.Button(
                            "To tu nemá být",
                            outline=True,
                            color="primary",
                            id="find-button",
                            n_clicks=0,
                        ),
                    ],
                    style={"display": "block", "margin-bottom": "10px"},
                ),
                html.Div(
                    [
                        dbc.Button(
                            "Show statistics",
                            color="primary",
                            outline=True,
                            id="statistic-button",
                            n_clicks=0,
                        ),
                    ],
                    style={"display": "block", "margin-bottom": "10px"},
                ),
                html.Div(id="graph-legend"),
            ],
            style={
                "width": "22%",
                "position": "relative",
                "overflow": "hidden",
                "display": "inline-block",
                "vertical-align": "top",
            },
        ),
        html.Div(
            [
                html.Div(
                    id="show_statistics",
                    style={
                        "max-height": "100vh",
                        "overflow-y": "auto",
                    },
                ),
                html.Div(id="placeholder-output"),
            ],
            style={
                "width": "43%",
                "position": "relative",
                "overflow": "hidden",
                "display": "inline-block",
                "vertical-align": "top",
            },
        ),
    ],
    style={
        "display": "flex",
        "flex-direction": "row",
        "width": "100%",
    },
)


def run_plotlydash(load_commits: int):
    global LOADED_COMMITS
    if not LOADED_COMMITS:
        LOADED_COMMITS = generate_commit_tree(load_commits)

    app.run_server(debug=True, dev_tools_ui=False, dev_tools_props_check=False)
