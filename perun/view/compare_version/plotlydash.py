import os
import random
import time

import dash
import dash_cytoscape as cyto
import git
import matplotlib.colors as mcolors
from dash import html, dcc
from dash.dependencies import Input, Output, State

from perun.select.better_repository_selection import BetterRepositorySelection
from perun.vcs.git_repository import GitRepository

app = dash.Dash()
# repo_path = "/home/lukas/PycharmProjects/You-are-Pythonista"
repo_path = os.getcwd()
# repo_path = "/home/luke/PycharmProjects/You-are-Pythonista"
# repo_path = "/home/luke/PycharmProjects/perun"
# repo_path = "C:\\Users\\lukas\\PycharmProjects\\perun"
# repo_path = "C:\\Users\\lukas\\PycharmProjects\\syncagent-server"
# repo_path = "/home/luke/PycharmProjects/syncagent-server"
repo = git.Repo(repo_path)
repo_commits = list(repo.iter_commits())
x_position, node_count = 0, 0
branches_checkbox, author_checkbox = [], []
repo_tags = {tag.commit.hexsha: tag.name for tag in repo.tags}
newest_tag = ""
selected_nodes = []
selected_options_state = []
selected_authors_state = []
LOADED_COMMITS = {}
branches_trans = {}
branches_commits = {}
visible_commits = []
selection = BetterRepositorySelection(repo_path)
max_confidence = 0


def generate_commit_tree(max_commits: int) -> dict:
    global newest_tag, max_confidence
    newest_tag = ""
    return_data = {}

    for commit in repo_commits[: max_commits if max_commits > 0 else 99999999]:

        branch_name = repo.git.name_rev(commit.hexsha, name_only=True)
        branch_name_full = branch_name

        if "Merge pull request" in commit.message:
            branch_name_tmp = commit.message.split("\n")[0].rsplit(" ", 1)[1]
            znak_count = branch_name.count("^")
            for xd_commit in commit.parents:
                if znak_count < repo.git.name_rev(xd_commit.hexsha, name_only=True).count("^"):
                    branches_commits[xd_commit.hexsha] = branch_name_tmp

        if "tags" in branch_name:
            branch_name = branch_name.split("^", 1)[0].split("~", 1)[0]
        else:
            if branch_name.rfind("~", 1) > branch_name.rfind("^", 1):
                parts = branch_name.rsplit("~", 1)
                branch_name = parts[0]
            else:
                branch_name = branch_name

        if commit.hexsha in branches_commits:
            branches_trans[branch_name] = branches_commits[commit.hexsha]

        if branch_name in branches_trans:
            branch_name = branches_trans[branch_name]

        if branch_name not in [item["label"] for item in branches_checkbox]:
            branches_checkbox.append({"label": branch_name, "value": branch_name})

        if commit.author.email not in author_checkbox:
            author_checkbox.append(commit.author.email)
        try:
            ds, confidence, diff_result = selection.should_check_version(
                GitRepository(repo_path).get_minor_version_info(commit.hexsha)
            )
            print(ds, confidence)
        except:
            print("nende to")
            continue
        if confidence > max_confidence:
            max_confidence = confidence
        return_data[commit.hexsha] = {
            "parents": [parent.hexsha for parent in commit.parents if parent.hexsha],
            "branch": branch_name,
            "author": commit.author.email,
            "branch_full": branch_name_full,
            "message": commit.message,
            "should_check": ds,
            "confidence": confidence,
        }

    return return_data


def generate_hex_color():
    r = random.randint(50, 215)
    g = random.randint(50, 215)
    b = random.randint(50, 215)
    hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
    return hex_color

@app.callback(
    Output("commit-graph", "elements", allow_duplicate=True),
    [
        Input("num-commits-input", "value"),
        Input("branch_and_tags_checklist", "value"),
        Input("authors_checklist", "value"),
        Input("commit-graph", "tapNodeData"),
        Input("show/hide_confidence-button", "n_clicks"),
    ],
    prevent_initial_call=True,
    priority=99,
)
def delete_graph(*args, **kwargs):
    return []


@app.callback(
    [
        Output("selected-commit-container", "children"),
        Output("button-place", "children"),
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

    if len(selected_nodes) == 1:
        return (
            html.Div(f"Selected commit hash: {selected_nodes}"),
            html.Button("Click here to find a suitable version to compare", id="find-button"),
        )
    if len(selected_nodes) == 2:
        return (
            html.Div(f"Selected commit hash: {selected_nodes}"),
            html.Button("Click here to compare selected versions", id="compare-button"),
        )
    else:
        return html.Div(f"Selected commit hash: {selected_nodes}"), ""


def commit_filtering(commits, selected_branches, selected_authors, num_commits):
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
                  }
                  for key, value in commits
              ][:num_commits]

    return commits


def interpolate_color(value):
    global max_confidence
    max_value = max_confidence
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
    ],
    priority=1,
)
def update_graph(
        num_commits: int,
        selected_branches: list,
        selected_authors: list,
        _,
        show_hide_confidence_n_clicks,
        *args,
        **kwargs,
) -> (list, list):
    time.sleep(0.1)

    global x_position, node_count, LOADED_COMMITS, visible_commits
    x_position, node_count = 0, 0
    loaded_commits = LOADED_COMMITS.copy().items()

    new_commits = commit_filtering(loaded_commits, selected_branches, selected_authors, num_commits)
    new_commit_hashes = {commit["hexsha"] for commit in new_commits.copy()}
    show_confidence = False if show_hide_confidence_n_clicks % 2 == 0 else True
    new_branch_positions = {"x8494156e1qw56ewq16e5q": "?"}
    for commit in new_commits:
        if (branch := commit["branch"]) not in new_branch_positions:
            new_branch_positions[branch] = {
                "position": x_position,
                "color": generate_hex_color(),
                "count": 1,
                "last": 2,
            }
            x_position += 110
        else:
            new_branch_positions[branch]["count"] += 1

    xd_branches = new_branch_positions.copy()

    new_nodes = []
    brach_x_position = {}
    for i, commit in enumerate(new_commits):
        if show_confidence:
            bg_color = interpolate_color(commit["confidence"])
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
                # "x": list(new_branch_positions.keys()).index(commit["branch"]) * 110,
                "x": x_position,
                "y": 120 * i,
            },
            "style": {"background-color": bg_color},
        }
        new_branch_positions[commit["branch"]]["count"] -= 1
        if new_branch_positions[commit["branch"]]["count"] <= 0:
            del new_branch_positions[commit["branch"]]

        new_nodes.append(node)

    new_edges = [
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
    visible_commits = [commit["hexsha"] for commit in new_commits]
    return new_nodes + new_edges


@app.callback(
    Output("find-button", "children"),
    [Input("find-button", "n_clicks")],
    [State("commit-graph", "tapNodeData")],
)
def update_button_text(n_clicks, tapNodeData):
    if not n_clicks:
        return "Click here to find a suitable version to compare"

    # TODO - do something with the selected nodes
    return f"Find another suitable version {n_clicks}"


def show_and_hide_if_commits_should_be_checked():
    pass


app.layout = html.Div(
    [
        html.Div(
            [
                html.Label("Number of Commits to Display:"),
                dcc.Input(id="num-commits-input", type="number", value=25),
                html.Div(id="output-container"),
            ],
            style={"width": "100%", "margin-bottom": "10px"},
        ),
        html.Div(
            [
                cyto.Cytoscape(
                    id="commit-graph",
                    layout={
                        "name": "preset",
                        "viewport": {"zoom": 1, "pan": {"x": 0, "y": 0}},
                        "boundingBox": {"x1": 0, "y1": 0, "x2": 100, "y2": 100},
                    },
                    style={
                        "width": "100%",
                        "height": "400px",
                        "border": "1px solid black",
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
            ],
            style={
                "width": "32%",
                "position": "relative",
                "overflow": "hidden",
                "display": "inline-block",
                "vertical-align": "top",
            },
        ),
        html.Div(
            [
                html.Div(id="button-place"),
                html.Label("Branches & tags"),
                dcc.Checklist(
                    id="branch_and_tags_checklist",
                    options=branches_checkbox,
                    value=selected_options_state,
                ),
                html.Label("Authors"),
                dcc.Checklist(
                    id="authors_checklist",
                    options=author_checkbox,
                    value=selected_authors_state,
                ),
                html.Button("Show/Hide confidence", id="show/hide_confidence-button", n_clicks=0),
            ],
            style={
                "width": "25%",
                "position": "relative",
                "overflow": "hidden",
                "display": "inline-block",
                "vertical-align": "top",
            },
        ),
        html.Div(
            id="selected-commit-container",
            style={
                "position": "absolute",
                "top": "10px",
                "left": "30%",
                "font-size": "24px",
            },
        ),
        html.Div(
            [
                html.Div(id="image-column1"),
                html.Div(id="image-column2"),
            ],
            style={"display": "flex"},
        ),
    ]
)


def run_plotlydash():
    global LOADED_COMMITS
    if not LOADED_COMMITS:
        # generating takes about 3sec for 100 commits
        LOADED_COMMITS = generate_commit_tree(50)
    app.run_server(debug=True)
