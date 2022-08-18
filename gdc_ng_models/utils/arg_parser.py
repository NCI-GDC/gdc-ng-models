from argparse import ArgumentParser


def get_parser():

    parser = ArgumentParser()

    parser.add_argument(
        "-m",
        "--module",
        type=str,
        help="The non-graph modules to be created",
        required=True,
    )

    parser.add_argument(
        "-H",
        "--host",
        type=str,
        help="The database host",
        required=False,
    )

    parser.add_argument(
        "-d",
        "--database",
        type=str,
        help="The name of the database",
        required=False,
    )

    parser.add_argument(
        "-u",
        "--admin_user",
        type=str,
        required=False,
    )

    parser.add_argument(
        "-p",
        "--admin_password",
        type=str,
        required=False,
    )

    sub_parser = parser.add_subparsers()

    create_parser = sub_parser.add_parser("create", help="Create tables")
    create_parser.set_defaults(action="create")

    grant_parser = sub_parser.add_parser(
        "grant", help="Grants privileges in module tables"
    )

    grant_parser.add_argument(
        "-r",
        "--role",
        type=str,
        required=True,
        help="User role to grant permissions to",
    )

    grant_parser.add_argument(
        "-P",
        "--permission",
        required=True,
        choices=["read", "write"],
        help="Permission to grand to user",
    )
    grant_parser.set_defaults(action="grant")

    revoke_parser = sub_parser.add_parser(
        "revoke", help="Revokes privileges in module tables"
    )

    revoke_parser.add_argument(
        "-r",
        "--role",
        type=str,
        required=True,
        help="User role to grant permissions to",
    )

    revoke_parser.add_argument(
        "-P",
        "--permission",
        required=True,
        choices=["read", "write"],
        help="User permission to revoke",
    )
    revoke_parser.set_defaults(action="revoke")
    return parser
