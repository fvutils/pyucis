
from ucis.rgy import FormatRgy
from ucis.rgy import FormatDescDb, FormatIfDb
from ucis.merge import DbMerger
from ucis.conversion import ConversionContext, ConversionListener


def convert(args):
    if args.input_format is None:
        args.input_format = "xml"
    if args.output_format is None:
        args.output_format = "xml"

    rgy = FormatRgy.inst()
    if not rgy.hasDatabaseFormat(args.input_format):
        raise Exception("Input format %s not recognized" % args.input_format)
    if not rgy.hasDatabaseFormat(args.output_format):
        raise Exception("Output format %s not recognized" % args.output_format)

    input_desc : FormatDescDb = rgy.getDatabaseDesc(args.input_format)
    output_desc : FormatDescDb = rgy.getDatabaseDesc(args.output_format)

    input_if = input_desc.fmt_if()
    output_if = output_desc.fmt_if()

    strict = getattr(args, 'strict', False)
    ctx = ConversionContext(
        strict=strict,
        listener=ConversionListener()
    )

    try:
        in_db = input_if.read(args.input)
    except Exception as e:
        raise Exception("Failed to read file %s ; %s" % (args.input, str(e)))

    # For SQLite output, use SqliteMerger to preserve history/test associations
    if args.output_format == "sqlite":
        from ucis.sqlite import SqliteUCIS
        from ucis.sqlite.sqlite_merge import SqliteMerger
        
        out_db = SqliteUCIS(args.out)
        merger = SqliteMerger(out_db)
        merger.merge(in_db, create_history=True, squash_history=False)
        out_db.close()
    else:
        # Generic merge for other formats
        out_db = output_if.create()
        merger = DbMerger()
        merger.merge(out_db, [in_db])
        try:
            output_if.write(out_db, args.out, ctx)
        except TypeError:
            # Older format interfaces may not accept ctx
            output_if.write(out_db, args.out)

    ctx.complete()

    if getattr(args, 'warn_summary', False) and ctx.warnings:
        import sys
        print(ctx.summarize(), file=sys.stderr)

    in_db.close()
