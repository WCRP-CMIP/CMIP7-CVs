import esgvoc.api as ev
from attrs import define
from rich import print
from rich.tree import Tree


@define
class Node:
    drs_name: str
    children: list["Node"]
    is_root: bool


def add_branch(node: Node, parent_tree: Tree) -> Tree:
    node_tree = parent_tree.add(node.drs_name)
    for node in node.children:
        add_branch(node, parent_tree=node_tree)

    return parent_tree


def main():
    experiments = ev.get_all_terms_in_collection("cmip7", "experiment")
    experiment_d = {}
    for experiment in experiments:
        if experiment.id not in experiment_d:
            experiment_d[experiment.id] = Node(
                experiment.drs_name,
                [],
                is_root=False,
            )

        experiment_d[experiment.id].is_root = (
            True if not experiment.parent_experiment else False
        )

        if experiment.parent_experiment:
            if experiment.parent_experiment.id not in experiment_d:
                experiment_d[experiment.parent_experiment.id] = Node(
                    experiment.parent_experiment.drs_name, [], False
                )

            experiment_d[experiment.parent_experiment.id].children.append(
                experiment_d[experiment.id]
            )

    res = Tree("CMIP7 experiments")
    for node in (v for v in experiment_d.values() if v.is_root):
        res = add_branch(node, parent_tree=res)

    print(res)


if __name__ == "__main__":
    main()
