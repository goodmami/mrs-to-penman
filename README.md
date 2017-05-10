
# Converting the Redwoods Treebank

## Requirements

You'll need some software and data to run the `convert-redwoods.sh`
and/or `mrs_to_penman.py` commands.

* [PyDelphin](https://github.com/delph-in/pydelphin)

  ```bash
  pip3 install pydelphin
  ```

* [Redwoods Treebank](http://moin.delph-in.net/RedwoodsTop)

  ```bash
  svn co http://svn.delph-in.net/erg/trunk/tsdb/gold profiles
  ```

## Convert the data

```bash
./convert-redwoods.sh
```

If you want to try different settings, edit `parameters.json` and add or
remove constraints. See below for a description of the constraints.

# Parsing and Converting New Data

## Additional Requirements

* [ACE](http://sweaglesw.org/linguistics/ace/)

  For Linux:

  ```bash
  wget http://sweaglesw.org/linguistics/ace/download/ace-0.9.25-x86-64.tar.gz -q -O - | tar xz
  ```

  For Mac:

  ```bash
  wget http://sweaglesw.org/linguistics/ace/download/ace-0.9.25-osx.tar.gz -q -O - | tar xz
  ```

  You can install this to a suitable location by, e.g., moving the
  `ace-0.9.25/` directory into `/opt/` and by adding
  `PATH=/opt/ace-0.9.25/:"$PATH"` to `.bashrc`. Alternatively, use the
  `--ace-binary` option to the `mrs_to_penman.py` command.

* [art](http://sweaglesw.org/linguistics/libtsdb/art) (recommended)

  Linux only:

  ```bash
  wget http://sweaglesw.org/linguistics/libtsdb/download/art-0.1.9-x86-64.tar.gz -q -O - | tar xf
  ```

* [ERG](http://moin.delph-in.net/ErgTop)

  For Linux:

  ```bash
  wget http://sweaglesw.org/linguistics/ace/download/erg-1214-x86-64-0.9.25.dat.bz2-q -O - | bunzip2 > erg-1214-0.9.25.dat
  ```

  For Mac:

  ```bash
  wget http://sweaglesw.org/linguistics/ace/download/erg-1214-osx-0.9.25.dat.bz2 -q -O - | bunzip2 > erg-1214-0.9.25.dat
  ```

## Parse and Convert

For sentence data (one sentence per line), you can either pipe sentences
in via stdin or direct `--input` to a file containing sentences. In
either case, a grammar file is required (e.g. the ERG).

```bash
cat sentences.txt | mrs_to_penman.py --grammar erg-1214-0.9.25.dat
```

or

```bash
mrs_to_penman.py --grammar erg-1214-0.9.25.dat --input sentences.txt
```

If you have a parsed full profile (e.g. using `art`), you can point
`--input` to the profile's directory. The `--grammar` option is not
required in this case.

```bash
art -a 'ace -g erg-1214-0.9.25.dat' path/to/profile/
[..]
mrs_to_penman.py --input path/to/profile
```

Parsing with `art` then converting a whole profile will be faster than
parsing and converting sentence data, and probably more robust, too.

If the data includes very long or complicated sentences, processing can
take some time. Use `-n1` (the default) to only unpack the top result
per input and `--timeout=1` to limit processing to 1 second (if it takes
longer, no results will be returned for that sentence). These options
can be specified on `mrs_to_penman.py` or in the `-a` value of `art`
(e.g.: `art -a 'ace -g erg-1214-0.9.25.dat -n1 --timeout 1' path/to/profile`).

# Options for `mrs_to_penman.py`

* `--grammar` - path to a grammar file compiled with ACE
* `--input` - path to sentence data; if a file, file is 1 sentence per
    line, and if a directory, directory is a profile; if not given, read
    stdin as though a file
* `-n` - maximum number of results per input (default: 1)
* `--parameters` - path to a JSON file for conversion parameters
* `--ace-binary` - path to the ACE binary (default: ace)
* `--timeout` - time to allow for parsing each item, in seconds
    (default: no limit)

# Conversion Parameters

The `--parameters` option takes a path to a JSON file with information
used to customize the PENMAN graphs written by the tool. There are two
main ways of doing this: (1) allowing (whitelisting) relations, and (2)
dropping (blacklisting) entire nodes. If no parameters file is given,
then all possible information is encoded in the graphs.

```json
{
  "allow_relations": { ... },
  "drop_nodes": [ ... ]
}
```

Allowing relations has four subcategories: (a) global allow, (b) allow
for individuals ("x"; nouny things), (c) allow for eventualities ("e";
verby things), and (d) allow for specific node types. For (a)--(c), the
value is a simple list of relations that are allowed for that category.
For (d), the value is a mapping of node types to lists of relations.

```json
{
  "allow_relations": {
    "global": [
      "ARG1-NEQ", "ARG1-EQ", ...
    ],
    "x": [
      "NUM", ...
    ],
    "e": [
      "TENSE", ...
    ],
    "predicate": {
      "pron": [
        "PERS", "NUM", "GEND", ...
      ],
      ...
    }
    }
  }
}
```

Dropping nodes takes a simple list of node types. Any triple with a
source or target anchored in a node of that type is dropped.

```json
{
  "drop_nodes": [
    "udef_q",
    "pronoun_q"
  ]
}
```

It's possible that some parameter values could result in a graph that is
disconnected. In these cases, the graph will not be serialized (and
you should see an error message). Note that it's also possible to have a
disconnected graph originally.
