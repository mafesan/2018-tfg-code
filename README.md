# Tool for massively extract and analyze GitHub artifacts

The set of scripts which compounds this tool can be classified into 4 different sections:

## Preliminary phase

### get-project-list.py

```
usage: get-project-list.py [-h] --input-file INPUT_FILE --output-file
                           OUTPUT_FILE [--log-file LOG_FILE] [-g]

Adapt projects.csv file from GHTorrent dump with preliminary filter(s)

optional arguments:
  -h, --help            show this help message and exit
  --input-file INPUT_FILE
                        Input projects CSV file
  --output-file OUTPUT_FILE
                        Output projects CSV file
  --log-file LOG_FILE   Path to log file
  -g, --debug           Enables debug mode
```

## Data extraction

### github-api.py
```
usage: github-api.py [-h] --github-token GITHUB_TOKEN --projects-file
                     PROJECTS_FILE [--log-file LOG_FILE] [-g]

Extracts git trees (list of files) from GitHub repositories

optional arguments:
  -h, --help            show this help message and exit
  --github-token GITHUB_TOKEN
                        GitHub token
  --projects-file PROJECTS_FILE
                        Projects file
  --log-file LOG_FILE   Path to log file
  -g, --debug           Enables debug mode
 ```

## Data filtering

### github-tree.py

```
usage: github-tree.py [-h] --heuristics-file HEURISTICS_FILE --trees-path
                      TREES_PATH [--log-file LOG_FILE] [-g]

Look for patterns and heuristics into Git-trees and return a list of positive
results

optional arguments:
  -h, --help            show this help message and exit
  --heuristics-file HEURISTICS_FILE
                          File with patterns and other heuristics
  --trees-path TREES_PATH
                          Path to folder containing trees information
  --log-file LOG_FILE   Log file
  --output-file OUT_FILE
                          Path to output hits file
  -g, --debug           Enables debug mode
```

### hits2urls.py

```
usage: hits2urls.py [-h] --json-path JSON_PATH --projects-file PROJECTS_FILE
                    --hits-file HITS_FILE [--output-file OUTPUT_FILE]
                    [--log-file LOG_FILE] [-g]

Converts positive results into URLs pointing to its raw files in GitHub

optional arguments:
  -h, --help            show this help message and exit
  --json-path JSON_PATH
                        Path where github-api JSONS are stored
  --projects-file PROJECTS_FILE
                        Projects file which was used with github-api
  --hits-file HITS_FILE
                        Path to the output file of github-tree
  --output-file OUTPUT_FILE
                        Path to store the URLs output file
  --log-file LOG_FILE   Path to log file
  -g, --debug           Enables debug mode
```

## Data analysis

### perceval-handler.py

```
usage: perceval-handler.py [-h] --github-token GITHUB_TOKEN --urls-file
                           URLS_FILE --output-path OUTPUT_PATH --perceval-path
                           PERCEVAL_PATH [--log-file LOG_FILE] [-c] [-g]

Calls GrimoireLab-Perceval to extract git information from the output file of
hits2urls.py script

optional arguments:
  -h, --help            show this help message and exit
  --github-token GITHUB_TOKEN
                        GitHub token
  --urls-file URLS_FILE
                        Path to URLs file (output from hits2urls.py)
  --output-path OUTPUT_PATH
                        Path where Perceval JSONs will be saved into
  --perceval-path PERCEVAL_PATH
                        Path where Perceval store its cache information
  --log-file LOG_FILE   Path to log file
  -c, --keep-cache      Keep Perceval cache
  -g, --debug           Enables debug mode

```

### projects2sql.py

```
usage: projects2sql.py [-h] --db-name DB_NAME --json-path JSON_PATH
                       --urls-file INPUT_FILE [--output-path OUTPUT_PATH]
                       [--log-file LOG_FILE] [--avoid-fw] [-g]

Generate SQL files extrating data from Perceval JSON files

optional arguments:
  -h, --help            show this help message and exit
  --db-name DB_NAME     Database name
  --json-path JSON_PATH
                        Path where Perceval JSONs are stored into
  --urls-file INPUT_FILE
                        Path to input URLs file produced with hits2urls script
  --output-path OUTPUT_PATH
                        Path where SQL files are stored into
  --log-file LOG_FILE   Path to log file
  --avoid-fw            Avoid `Framework`-type projects
  -g, --debug           Enables debug mode
```

### ghtorrent-users2sql.py

```
usage: ghtorrent-users2sql.py [-h] --input-file INPUT_FILE --db-name DB_NAME
                              [--output-path OUT_PATH] [--log-file LOG_FILE]
                              [-g]

Converts the USERS table from GHTorrent (csv) into a SQL script

optional arguments:
  -h, --help            show this help message and exit
  --input-file INPUT_FILE
                        CSV file of USERS table from GHTorrent
  --db-name DB_NAME     Database name
  --output-path OUT_PATH
                        Path where users.sql script will be stored
  --log-file LOG_FILE   Path to log file
  -g, --debug           Enables debug mode
```

### db_structure.sql

SQL script to create the structure of the MySQL database where the SQL data have to be imported. It is necessary to edit this file in order to set up the database name to match with the parameter `--db-name` from last scripts (By default, it is set to `my_database`).

---

# Dependencies

Note: `pip3` package is needed
```
pip3 install -r requirements.txt
```
