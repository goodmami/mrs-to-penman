
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

If you want to try different settings, edit `convert-redwoods.sh` and
use some of the commented-out options at the bottom of the file. See
below for a description of the options.

# Parsing and Converting New Data

## Additional Requirements

* [ACE](http://sweaglesw.org/linguistics/ace/)

  For Linux:

  ```bash
  wget http://sweaglesw.org/linguistics/ace/download/ace-0.9.24-x86-64.tar.gz -q -O - | tar xz
  ```

  For Mac:

  ```bash
  wget http://sweaglesw.org/linguistics/ace/download/ace-0.9.24-osx.tar.gz -q -O - | tar xz
  ```

  You can install this to a suitable location by, e.g., moving the
  `ace-0.9.24/` directory into `/opt/` and by adding
  `PATH=/opt/ace-0.9.24/:"$PATH"` to `.bashrc`. Alternatively, use the
  `--ace-binary` option to the `mrs_to_penman.py` command.

* [art](http://sweaglesw.org/linguistics/libtsdb/art) (recommended)

  Linux only:

  ```bash
  wget http://sweaglesw.org/linguistics/libtsdb/download/art-0.1.9-x86-64.tar.gz -q -O - | tar xf
  ```

* [ERG](http://moin.delph-in.net/ErgTop)

  For Linux:

  ```bash
  wget http://sweaglesw.org/linguistics/ace/download/erg-1214-x86-64-0.9.24.dat.bz2-q -O - | bunzip2 > erg-1214-0.9.24.dat
  ```

  For Mac:

  ```bash
  wget http://sweaglesw.org/linguistics/ace/download/erg-1214-osx-0.9.24.dat.bz2 -q -O - | bunzip2 > erg-1214-0.9.24.dat
  ```

## Parse and Convert

For sentence data (one sentence per line), you can either pipe sentences
in via stdin or direct `--input` to a file containing sentences. In
either case, a grammar file is required (e.g. the ERG).

```bash
cat sentences.txt | mrs_to_penman.py --grammar erg-1214-0.9.24.dat
```

or

```bash
mrs_to_penman.py --grammar erg-1214-0.9.24.dat --input sentences.txt
```

If you have a parsed full profile (e.g. using `art`), you can point
`--input` to the profile's directory. The `--grammar` option is not
required in this case.

```bash
art -a 'ace -g erg-1214-0.9.24.dat' path/to/profile/
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
(e.g.: `art -a 'ace -g erg-1214-0.9.24.dat -n1 --timeout 1' path/to/profile`).

# Options for `mrs_to_penman.py`

* `--grammar` - path to a grammar file compiled with ACE
* `--input` - path to sentence data; if a file, file is 1 sentence per
    line, and if a directory, directory is a profile; if not given, read
    stdin as though a file
* `-n` - maximum number of results per input (default: 1)
* `--properties` - include variable properties
* `--lnk` - include lnk (surface alignment) values (e.g. `:lnk "<0:5>"`
    means characters 0 to 5)
* `--udef-q` - include default quantifiers
* `--ace-binary` - path to the ACE binary (default: ace)
* `--timeout` - time to allow for parsing each item, in seconds
    (default: no limit)
