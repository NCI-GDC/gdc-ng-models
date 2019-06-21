from argparse import ArgumentParser


def get_parser():

    parser = ArgumentParser()

    parser.add_argument(
        '-m',
        '--module',
        type=str,
        help='The non-graph modules to be created',
        required=True,
    )

    parser.add_argument(
        '-host',
        '--host',
        type=str,
        help='The database host',
        required=False,
    )

    parser.add_argument(
        '-d',
        '--database',
        type=str,
        help='The name of the database',
        required=False,
    )

    parser.add_argument(
        '-u',
        '--admin_user',
        type=str,
        required=False,
    )

    parser.add_argument(
        '-p',
        '--admin_password',
        type=str,
        required=False,
    )

    return parser
