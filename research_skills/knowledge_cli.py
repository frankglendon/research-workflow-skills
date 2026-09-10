"""Local knowledge commands; the host selects and applies retrieved references."""
from . import knowledge

COMMANDS = {'kb-build', 'kb-search', 'kb-context', 'kb-status'}


def register(commands):
    for name in sorted(COMMANDS):
        parser = commands.add_parser(name)
        parser.add_argument('--index', default='.research-kb/index.sqlite3')
        if name == 'kb-build':
            parser.add_argument('--catalog', required=True)
        if name in {'kb-search', 'kb-context'}:
            parser.add_argument('--query', required=True)
            parser.add_argument('--audience', choices=['local', 'external'], default='local')
            parser.add_argument('--limit', type=int, default=6)
        if name == 'kb-search':
            parser.add_argument('--kind', choices=sorted(knowledge.KINDS))
            parser.add_argument('--stage')
            parser.add_argument('--page-type')
        if name == 'kb-context':
            parser.add_argument('--max-chars', type=int, default=12000)


def dispatch(args):
    if args.command == 'kb-build':
        return knowledge.build(args.catalog, args.index)
    if args.command == 'kb-status':
        return knowledge.status(args.index)
    options = {'audience': args.audience, 'limit': args.limit}
    if args.command == 'kb-context':
        return knowledge.context(args.index, args.query, max_chars=args.max_chars, **options)
    return knowledge.search(args.index, args.query, kind=args.kind,
                            stage=args.stage, page_type=args.page_type, **options)
