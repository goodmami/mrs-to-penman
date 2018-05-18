#!/usr/bin/env python3

import sys
import os
import re
import argparse
import json

from delphin.interfaces import ace
from delphin.mrs import xmrs, simplemrs, penman
from delphin.mrs.components import var_sort
from delphin import itsdb

Triple = penman.penman.Triple
codec = penman.XMRSCodec(indent=2)

def run(args):
    if (not args.input or os.path.isfile(args.input)) and not args.grammar:
        sys.exit('--grammar must be used when input is sentence data')
    if args.input:
        if os.path.isfile(args.input):
            with open(args.input, 'r') as fh:
                process(parse_input(fh, args), args)
        elif os.path.isdir(args.input):
            process(read_profile(args.input, args), args)
        else:
            sys.exit('--input argument is not a file or directory')
    else:
        process(parse_input(sys.stdin, args), args)


def process(items, args):
    for item_id, snt, mrss in items:
        print('# ::id {}\n# ::snt {}'.format(item_id, snt))
        for mrs in mrss[:args.n]:
            try:
                print(make_penman(mrs, args))
            except penman.penman.EncodeError as ex:
                print('Item {}\t{}'.format(item_id, str(ex)),
                      file=sys.stderr)
                print('()')

        print()


def parse_input(in_fh, args):
    cmdargs = ['-n', str(args.n)]
    if args.timeout is not None:
        cmdargs.extend(['--timeout', str(args.timeout)])

    with ace.AceParser(
            args.grammar,
            cmdargs=cmdargs,
            executable=args.ace_binary,
            tsdbinfo=False) as parser:
        for i, line in enumerate(in_fh):
            snt, mrss = line.rstrip('\n'), []
            if snt.strip():
                try:
                    response = parser.interact(line)
                    for result in response.results():
                        mrss.append(result.mrs())
                except Exception as ex:
                    print(
                        'An error occurred during parsing item #{}: {}\n'
                        'The error is: {}'
                        .format(i, snt, str(ex)),
                        file=sys.stderr
                    )
            yield (i, snt, mrss)


def read_profile(f, args):
    p = itsdb.ItsdbProfile(f)
    mrs_dataspec = args
    inputs = dict((r['i-id'], r['i-input']) for r in p.read_table('item'))
    cur_id, mrss = None, []

    if p.exists('p-result'):
        rows = p.read_table('p-result')
        id_spec = 'i-id'
        mrs_spec = 'mrs'
    else:
        rows = p.join('parse', 'result')
        id_spec = 'parse:i-id'
        mrs_spec = 'result:mrs'

    for row in rows:
        mrs = simplemrs.loads_one(row[mrs_spec])

        if cur_id is None:
            cur_id = row[id_spec]

        if cur_id == row[id_spec]:
            mrss.append(mrs)
        else:
            yield (cur_id, inputs[cur_id], mrss)
            cur_id, mrss = row[id_spec], [mrs]

    if mrss:
        yield (cur_id, inputs[cur_id], mrss)


def make_penman(x, args):
    g = make_graph(x, args)
    p = codec.encode(g)
    return p


def make_graph(x, args):
    if args.parameters:
        params = json.load(open(args.parameters))
    else:
        params = {}

    # first create a graph to get normalized triples
    g = codec.triples_to_graph(xmrs.Dmrs.to_triples(x, properties=True))

    # then filter if necessary
    if params:
        varsort = dict((ep.nodeid, var_sort(ep.intrinsic_variable))
                       for ep in x.eps())
        preds = dict((nid, x.pred(nid).short_form()) for nid in x.nodeids())
        drop = set(params.get('drop_nodes', []))
        allow = params.get('allow_relations', {})
        global_allow = set(allow.get('global', []))
        x_allow = set(allow.get('x', []))
        e_allow = set(allow.get('e', []))
        pred_allow = allow.get('predicate', {})
        ts = [
            t for t in g.triples()
            if (preds.get(t.source) not in drop and
                (t.relation in global_allow or
                 (varsort.get(t.source) == 'x' and t.relation in x_allow) or
                 (varsort.get(t.source) == 'e' and t.relation in e_allow) or
                 (t.relation in pred_allow.get(preds.get(t.source), []))))
        ]
        top = g.top if g.top in [t.source for t in ts] else None
        g = codec.triples_to_graph(ts, top=top)
        if params.get('substitute_attribute_value', {}):
            g = _substitute_attrval(
                g,
                params['substitute_attribute_value'],
                params['default_attribute_value']
            )

    return g

def _substitute_attrval(g, subs, default_value):
    attrs = set(g.attributes())
    ts = []
    for t in g.triples():
        if t not in attrs or t.relation not in subs:
            ts.append(t)
        else:
            val = str(t.target)
            for match, sub in subs[t.relation]:
                val = re.sub(match, sub, val)
            if not val:
                val = default_value
            ts.append(Triple(t.source, t.relation, val, t.inverted))
    return codec.triples_to_graph(ts, top=g.top)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-g', '--grammar', help='path to a grammar file compiled with ACE')
    argparser.add_argument('-i', '--input', help='path to sentence data; if a file, file is 1 sentence per line, and if a directory, directory is a profile; if not given, read stdin as though a file')
    argparser.add_argument('-n', type=int, default=1, help='maximum number of results per input (default: 1)')
    argparser.add_argument('-p', '--parameters', help="JSON file of conversion parameters")
    argparser.add_argument('--ace-binary', default='ace', help='path to the ACE binary (default: ace)')
    argparser.add_argument('--timeout', type=int, help='time to allow for parsing each item (default: None)')
    args = argparser.parse_args()

    run(args)


if __name__ == '__main__':
    main()

